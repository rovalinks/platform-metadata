from utils.logger import logger
from services.compliance import ComplianceService
from services.adapter import AdapterService
from services.executor import ExecutorService


class EnforcementService:
    def __init__(self, discovery):
        self.discovery = discovery
        self.compliance = ComplianceService()
        self.adapters = AdapterService()
        self.executor = ExecutorService()

    def plan(self, project_id: str):
        actions = []
        
        # Updated: Retrieve resources first
        resources = self.discovery.discover(project_id)
        
        # Updated: Pass resources to evaluate
        for result in self.compliance.evaluate(resources):
            if result.compliant:
                continue

            client = self.adapters.client_for(result.asset_type)
            if client is None:
                continue

            actions.append(
                {
                    "resource": result.name,
                    "asset_type": result.asset_type,
                    # Note: Ensure this method signature still works with project_id 
                    # or update it to use the resources/project metadata if needed
                    "labels": self.compliance.governance.expected_labels(project_id),
                    "action": "apply_labels",
                }
            )

        return actions

    def execute(self, project_id: str):
        logger.info(
            "Executing enforcement for project %s",
            project_id,
        )
        
        actions = self.plan(project_id)
        
        result = self.executor.execute(
            actions
        )
        
        logger.info(
            "Completed enforcement with %d actions",
            len(actions),
        )
        
        return result