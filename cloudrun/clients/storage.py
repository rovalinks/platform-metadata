from google.cloud import storage
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class StorageClient:
    def __init__(self):
        self.client = storage.Client()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("storage.googleapis.com/")

    def _parse_bucket_name(self, resource_url: str) -> str:
        return resource_url.split("/")[-1]

    def get(self, resource_name: str, **kwargs):
        bucket_name = self._parse_bucket_name(resource_name)
        try:
            bucket = self.client.get_bucket(bucket_name)
            return SimpleNamespace(name=resource_name, labels=bucket.labels or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Storage Bucket {bucket_name}: {e}")
            raise

    # EXACT METHOD SIGNATURE EXPECTED BY EXECUTOR.PY
    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Storage Bucket {resource_name} with labels: {labels}")
            return True

        bucket_name = self._parse_bucket_name(resource_name)
        try:
            bucket = self.client.get_bucket(bucket_name)
            bucket.labels = labels
            bucket.patch()
            
            logger.info(f"Successfully patched Storage Bucket {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Storage Bucket {bucket_name}: {e}")
            return False