from google.cloud import storage
from utils.logger import logger
import config

class StorageClient:
    def __init__(self):
        self.client = storage.Client()
        self.dry_run = config.DRY_RUN

    def _parse_bucket_name(self, resource_url: str) -> str:
        # Resource URLs usually look like: projects/_/buckets/my-bucket-name
        return resource_url.split("/")[-1]

    def get(self, resource_name: str, asset_type: str) -> dict:
        bucket_name = self._parse_bucket_name(resource_name)
        try:
            bucket = self.client.get_bucket(bucket_name)
            return bucket.labels or {}
        except Exception as e:
            logger.error(f"Failed to fetch Storage Bucket {bucket_name}: {e}")
            raise

    def patch(self, resource_name: str, asset_type: str, expected_labels: dict, expected_tags: dict) -> bool:
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Storage Bucket {resource_name} with labels: {expected_labels}")
            return True

        bucket_name = self._parse_bucket_name(resource_name)
        try:
            bucket = self.client.get_bucket(bucket_name)
            
            # Merge existing labels with expected labels
            current_labels = bucket.labels or {}
            current_labels.update(expected_labels)
            
            bucket.labels = current_labels
            bucket.patch()
            
            logger.info(f"Successfully patched Storage Bucket {bucket_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Storage Bucket {bucket_name}: {e}")
            return False
            