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

    def project_metadata(self, actual_project_id: str, product_seed_label: str):
        """Returns the application and binding by matching BOTH Project ID and Product."""
        for application in self.registry.load_all():
            
            # 1. First, check if the product matches the developer's label
            if application.get("product") == product_seed_label:
                
                # 2. Then, check if this application is bound to the actual GCP project
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

    def expected_labels(self, actual_project_id: str, product_seed_label: str, asset_type: str = None):
        """Returns expected governance labels for a resource based on its project and product seed."""
        logger.info(f"Loading governance labels for Project: {actual_project_id}, Product: {product_seed_label}")
        application, binding = self.project_metadata(actual_project_id, product_seed_label)
        
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

    def expected_tags(self, actual_project_id: str, product_seed_label: str, asset_type: str = None):
        """Returns expected governance tags for a resource based on its project and product seed."""
        logger.info(f"Loading governance tags for Project: {actual_project_id}, Product: {product_seed_label}")
        application, binding = self.project_metadata(actual_project_id, product_seed_label)
        
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