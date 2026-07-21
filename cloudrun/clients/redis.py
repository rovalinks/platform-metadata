from google.cloud import redis_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class RedisClient:
    def __init__(self):
        self.client = redis_v1.CloudRedisClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("redis.googleapis.com/")

    def _parse_resource_name(self, resource_url: str):
        # CAI format: //redis.googleapis.com/projects/P/locations/L/instances/I
        parts = resource_url.replace("//redis.googleapis.com/", "").split("/")
        project = parts[parts.index("projects") + 1]
        location = parts[parts.index("locations") + 1]
        instance = parts[parts.index("instances") + 1]
        return f"projects/{project}/locations/{location}/instances/{instance}"

    def get(self, resource_name: str, **kwargs):
        instance_name = self._parse_resource_name(resource_name)
        try:
            instance = self.client.get_instance(name=instance_name)
            return SimpleNamespace(name=resource_name, labels=dict(instance.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Redis {instance_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Redis {resource_name} with {labels}")
            return True

        instance_name = self._parse_resource_name(resource_name)
        try:
            instance = redis_v1.Instance(name=instance_name, labels=labels)
            # Fire and forget the Long Running Operation
            self.client.update_instance(
                instance=instance,
                update_mask={"paths": ["labels"]}
            )
            logger.info(f"Successfully dispatched patch for Redis {instance_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Redis {instance_name}: {e}")
            return False
