import requests
import google.auth
from google.auth.transport.requests import Request
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class DNSClient:
    def __init__(self):
        self.dry_run = config.DRY_RUN
        self.credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("dns.googleapis.com/")

    def _get_headers(self):
        if not self.credentials.valid: self.credentials.refresh(Request())
        return {"Authorization": f"Bearer {self.credentials.token}", "Content-Type": "application/json"}

    def _get_url(self, resource_name: str):
        parts = resource_name.replace("//dns.googleapis.com/", "").split("/")
        project = parts[parts.index("projects") + 1]
        zone = parts[parts.index("managedZones") + 1]
        return f"https://dns.googleapis.com/dns/v1/projects/{project}/managedZones/{zone}"

    def get(self, resource_name: str, **kwargs):
        url = self._get_url(resource_name)
        try:
            response = requests.get(url, headers=self._get_headers())
            if response.status_code in (403, 404): return None
            response.raise_for_status()
            return SimpleNamespace(name=resource_name, labels=response.json().get("labels", {}), tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Cloud DNS {resource_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        if self.dry_run: return True

        url = self._get_url(resource_name)
        try:
            response = requests.patch(url, headers=self._get_headers(), json={"labels": labels})
            response.raise_for_status()
            logger.info(f"Successfully patched Cloud DNS {resource_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Cloud DNS {resource_name}: {e}")
            return False
