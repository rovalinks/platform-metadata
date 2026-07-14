from utils.logger import logger
from models.report import GovernanceReport
from services.discovery import DiscoveryService
from services.compliance import ComplianceService
from services.enforcement import EnforcementService

class ReportService:

    def __init__(self, repository, discovery):
        self.repository = repository 
        self.discovery = discovery
        self.compliance = ComplianceService()
        self.enforcement = EnforcementService(discovery)

    def run(self, run_id: str):
        """
        Returns a complete summary for a remediation run.
        """
        return self.repository.remediation_run_summary(run_id)

    def report(self, project_id: str):
        logger.info("Generating governance report")

        # Step 1: Discover resources first
        resources = self.discovery.discover(project_id)
        
        # Step 2: Pass resources to compliance and enforcement
        compliance = self.compliance.evaluate(resources)
        
        # Note: Depending on your EnforcementService implementation, 
        # you may need to pass resources here if it still internally uses project_id
        actions = self.enforcement.plan(project_id)

        compliant = sum(
            1 for item in compliance
            if item.compliant
        )

        return GovernanceReport(
            project=project_id,
            total_resources=len(resources),
            supported_resources=len(compliance),
            compliant_resources=compliant,
            non_compliant_resources=len(compliance) - compliant,
            enforcement_candidates=len(actions),
            compliance_percentage=(
                round(
                    compliant / len(compliance) * 100,
                    2,
                )
                if compliance
                else 100.0
            ),
        )