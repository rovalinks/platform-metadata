from registry.reader import RegistryReader
from utils.labels import normalize_label_value
from utils.logger import logger
class GovernanceService:
    """Provides governance metadata from the application registry."""
    def __init__(self):
        self.registry = RegistryReader()
    def projects(self):
        """
        Returns every registered GCP project.
        """
        projects = []
        for application in self.registry.load_all():
            for binding in application["bindings"]:
                if binding["cloud"] != "gcp":
                    continue
                projects.append(
                    {
                        "projectId": binding["projectId"],
                        "application": application["product"],
                        "binding": binding,
                    }
                )
        return projects
    def project_metadata(self, project_id: str):
        """
        Returns the application and matching deployment binding.
        """
        for application in self.registry.load_all():
            for binding in application["bindings"]:
                if binding["cloud"] != "gcp":
                    continue
                if binding["projectId"] == project_id:
                    logger.info(
                        "Matched application '%s' for project '%s'",
                        application["product"],
                        project_id,
                    )
                    return application, binding
        logger.warning(
            "No registry entry found for project %s",
            project_id,
        )
        return None, None
    def expected_labels(self, project_id: str, force_refresh: bool = False):
        """
        Returns expected governance labels for a project.
        """
        self.registry.load_all(force_refresh=force_refresh)
        logger.info(
            "Loading governance metadata for project %s",
            project_id,
        )
        application, binding = self.project_metadata(project_id)
        if application is None:
            return {}
        return {
            "application": normalize_label_value(application["product"]),
            "team": normalize_label_value(application["team"]),
            "owner": normalize_label_value(application["owner"]),
            "budgetowner": normalize_label_value(application["budgetOwner"]),
            "organization": normalize_label_value(application["organization"]),
            "department": normalize_label_value(application["department"]),
            "costcenter": normalize_label_value(application["costCenter"]),
            "environment": normalize_label_value(binding["environment"]),
            "businesscriticality": normalize_label_value(binding["businessCriticality"]),
        }
    def expected_tags(self, project_id: str):
        """
        Returns expected governance labels for a project.
        """
        logger.info(
            "Loading governance metadata for project %s",
            project_id,
        )
        application, binding = self.project_metadata(project_id)
        if application is None:
            return {}
        return {
            "application": normalize_label_value(application["product"]),
            "team": normalize_label_value(application["team"]),
            "owner": normalize_label_value(application["owner"]),
            "budgetOwner": normalize_label_value(application["budgetOwner"]),
            "organization": normalize_label_value(application["organization"]),
            "department": normalize_label_value(application["department"]),
            "costCenter": normalize_label_value(application["costCenter"]),
            "environment": normalize_label_value(binding["environment"]),
            "businessCriticality": normalize_label_value(binding["businessCriticality"]),
        }