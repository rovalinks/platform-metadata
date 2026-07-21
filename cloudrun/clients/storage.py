from google.cloud import storage
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class StorageClient:
    def __init__(self):
        self.client = storage.Client()
        self.dry_run = config.DRY_RUN

    # Fixed missing supports method
    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("storage.googleapis.com/")

    def _parse_bucket_name(self, resource_url: str) -> str:
        return resource_url.split("/")[-1]

    # Fixed signature to accept executor.py contract
    def get(self, resource_name: str, **kwargs):
        bucket_name = self._parse_bucket_name(resource_name)
        try:
            bucket = self.client.get_bucket(bucket_name)
            return SimpleNamespace(labels=bucket.labels or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Storage Bucket {bucket_name}: {e}")
            raise

    # Fixed signature to accept executor.py contract
    def patch(self, resource_name: str, expected_labels: dict, expected_tags: dict, **kwargs) -> bool:
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Storage Bucket {resource_name} with labels: {expected_labels}")
            return True

        bucket_name = self._parse_bucket_name(resource_name)
        try:
            bucket = self.client.get_bucket(bucket_name)
            
            current_labels = bucket.labels or {}
            current_labels.update(expected_labels)
            
            bucket.labels = current_labels
            bucket.patch()
            
            logger.info(f"Successfully patched Storage Bucket {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Storage Bucket {bucket_name}: {e}")
            return False