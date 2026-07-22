from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import time
from google.api_core.exceptions import BadRequest, NotFound
import config
from repositories.execution_repository import ExecutionRepository
from repositories.remediation_repository import RemediationRepository
from repositories.run_status_repository import RunStatusRepository
from services.adapter import AdapterService
from services.cloud_task_service import CloudTaskService
from utils.exceptions import format_gcp_exception
from utils.logger import logger
from services.ownership import OwnershipService
from services.capability import CapabilityService
from services.tag_service import TagService

class ExecutorService:
    def __init__(self):
        self.adapters = AdapterService()
        self.repository = RemediationRepository()
        self.execution_repository = ExecutionRepository()
        self.run_status = RunStatusRepository()
        self.cloud_tasks = CloudTaskService()
        self.ownership = OwnershipService()
        self.capability = CapabilityService()
        self.tag_service = TagService()

    def execute(self, actions):
        results = []
        with ThreadPoolExecutor(max_workers=config.MAX_PARALLEL_WORKERS) as executor:
            future_to_action = {executor.submit(self._execute_single_action, action): action for action in actions}
            for future in as_completed(future_to_action):
                results.append(future.result())
        return results

    def execute_resource(self, resource, labels: dict, tags: dict):
        """
        Executes a single resource action for greenfield flows.
        """
        # We reuse the same logic as execute() but for a single resource
        return self.execute(
            [
                {
                    "resource": resource.name,
                    "asset_type": resource.asset_type,
                    "labels": labels,
                    "tags": tags,
                }
            ]
        )[0]

    def _execute_single_action(self, action):
        client = self.adapters.client_for(action["asset_type"])
        if client is None:
            return {"resource": action["resource"], "status": "unsupported"}
        
        logger.info("Applying remediation to %s using %s", action["resource"], client.__class__.__name__)
        
        try:
            resource = client.get(action["resource"])
            
            # --- NULL CHECK ---
            if resource is None:
                logger.info("Resource %s is tag-only or unsupported for labels. Bypassing.", action["resource"])
                return {"resource": action["resource"], "status": "bypassed"}
            # ---------------------------

            if self.capability.supports_labels(action["asset_type"]):
                final_labels = self.ownership.build(
                    existing=resource.labels,
                    desired=action["labels"],
                    allowed=list(action["labels"].keys())
                )
                
                # =========================================================
                # GLOBAL DRY RUN INTERCEPTOR
                # =========================================================
                if config.DRY_RUN:
                    logger.info("[DRY RUN] Would patch %s with labels: %s", action["resource"], final_labels)
                else:
                    client.apply_labels(resource, final_labels)
                # =========================================================
                
            elif self.capability.supports_tags(action["asset_type"]):
                # --- TAGS TEMPORARILY DISABLED ---
                logger.info("Resource %s is Tag-only. Tags are currently disabled by configuration. Bypassing.", action["resource"])
                return {"resource": action["resource"], "status": "bypassed"}
                # ---------------------------------
            
            logger.info("Successfully updated %s", action["resource"])
            return {"resource": action["resource"], "status": "updated"}
            
        except NotFound:
            # CLEANLY CATCH 404s FOR DELETED RESOURCES
            logger.warning("Resource %s not found (likely deleted). Bypassing.", action["resource"])
            return {"resource": action["resource"], "status": "bypassed"}
            
        except Exception as error:
            logger.exception("Failed updating %s", action["resource"])
            return {"resource": action["resource"], "status": "failed", "error": format_gcp_exception(error)}

    def execute_batch(self, run_id: str, offset: int, batch_size: int):
        plans = self.repository.get_planned_batch(run_id=run_id, offset=offset, batch_size=batch_size)
        if not plans:
            return {"processed": 0, "successful": 0, "failed": 0}
        actions = [{"resource": p.resource_name, "asset_type": p.asset_type, "labels": p.planned_labels, "tags": p.planned_tags} for p in plans]
        results = self.execute(actions)
        plans_by_resource = {p.resource_name: p for p in plans}
        successful = 0
        failed = 0
        for result in results:
            plan = plans_by_resource[result["resource"]]
            status = "SUCCESS" if result["status"] in ["updated", "bypassed", "unsupported"] else "FAILED"
            if status == "SUCCESS": successful += 1
            else: failed += 1
            self.execution_repository.save(run_id=run_id, project_id=plan.project_id, asset_type=plan.asset_type, resource_name=plan.resource_name, status=status, execution_mode="BROWNFIELD", error_message=result.get("error"))
            for attempt in range(12):
                try:
                    if status == "SUCCESS": self.repository.mark_success(run_id, plan.resource_name)
                    else: self.repository.mark_failed(run_id, plan.resource_name)
                    break
                except BadRequest as e:
                    if "streaming buffer" not in str(e): raise
                    time.sleep(10)
        if self.execution_repository.is_completed(run_id):
            counts = self.repository.count_by_status(run_id)
            self.run_status.complete(run_id=run_id, successful=counts.get("SUCCESS", 0), failed=counts.get("FAILED", 0))
        return {"processed": len(plans), "successful": successful, "failed": failed}

    def execute_run(self, run_id: str, planned_actions_count: int):
        if self.execution_repository.already_executed(run_id): raise RuntimeError(f"Run {run_id} already executed.")
        if planned_actions_count == 0: return {"run_id": run_id, "status": "COMPLETED", "resources": 0}
        total_batches = math.ceil(planned_actions_count / config.REMEDIATION_BATCH_SIZE)
        for batch_number in range(total_batches):
            self.cloud_tasks.enqueue_remediation_batch(run_id=run_id, batch_number=batch_number + 1, total_batches=total_batches, offset=(batch_number * config.REMEDIATION_BATCH_SIZE), batch_size=config.REMEDIATION_BATCH_SIZE)
        return {"run_id": run_id, "status": "QUEUED", "resources": planned_actions_count, "batches": total_batches}
