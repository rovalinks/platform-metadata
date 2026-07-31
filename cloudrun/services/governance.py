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

    def project_metadata(self, project_id: str):
        """Returns the application and matching deployment binding."""
        for application in self.registry.load_all():
            for binding in application.get("bindings", []):
                if binding.get("cloud") != "gcp":
                    continue
                if binding.get("projectId") == project_id:
                    logger.info(
                        "Matched application '%s' for project '%s'",
                        application.get("product", "unknown"),
                        project_id,
                    )
                    return application, binding

        logger.warning("No deployment binding found for project '%s'", project_id)
        return None, None

    def expected_labels(self, project_id: str, asset_type: str | None = None):
        """Returns expected governance labels for a project/resource dynamically."""
        logger.info(
            "Loading governance metadata for project %s",
            project_id,
        )
        application, binding = self.project_metadata(project_id)
        if application is None:
            return {}

        labels = {}

        # 1. Dynamically extract all root-level YAML keys
        for key, value in application.items():
            if key not in ["schemaVersion", "bindings"]:
                # GCP labels must be lowercase. Map 'product' to 'application' for legacy support.
                label_key = "application" if key == "product" else key.lower()
                labels[label_key] = normalize_label_value(value)

        # 2. Dynamically extract all binding-level YAML keys
        for key, value in binding.items():
            # REGION IS NO LONGER IGNORED HERE:
            if key not in ["cloud", "projectId"]:
                labels[key.lower()] = normalize_label_value(value)

        # 3. Exclude application/product and region specifically for Project-level resources
        if asset_type == "cloudresourcemanager.googleapis.com/Project":
            labels.pop("application", None) # Pops the 'product' label
            labels.pop("region", None)      # Pops the 'region' label

        return labels

    def expected_tags(self, project_id: str):
        """Returns expected governance tags for a project dynamically."""
        logger.info(
            "Loading governance metadata for project %s",
            project_id,
        )
        application, binding = self.project_metadata(project_id)
        if application is None:
            return {}
            
        tags = {}

        # 1. Dynamically extract all root-level YAML keys
        for key, value in application.items():
            if key not in ["schemaVersion", "bindings"]:
                tag_key = "application" if key == "product" else key
                tags[tag_key] = normalize_label_value(value)

        # 2. Dynamically extract all binding-level YAML keys
        for key, value in binding.items():
            # REGION IS NO LONGER IGNORED HERE:
            if key not in ["cloud", "projectId"]:
                tags[key] = normalize_label_value(value)

        return tags