from google.cloud import dataform_v1beta1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class DataformClient:
    def __init__(self):
        self.client = dataform_v1beta1.DataformClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("dataform.googleapis.com/")

    def get(self, resource_name: str, **kwargs):
        repo_name = resource_name.replace("//dataform.googleapis.com/", "")
        try:
            repo = self.client.get_repository(name=repo_name)
            return SimpleNamespace(name=resource_name, labels=dict(repo.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Dataform Repository {repo_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        if self.dry_run: return True

        repo_name = resource_name.replace("//dataform.googleapis.com/", "")
        try:
            repo = dataform_v1beta1.Repository(name=repo_name, labels=labels)
            self.client.update_repository(repository=repo, update_mask={"paths": ["labels"]})
            logger.info(f"Successfully patched Dataform Repository {repo_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Dataform Repository {repo_name}: {e}")
            return False
