from google.cloud import run_v2
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class CloudRunClient:
    def __init__(self):
        self.client = run_v2.ServicesClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("run.googleapis.com/")

    def _parse_resource_name(self, resource_url: str):
        parts = resource_url.removeprefix("//run.googleapis.com/", "").split("/")
        project = parts[parts.index("projects") + 1]
        location = parts[parts.index("locations") + 1]
        service = parts[parts.index("services") + 1]
        return f"projects/{project}/locations/{location}/services/{service}"

    def get(self, resource_name: str, **kwargs):
        service_name = self._parse_resource_name(resource_name)
        try:
            service = self.client.get_service(name=service_name)
            return SimpleNamespace(name=resource_name, labels=dict(service.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Cloud Run Service {service_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Cloud Run {resource_name} with {labels}")
            return True

        service_name = self._parse_resource_name(resource_name)
        try:
            service = self.client.get_service(name=service_name)
            service.labels = labels
            
            self.client.update_service(
                service=service,
                update_mask={"paths": ["labels"]}
            )
            logger.info(f"Successfully patched Cloud Run {service_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Cloud Run {service_name}: {e}")
            return False
