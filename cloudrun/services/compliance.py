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
            
            # ---> NEW TWO-KEY SEED LOGIC <---
            actual_labels = resource.labels if is_label_supported else resource.tags
            if not actual_labels:
                actual_labels = {}
                
            # Extract the mandatory seed label
            seed_value = actual_labels.get("product")

            # ---> THE MISSING SEED TRAP <---
            if not seed_value:
                logger.warning(f"Resource {resource.name} is missing the 'product' seed label. Flagging as non-compliant.")
                results.append(ComplianceResult(
                    asset_type=resource.asset_type,
                    name=resource.name,
                    project=resource.project,
                    compliant=False,
                    missing_labels=["product (MISSING MANDATORY SEED)"],
                    incorrect_labels=[],
                ))
                continue
            # -------------------------------
            
            # Create a unique cache key for Project + Product to prevent cross-contamination
            cache_key = f"{project}::{seed_value}"
            
            expected = {}
            
            if is_label_supported:
                if cache_key not in label_cache:
                    # Pass BOTH keys and the asset type
                    label_cache[cache_key] = self.governance.expected_labels(project, seed_value, resource.asset_type)
                expected = label_cache[cache_key]
            else:
                if cache_key not in tag_cache:
                    # Pass BOTH keys and the asset type
                    tag_cache[cache_key] = self.governance.expected_tags(project, seed_value, resource.asset_type)
                expected = tag_cache[cache_key]
                
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
        
        # ---> NEW TWO-KEY SEED LOGIC <---
        is_label_supported = self.capability.supports_labels(resource.asset_type)
        actual_labels = getattr(resource, 'labels', {}) if is_label_supported else getattr(resource, 'tags', {})
        if not actual_labels:
            actual_labels = {}
            
        seed_value = actual_labels.get("product")

        # ---> THE MISSING SEED TRAP <---
        if not seed_value:
            logger.warning(f"Resource {resource.name} is missing the 'product' seed label. Flagging as non-compliant.")
            return ComplianceResult(
                asset_type=resource.asset_type,
                name=resource.name,
                project=resource.project,
                compliant=False,
                missing_labels=["product (MISSING MANDATORY SEED)"],
                incorrect_labels=[],
            )
        # -------------------------------

        if is_label_supported:
            expected = self.governance.expected_labels(resource.project, seed_value, resource.asset_type)
            return self._evaluate_resource(resource, expected, is_label_mode=True)
        else:
            expected = self.governance.expected_tags(resource.project, seed_value, resource.asset_type)
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