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

    def project_metadata(self, seed_value: str):
        """Returns the application and matching deployment binding based on the seed value."""
        for application in self.registry.load_all():
            for binding in application.get("bindings", []):
                if binding.get("cloud") != "gcp":
                    continue
                
                # The seed_value passed from the resource's label matches the YAML's projectId
                if binding.get("projectId") == seed_value:
                    logger.info(
                        "Matched application '%s' for seed value '%s'",
                        application.get("product", "unknown"),
                        seed_value,
                    )
                    return application, binding
        
        logger.warning("No registry mapping found for seed value: %s", seed_value)
        return None, None

    def expected_labels(self, seed_value: str, asset_type: str = None):
        """Returns expected governance labels for a resource based on its seed value."""
        logger.info("Loading governance labels for seed value: %s", seed_value)
        application, binding = self.project_metadata(seed_value)
        if application is None:
            return {}

        labels = {}

        # 1. Dynamically extract all root-level YAML keys (No hardcoded translations!)
        for key, value in application.items():
            if key not in ["schemaVersion", "bindings"]:
                labels[key.lower()] = normalize_label_value(value)

        # 2. Dynamically extract all binding-level YAML keys
        for key, value in binding.items():
            if key not in ["cloud", "projectId"]:
                labels[key.lower()] = normalize_label_value(value)

        # 3. Exclude product and region specifically for Project-level resources
        if asset_type == "cloudresourcemanager.googleapis.com/Project":
            labels.pop("product", None)     
            labels.pop("application", None) 
            labels.pop("region", None)      

        return labels

    def expected_tags(self, seed_value: str, asset_type: str = None):
        """Returns expected governance tags for a resource based on its seed value."""
        logger.info("Loading governance tags for seed value: %s", seed_value)
        application, binding = self.project_metadata(seed_value)
        if application is None:
            return {}
            
        tags = {}

        # 1. Dynamically extract all root-level YAML keys (No hardcoded translations!)
        for key, value in application.items():
            if key not in ["schemaVersion", "bindings"]:
                tags[key.lower()] = normalize_label_value(value)

        # 2. Dynamically extract all binding-level YAML keys
        for key, value in binding.items():
            if key not in ["cloud", "projectId"]:
                tags[key.lower()] = normalize_label_value(value)

        # 3. Exclude product and region specifically for Project-level resources
        if asset_type == "cloudresourcemanager.googleapis.com/Project":
            tags.pop("product", None)
            tags.pop("application", None)
            tags.pop("region", None)

        return tags