from utils.logger import logger
from models.compliance import ComplianceResult, ComplianceSummary
from services.governance import GovernanceService
from services.capability import CapabilityService
from repositories.snapshot_repository import SnapshotRepository

class ComplianceService:
    """Evaluates governance compliance for one or more GCP resources."""
    
    def __init__(self):
        self.governance = GovernanceService()
        self.capability = CapabilityService()
        
    def evaluate(self, resources, run_id: str | None = None, force_refresh: bool = False):
        """
        Evaluate compliance for a provided list of resources.
        """
        logger.info("Evaluating compliance for %d resource(s)", len(resources))
        
        if force_refresh:
            self.governance.registry.load_all(force_refresh=True)
            
        results = []
        label_cache = {}
        tag_cache = {}
        
        for resource in resources:
            is_label_supported = self.capability.supports_labels(resource.asset_type)
            is_tag_supported = self.capability.supports_tags(resource.asset_type)
            
            if not (is_label_supported or is_tag_supported):
                logger.debug("Skipping unsupported resource type: %s", resource.asset_type)
                continue
                
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
                
            result = self._evaluate_resource(resource, expected, is_label_mode=is_label_supported)
            results.append(result)
            
        return results

    def _evaluate_resource(self, resource, expected: dict, is_label_mode: bool = True):
        actual = resource.labels if is_label_mode else resource.tags
        missing = []
        incorrect = []

        # 1. Create a safe, all-lowercase copy of the actual GCP labels
        actual_lower = {str(k).lower(): str(v).lower() for k, v in actual.items()} if actual else {}

        for key, expected_value in expected.items():
            # 2. Force the YAML key/value to lowercase for the check
            safe_key = str(key).lower()
            safe_expected_value = str(expected_value).lower()
            
            actual_value = actual_lower.get(safe_key)

            if actual_value is None:
                missing.append(key) # Keep original YAML key for the planner
            elif actual_value != safe_expected_value:
                incorrect.append(key)
                
        return ComplianceResult(
            asset_type=resource.asset_type,
            name=resource.name,
            project=resource.project,
            compliant=(len(missing) == 0 and len(incorrect) == 0),
            missing_labels=missing,
            incorrect_labels=incorrect,
        )

    def evaluate_resource(self, resource):
        """Evaluate compliance for a single discovered resource."""
        if self.capability.supports_labels(resource.asset_type):
            expected = self.governance.expected_labels(resource.project)
            return self._evaluate_resource(resource, expected, is_label_mode=True)
        else:
            expected = self.governance.expected_tags(resource.project)
            return self._evaluate_resource(resource, expected, is_label_mode=False)

    def summary(self, resources):
        """Generate a summary for a provided list of resources."""
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