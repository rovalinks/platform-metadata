import requests
import google.auth
from google.auth.transport.requests import Request
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class CloudSQLClient:
    def __init__(self):
        self.dry_run = config.DRY_RUN
        # FIX: Explicitly request the cloud-platform scope for REST API calls
        self.credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])

    def _get_headers(self):
        if not self.credentials.valid:
            self.credentials.refresh(Request())
        return {
            "Authorization": f"Bearer {self.credentials.token}",
            "Content-Type": "application/json"
        }

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("sqladmin.googleapis.com/")

    def _parse_resource_name(self, resource_url: str):
        parts = resource_url.replace("//sqladmin.googleapis.com/", "").split("/")
        project = parts[parts.index("projects") + 1]
        instance = parts[parts.index("instances") + 1]
        return project, instance

    def get(self, resource_name: str, **kwargs):
        project, instance = self._parse_resource_name(resource_name)
        url = f"https://sqladmin.googleapis.com/v1/projects/{project}/instances/{instance}"
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            data = response.json()
            
            labels = data.get("settings", {}).get("userLabels", {})
            return SimpleNamespace(name=resource_name, labels=labels, tags={})
        except requests.exceptions.HTTPError as e:
            # FIX: Gracefully bypass if the instance is deleted (404) or IAM hasn't propagated (403)
            if e.response.status_code in (403, 404):
                logger.warning(f"Cloud SQL resource {instance} returned {e.response.status_code}. Bypassing.")
                return None
            logger.error(f"Failed to fetch Cloud SQL Instance {instance}: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to fetch Cloud SQL Instance {instance}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Cloud SQL {resource_name} with {labels}")
            return True

        project, instance = self._parse_resource_name(resource_name)
        url = f"https://sqladmin.googleapis.com/v1/projects/{project}/instances/{instance}"
        
        body = {
            "settings": {
                "userLabels": labels
            }
        }
        
        try:
            response = requests.patch(url, headers=self._get_headers(), json=body)
            response.raise_for_status()
            logger.info(f"Successfully patched Cloud SQL Instance {instance}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Cloud SQL Instance {instance}: {e}")
            return False