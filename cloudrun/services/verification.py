from utils.logger import logger
from models.verification import VerificationResult
from services.discovery import DiscoveryService
from services.governance import GovernanceService

class VerificationService:
    def __init__(self, discovery):
        self.discovery = discovery
        self.governance = GovernanceService()

    def verify(self, project_id: str):
        logger.info("Verifying metadata for project %s", project_id)
        
        expected = self.governance.expected_labels(project_id)
        resources = self.discovery.discover(project_id)
        
        results = []
        for resource in resources:
            missing = []
            for key, value in expected.items():
                if resource.labels.get(key) != value:
                    missing.append(key)
            
            results.append(
                VerificationResult(
                    resource=resource.name,
                    asset_type=resource.asset_type,
                    verified=len(missing) == 0,
                    message=(
                        "Metadata verified."
                        if len(missing) == 0
                        else f"Missing or incorrect labels: {', '.join(missing)}"
                    ),
                )
            )

        logger.info("Verified %d resources", len(results))
        logger.info("Verification completed")
        
        return results