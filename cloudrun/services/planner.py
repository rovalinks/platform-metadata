from models.remediation import RemediationPlan
from repositories.remediation_repository import RemediationRepository
from services.capability import CapabilityService
from services.governance import GovernanceService
from utils.logger import logger


class PlannerService:
    """
    Generates remediation plans for non-compliant resources.

    The planner never modifies GCP resources.
    It only creates and persists remediation plans.
    """

    PROJECT_ASSET_TYPE = "cloudresourcemanager.googleapis.com/Project"

    def __init__(self):
        self.governance = GovernanceService()
        self.repository = RemediationRepository()
        self.capability = CapabilityService()

    def create(
        self,
        compliance_results,
        run_id: str,
    ):
        logger.info("Generating remediation plan")

        plans = []
        expected_metadata_cache = {}

        for result in compliance_results:
            if result.compliant:
                continue

            project = result.project
            asset_type = result.asset_type
            
            # Extract product seed label if available (will be None for Project containers)
            product_seed = getattr(result, "product_seed", None)
            if not product_seed and hasattr(result, "labels"):
                product_seed = result.labels.get("product")

            mode = (
                "labels"
                if self.capability.supports_labels(asset_type)
                else "tags"
            )
            
            # Safe cache key incorporating asset type and seed
            cache_key = (project, asset_type, product_seed, mode)

            if cache_key not in expected_metadata_cache:
                if mode == "labels":
                    expected_metadata_cache[cache_key] = (
                        self.governance.expected_labels(
                            actual_project_id=project,
                            product_seed_label=product_seed,
                            asset_type=asset_type,
                        )
                    )
                else:
                    expected_metadata_cache[cache_key] = (
                        self.governance.expected_tags(
                            actual_project_id=project,
                            product_seed_label=product_seed,
                            asset_type=asset_type,
                        )
                    )

            expected_metadata = expected_metadata_cache[cache_key]

            # 1. Build the desired metadata using both missing AND incorrect labels
            planned_labels = {}
            remediation_keys = set(result.missing_labels)

            for key in remediation_keys:
                if key in expected_metadata:
                    planned_labels[key] = expected_metadata[key]

            # 2. Decide the enforcement mechanism
            planned_tags = {}
            if mode == "labels":
                if not planned_labels:
                    continue
            else:
                planned_tags = planned_labels
                planned_labels = {}

                if not planned_tags:
                    continue

            # 3. Create the RemediationPlan
            plans.append(
                RemediationPlan(
                    run_id=run_id,
                    project_id=project,
                    asset_type=asset_type,
                    resource_name=result.name,
                    missing_labels=list(remediation_keys),
                    planned_labels=planned_labels,
                    planned_tags=planned_tags,
                )
            )

        stored = self.repository.save(plans)

        if stored == 0:
            logger.warning(
                "No remediation actions generated for run %s",
                run_id,
            )

        logger.info(
            "Created remediation run %s with %d planned actions",
            run_id,
            stored,
        )

        return {
            "run_id": run_id,
            "planned_actions": stored,
        }