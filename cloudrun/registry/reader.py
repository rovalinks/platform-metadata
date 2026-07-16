import time
import yaml
from io import StringIO
from google.cloud import storage
from cache.registry_cache import RegistryCache
from config import REGISTRY_BUCKET, REGISTRY_PREFIX, REGISTRY_CACHE_TTL
from utils.logger import logger
class RegistryReader:
    """Reads application registry YAML files from Cloud Storage."""
    def __init__(self):
        self.client = storage.Client()
        self._last_refresh = 0
    def load_all(self, force_refresh: bool = False):
        current_time = time.time()
        applications = None if force_refresh else RegistryCache.get()
        if applications is not None and (current_time - self._last_refresh) < REGISTRY_CACHE_TTL:
            return applications
        logger.info("========== REGISTRY READER START ==========")
        logger.info("Bucket: %s | Prefix: %s", REGISTRY_BUCKET, REGISTRY_PREFIX)
        applications = []
        blobs = list(self.client.list_blobs(REGISTRY_BUCKET, prefix=REGISTRY_PREFIX))
        logger.info("Blob count: %d", len(blobs))
        for blob in blobs:
            if not blob.name.endswith(".yaml"):
                continue
            logger.info("Blob: %s", blob.name)
            applications.append(yaml.safe_load(StringIO(blob.download_as_text())))
        logger.info("Applications loaded: %d", len(applications))
        logger.info("Registry cache refreshed. Expires in %s seconds.", REGISTRY_CACHE_TTL)
        logger.info("========== REGISTRY READER END ==========")
        RegistryCache.set(applications)
        self._last_refresh = current_time
        return applications