from google.cloud import functions_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class CloudFunctionsClient:
    def __init__(self):
        self.client = functions_v1.CloudFunctionsServiceClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.split("/")[0] == "cloudfunctions.googleapis.com"

    def _parse_resource_name(self, resource_url: str):
        # CAI format: //cloudfunctions.googleapis.com/projects/P/locations/L/functions/F
        parts = resource_url.split("//")[-1].split("/")[1:]
        project = parts[parts.index("projects") + 1]
        location = parts[parts.index("locations") + 1]
        function = parts[parts.index("functions") + 1]
        return f"projects/{project}/locations/{location}/functions/{function}"

    def get(self, resource_name: str, **kwargs):
        func_name = self._parse_resource_name(resource_name)
        try:
            func = self.client.get_function(name=func_name)
            return SimpleNamespace(name=resource_name, labels=dict(func.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Cloud Function {func_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Cloud Function {resource_name} with {labels}")
            return True

        func_name = self._parse_resource_name(resource_name)
        try:
            func = self.client.get_function(name=func_name)
            func.labels = labels
            
            self.client.update_function(
                function=func,
                update_mask={"paths": ["labels"]}
            )
            logger.info(f"Successfully patched Cloud Function {func_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Cloud Function {func_name}: {e}")
            return False
