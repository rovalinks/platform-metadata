from google.cloud import appengine_admin_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class AppEngineClient:
    def __init__(self):
        self.client = appengine_admin_v1.ApplicationsClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("appengine.googleapis.com/")

    def _parse_resource_name(self, resource_url: str):
        # CAI format: //appengine.googleapis.com/apps/APP_ID (usually the project ID)
        parts = resource_url.replace("//appengine.googleapis.com/", "").split("/")
        app_id = parts[parts.index("apps") + 1]
        return f"apps/{app_id}" if not app_id.startswith("apps/") else app_id

    def get(self, resource_name: str, **kwargs):
        app_name = self._parse_resource_name(resource_name)
        try:
            app = self.client.get_application(name=app_name)
            return SimpleNamespace(name=resource_name, labels=dict(app.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch App Engine {app_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch App Engine {resource_name} with {labels}")
            return True

        app_name = self._parse_resource_name(resource_name)
        try:
            app = appengine_admin_v1.Application(name=app_name, labels=labels)
            self.client.update_application(
                application=app,
                update_mask={"paths": ["labels"]}
            )
            logger.info(f"Successfully patched App Engine {app_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch App Engine {app_name}: {e}")
            return False
