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