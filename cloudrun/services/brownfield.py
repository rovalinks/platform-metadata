from services.discovery import DiscoveryService
from services.compliance import ComplianceService
from services.planner import PlannerService
from services.executor import ExecutorService
from utils.logger import logger
import config
import uuid

class BrownfieldService:
    def __init__(self):
        self.discovery = DiscoveryService()
        self.compliance = ComplianceService()
        self.planner = PlannerService()
        self.executor = ExecutorService()

    def execute(self, project_ids: list):
        run_id = str(uuid.uuid4())
        logger.info("========== BROWNFIELD ORG/MULTI-PROJECT START ==========")
        logger.info("Governance Run ID: %s", run_id)
        logger.info("Target Projects: %d", len(project_ids))

        all_resources = []
        all_compliance = []

        # Loop through all projects to gather reality
        for project_id in project_ids:
            logger.info("Processing Project: %s", project_id)
            
            # Step 1: Discover
            resources = self.discovery.discover(project_id, run_id)
            all_resources.extend(resources)
            
            # Step 2: Evaluate
            compliance = self.compliance.evaluate(resources, run_id=run_id, force_refresh=True)
            all_compliance.extend(compliance)

        total_discovered = len(all_resources)
        total_evaluated = len(all_compliance)

        logger.info("Discovery complete. %d resources found across %d projects.", total_discovered, len(project_ids))

        # Step 3: Plan (Everything under one run_id)
        logger.info("Step 3/4 - Generating remediation plan")
        plan = self.planner.create(all_compliance, run_id)

        if plan["planned_actions"] == 0:
            logger.info("No remediation required. All resources are compliant.\n========== BROWNFIELD COMPLETE ==========")
            return {
                "projects_scanned": len(project_ids),
                "discovered": total_discovered,
                "evaluated": total_evaluated,
                "planned": 0,
                "queued": 0,
                "batches": 0,
                "run_id": run_id,
                "status": "COMPLIANT",
            }

        # Step 4: Execute (Cloud Tasks handles the massive batch perfectly)
        logger.info("Step 4/4 - Executing remediation for %d resources", plan["planned_actions"])
        execution = self.executor.execute_run(
            run_id=plan["run_id"],
            planned_actions_count=plan["planned_actions"],
        )

        logger.info("========== BROWNFIELD COMPLETE ==========")
        return {
            "projects_scanned": len(project_ids),
            "discovered": total_discovered,
            "evaluated": total_evaluated,
            "planned": plan["planned_actions"],
            "queued": plan["planned_actions"],
            "batches": execution.get("batches", 1),
            "run_id": execution["run_id"],
            "status": execution["status"],
        }



# from services.discovery import DiscoveryService
# from services.compliance import ComplianceService
# from services.planner import PlannerService
# from services.executor import ExecutorService
# from utils.logger import logger
# import config
# import uuid
# class BrownfieldService:
#     """
#     Executes the complete Brownfield governance workflow.
#     Discover
#         ↓
#     Compliance
#         ↓
#     Plan
#         ↓
#     Execute (Asynchronous via Cloud Tasks)
#     """
#     def __init__(self):
#         self.discovery = DiscoveryService()
#         self.compliance = ComplianceService()
#         self.planner = PlannerService()
#         self.executor = ExecutorService()
#     def execute(self, project_id: str,):
#         run_id = str(uuid.uuid4())
#         logger.info("Governance Run ID: %s",run_id,)
#         logger.info("Step 1/4 - Discovering resources")
#         resources = self.discovery.discover(project_id, run_id)
#         compliance = self.compliance.evaluate(resources, run_id=run_id, force_refresh=True)
#         logger.info("========== BROWNFIELD START ==========")
#         logger.info("Project: %s",project_id,)
#         discovered = len(resources)
#         logger.info(
#             "Discovery complete. %d resources discovered.",
#             discovered,
#         )
#         logger.info(
#             "Step 2/4 - Evaluating compliance"
#         )
#         compliance = self.compliance.evaluate(resources, run_id=run_id)
#         evaluated = len(compliance)
#         logger.info(
#             "Compliance complete. %d supported resources evaluated.",
#             evaluated,
#         )
#         logger.info(
#             "Step 3/4 - Generating remediation plan"
#         )
#         plan = self.planner.create(
#             compliance,
#             run_id,
#         )
#         logger.info(
#             "Remediation plan created. Run ID: %s",
#             plan["run_id"],
#         )
#         logger.info(
#             "Planned actions: %d",
#             plan["planned_actions"],
#         )
#         if plan["planned_actions"] == 0:
#             logger.info(
#                 "No remediation required. All supported resources are compliant.\n"
#                 "========== BROWNFIELD COMPLETE =========="
#             )
#             return {
#                 "project": project_id,
#                 "discovered": discovered,
#                 "evaluated": evaluated,
#                 "planned": 0,
#                 "queued": 0,
#                 "batches": 0,
#                 "run_id": run_id,
#                 "status": "COMPLIANT",
#             }
#         logger.info(
#             "Step 4/4 - Executing remediation"
#         )
#         execution = self.executor.execute_run(
#             run_id=plan["run_id"],
#             planned_actions_count=plan["planned_actions"],
#         )
#         logger.info(
#             "Remediation run queued."
#         )
#         logger.info(
#             "Run ID: %s",
#             execution["run_id"],
#         )
#         logger.info(
#             "========== BROWNFIELD COMPLETE =========="
#         )
#         return {
#             "project": project_id,
#             "discovered": discovered,
#             "evaluated": evaluated,
#             "planned": plan["planned_actions"],
#             "queued": plan["planned_actions"],
#             "batches": execution.get(
#                 "batches",
#                 (
#                     plan["planned_actions"]
#                     + config.REMEDIATION_BATCH_SIZE
#                     - 1
#                 ) // config.REMEDIATION_BATCH_SIZE 
#             ),
#             "run_id": execution["run_id"],
#             "status": execution["status"],
#         }