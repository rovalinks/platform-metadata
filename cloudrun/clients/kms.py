from google.cloud import kms_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class KMSClient:
    def __init__(self):
        self.client = kms_v1.KeyManagementServiceClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.split("/")[0] == "cloudkms.googleapis.com"

    def _parse_resource_name(self, resource_url: str):
        # Format: //cloudkms.googleapis.com/projects/P/locations/L/keyRings/R/cryptoKeys/K
        return resource_url.replace("//cloudkms.googleapis.com/", "")

    def get(self, resource_name: str, **kwargs):
        key_name = self._parse_resource_name(resource_name)
        try:
            key = self.client.get_crypto_key(name=key_name)
            return SimpleNamespace(name=resource_name, labels=dict(key.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch CryptoKey {key_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch CryptoKey {resource_name} with {labels}")
            return True

        key_name = self._parse_resource_name(resource_name)
        try:
            key = self.client.get_crypto_key(name=key_name)
            key.labels = labels
            
            self.client.update_crypto_key(
                crypto_key=key,
                update_mask={"paths": ["labels"]}
            )
            
            logger.info(f"Successfully patched CryptoKey {key_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch CryptoKey {key_name}: {e}")
            return False