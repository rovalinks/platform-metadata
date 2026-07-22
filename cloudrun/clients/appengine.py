from google.cloud import appengine_admin_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class AppEngineClient:
    def __init__(self):
        self.client = appengine_admin_v1.ApplicationsClient()
        self.versions_client = appengine_admin_v1.VersionsClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("appengine.googleapis.com/")

    def get(self, resource_name: str, **kwargs):
        try:
            if "/versions/" in resource_name:
                parts = resource_name.replace("//appengine.googleapis.com/", "").split("/")
                app_id = parts[parts.index("apps") + 1]
                service_id = parts[parts.index("services") + 1]
                version_id = parts[parts.index("versions") + 1]
                
                req = appengine_admin_v1.GetVersionRequest(name=f"apps/{app_id}/services/{service_id}/versions/{version_id}")
                version = self.versions_client.get_version(request=req)
                return SimpleNamespace(name=resource_name, labels=dict(version.labels) if version.labels else {}, tags={})
            else:
                app_id = resource_name.replace("//appengine.googleapis.com/apps/", "")
                app = self.client.get_application(name=f"apps/{app_id}")
                return SimpleNamespace(name=resource_name, labels=dict(app.labels) if app.labels else {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch App Engine {resource_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        try:
            if "/versions/" in resource_name:
                parts = resource_name.replace("//appengine.googleapis.com/", "").split("/")
                app_id = parts[parts.index("apps") + 1]
                service_id = parts[parts.index("services") + 1]
                version_id = parts[parts.index("versions") + 1]
                
                v_name = f"apps/{app_id}/services/{service_id}/versions/{version_id}"
                version = appengine_admin_v1.Version(name=v_name, labels=labels)
                req = appengine_admin_v1.UpdateVersionRequest(name=v_name, version=version, update_mask={"paths": ["labels"]})
                self.versions_client.update_version(request=req)
            else:
                app_id = resource_name.replace("//appengine.googleapis.com/apps/", "")
                app = appengine_admin_v1.Application(name=f"apps/{app_id}", labels=labels)
                req = appengine_admin_v1.UpdateApplicationRequest(name=app.name, application=app, update_mask={"paths": ["labels"]})
                self.client.update_application(request=req)
                
            logger.info(f"Successfully patched App Engine {resource_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch App Engine {resource_name}: {e}")
            return False


# from google.cloud import appengine_admin_v1
# from utils.logger import logger
# from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
# import config
# from types import SimpleNamespace

# class AppEngineClient:
#     def __init__(self):
#         self.client = appengine_admin_v1.ApplicationsClient()
#         self.dry_run = config.DRY_RUN

#     def supports(self, asset_type: str) -> bool:
#         supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
#         return asset_type in supported_types and asset_type.startswith("appengine.googleapis.com/")

#     def _parse_resource_name(self, resource_url: str):
#         # CAI format: //appengine.googleapis.com/apps/APP_ID (usually the project ID)
#         parts = resource_url.replace("//appengine.googleapis.com/", "").split("/")
#         app_id = parts[parts.index("apps") + 1]
#         return f"apps/{app_id}" if not app_id.startswith("apps/") else app_id

#     def get(self, resource_name: str, **kwargs):
#         app_name = self._parse_resource_name(resource_name)
#         try:
#             app = self.client.get_application(name=app_name)
#             return SimpleNamespace(name=resource_name, labels=dict(app.labels) or {}, tags={})
#         except Exception as e:
#             logger.error(f"Failed to fetch App Engine {app_name}: {e}")
#             raise

#     def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
#         resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
#         if self.dry_run:
#             logger.info(f"[DRY RUN] Would patch App Engine {resource_name} with {labels}")
#             return True

#         app_name = self._parse_resource_name(resource_name)
#         try:
#             app = appengine_admin_v1.Application(name=app_name, labels=labels)
#             self.client.update_application(
#                 application=app,
#                 update_mask={"paths": ["labels"]}
#             )
#             logger.info(f"Successfully patched App Engine {app_name}")
#             return True
#         except Exception as e:
#             logger.error(f"Failed to patch App Engine {app_name}: {e}")
#             return False
