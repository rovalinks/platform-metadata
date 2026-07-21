from google.cloud import resourcemanager_v3
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class ResourceManagerClient:
    def __init__(self):
        self.client = resourcemanager_v3.ProjectsClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("cloudresourcemanager.googleapis.com/")

    def _parse_resource_name(self, resource_url: str):
        parts = resource_url.replace("//cloudresourcemanager.googleapis.com/", "").split("/")
        project_id = parts[-1]
        return f"projects/{project_id}" if not project_id.startswith("projects/") else project_id

    def get(self, resource_name: str, **kwargs):
        project_name = self._parse_resource_name(resource_name)
        try:
            project = self.client.get_project(name=project_name)
            return SimpleNamespace(name=resource_name, labels=dict(project.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Project {project_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Project {resource_name} with {labels}")
            return True

        project_name = self._parse_resource_name(resource_name)
        try:
            project = self.client.get_project(name=project_name)
            project.labels = labels
            
            self.client.update_project(
                project=project,
                update_mask={"paths": ["labels"]}
            )
            
            logger.info(f"Successfully patched Project {project_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Project {project_name}: {e}")
            return False