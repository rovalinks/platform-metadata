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
            mode = (
                "labels"
                if self.capability.supports_labels(result.asset_type)
                else "tags"
            )
            cache_key = (project, mode)

            if cache_key not in expected_metadata_cache:
                if mode == "labels":
                    expected_metadata_cache[cache_key] = (
                        self.governance.expected_labels(project)
                    )
                else:
                    expected_metadata_cache[cache_key] = (
                        self.governance.expected_tags(project)
                    )

            expected_metadata = expected_metadata_cache[cache_key]

            # 1. Build the desired metadata once
            planned_labels = {}
            for label in result.missing_labels:
                if label in expected_metadata:
                    planned_labels[label] = expected_metadata[label]

            # 2. Decide the enforcement mechanism
            planned_tags = {}
            if mode == "labels":
                # If no labels were actually missing/expected, skip
                if not planned_labels:
                    continue
            else:
                # If not label-supported, assume tag-supported
                planned_tags = planned_labels
                planned_labels = {}

                # If no tags were generated, skip
                if not planned_tags:
                    continue

            # 3. Create the RemediationPlan
            plans.append(
                RemediationPlan(
                    run_id=run_id,
                    project_id=project,
                    asset_type=result.asset_type,
                    resource_name=result.name,
                    missing_labels=result.missing_labels,
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