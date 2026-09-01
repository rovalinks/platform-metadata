from registry.reader import RegistryReader
from utils.labels import normalize_label_value
from utils.logger import logger

class GovernanceService:
    """Provides governance metadata from the application registry."""

    def __init__(self):
        self.registry = RegistryReader()

    def projects(self):
        """Returns every registered GCP project."""
        projects = []
        for application in self.registry.load_all():
            for binding in application.get("bindings", []):
                if binding.get("cloud") != "gcp":
                    continue
                projects.append(
                    {
                        "projectId": binding["projectId"],
                        "application": application.get("product", "unknown"),
                        "binding": binding,
                    }
                )
        return projects

    def project_metadata(self, actual_project_id: str, product_seed_label: str = None, asset_type: str = None):
        """
        Returns application/project baseline metadata.
        
        - If asset_type is a GCP Project container, it resolves the dedicated Project Baseline file 
          (where product matches the projectId or is set to 'project').
        - If evaluating an application resource, it resolves using BOTH actual_project_id and product_seed_label.
        """
        all_apps = self.registry.load_all()

        # 1. GCP Project Container Baseline Lookup
        if asset_type == "cloudresourcemanager.googleapis.com/Project":
            for application in all_apps:
                for binding in application.get("bindings", []):
                    if binding.get("cloud") != "gcp":
                        continue
                    
                    project_id = binding.get("projectId")
                    product_name = application.get("product", "")

                    # Matches dedicated project baseline (product equals projectId or 'project')
                    if project_id == actual_project_id and (product_name == actual_project_id or product_name.lower() == "project"):
                        logger.info(
                            "Matched Project Baseline metadata for project '%s'",
                            actual_project_id,
                        )
                        return application, binding

            logger.warning("No dedicated project-level baseline mapping found for project: %s", actual_project_id)
            return None, None

        # 2. Granular Application Resource Lookup
        for application in all_apps:
            if application.get("product") == product_seed_label:
                for binding in application.get("bindings", []):
                    if binding.get("cloud") != "gcp":
                        continue
                        
                    if binding.get("projectId") == actual_project_id:
                        logger.info(
                            "Matched application '%s' for project '%s'",
                            product_seed_label,
                            actual_project_id,
                        )
                        return application, binding

        logger.warning(f"No registry mapping found for Product: '{product_seed_label}' in Project: '{actual_project_id}'")
        return None, None

    def expected_labels(self, actual_project_id: str, product_seed_label: str = None, asset_type: str = None):
        """Returns expected governance labels for a resource or project based on asset_type."""
        logger.info(f"Loading governance labels for Project: {actual_project_id}, Product: {product_seed_label}, AssetType: {asset_type}")
        application, binding = self.project_metadata(actual_project_id, product_seed_label, asset_type)
        
        if application is None:
            return {}

        labels = {}

        # Extract root-level YAML keys
        for key, value in application.items():
            if key not in ["schemaVersion", "bindings"]:
                labels[key.lower()] = normalize_label_value(value)

        # Extract binding-level YAML keys
        for key, value in binding.items():
            if key not in ["cloud", "projectId"]:
                labels[key.lower()] = normalize_label_value(value)

        # Enforce strict whitelist for Project-level container resources
        if asset_type == "cloudresourcemanager.googleapis.com/Project":
            allowed_project_keys = {
                "team", "owner", "budgetowner", "organization", 
                "department", "environment", "businesscriticality"
            }
            labels = {k: v for k, v in labels.items() if k in allowed_project_keys}

        return labels

    def expected_tags(self, actual_project_id: str, product_seed_label: str = None, asset_type: str = None):
        """Returns expected governance tags for a resource or project based on asset_type."""
        logger.info(f"Loading governance tags for Project: {actual_project_id}, Product: {product_seed_label}, AssetType: {asset_type}")
        application, binding = self.project_metadata(actual_project_id, product_seed_label, asset_type)
        
        if application is None:
            return {}
            
        tags = {}

        # Extract root-level YAML keys
        for key, value in application.items():
            if key not in ["schemaVersion", "bindings"]:
                tags[key.lower()] = normalize_label_value(value)

        # Extract binding-level YAML keys
        for key, value in binding.items():
            if key not in ["cloud", "projectId"]:
                tags[key.lower()] = normalize_label_value(value)

        # Enforce strict whitelist for Project-level container resources
        if asset_type == "cloudresourcemanager.googleapis.com/Project":
            allowed_project_keys = {
                "team", "owner", "budgetowner", "organization", 
                "department", "environment", "businesscriticality"
            }
            tags = {k: v for k, v in tags.items() if k in allowed_project_keys}

        return tags