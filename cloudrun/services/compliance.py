from utils.logger import logger
from models.compliance import ComplianceResult, ComplianceSummary
from services.governance import GovernanceService
from services.capability import CapabilityService


class ComplianceService:
    """Evaluates governance compliance for one or more GCP resources."""

    def __init__(self):
        self.governance = GovernanceService()
        self.capability = CapabilityService()

    def evaluate(self, resources, run_id: str | None = None):
        """
        Evaluate compliance for a provided list of resources.
        """
        logger.info(
            "Evaluating compliance for %d resource(s)",
            len(resources),
        )

        results = []
        # Caches to avoid redundant governance API calls
        label_cache = {}
        tag_cache = {}

        for resource in resources:
            is_label_supported = self.capability.supports_labels(resource.asset_type)
            is_tag_supported = self.capability.supports_tags(resource.asset_type)

            # Check if resource type is supported for either label or tag evaluation
            if not (is_label_supported or is_tag_supported):
                continue

            # Fetch expected schema based on capability, using caches
            project = resource.project
            expected = {}

            if is_label_supported:
                if project not in label_cache:
                    label_cache[project] = self.governance.expected_labels(project)
                expected = label_cache[project]
            else:
                if project not in tag_cache:
                    tag_cache[project] = self.governance.expected_tags(project)
                expected = tag_cache[project]

            # Evaluate resource
            results.append(
                self._evaluate_resource(
                    resource,
                    expected,
                    is_label_supported
                )
            )

        logger.info(
            "Evaluated %d supported resources",
            len(results),
        )

        if run_id:
            from repositories.snapshot_repository import SnapshotRepository

            SnapshotRepository().save_compliance(
                results,
                run_id,
            )

        return results

    def _evaluate_resource(
        self,
        resource,
        expected_schema,
        is_label_mode,
    ):
        """Helper to evaluate compliance for a single resource."""
        missing = []
        incorrect = []

        # Choose the metadata source based on the mode determined in evaluate()
        actual_metadata = (resource.labels if is_label_mode else resource.tags) or {}
        logger.info("Mode: %s", "labels" if is_label_mode else "tags")
        logger.info("Expected: %s", expected_schema)
        logger.info("Actual: %s", actual_metadata)

        for key, expected_value in expected_schema.items():
            actual_value = actual_metadata.get(key)

            if actual_value is None:
                missing.append(key)
            elif str(actual_value) != str(expected_value):
                incorrect.append(key)

        return ComplianceResult(
            asset_type=resource.asset_type,
            name=resource.name,
            project=resource.project,
            compliant=(
                len(missing) == 0
                and len(incorrect) == 0
            ),
            missing_labels=missing,
            incorrect_labels=incorrect,
        )

    def evaluate_resource(self, resource):
        """
        Evaluate compliance for a single discovered resource.
        """
        # Determine mode for single resource evaluation
        if self.capability.supports_labels(resource.asset_type):
            expected = self.governance.expected_labels(resource.project)
            return self._evaluate_resource(resource, expected, is_label_mode=True)
        else:
            expected = self.governance.expected_tags(resource.project)
            return self._evaluate_resource(resource, expected, is_label_mode=False)

    def summary(self, resources):
        """
        Generate a summary for a provided list of resources.
        """
        results = self.evaluate(resources)
        total = len(results)
        
        compliant = sum(1 for result in results if result.compliant)
        non_compliant = total - compliant
        percentage = ((compliant / total) * 100) if total else 100

        return ComplianceSummary(
            total_resources=total,
            compliant_resources=compliant,
            non_compliant_resources=non_compliant,
            compliance_percentage=round(percentage, 2),
        )