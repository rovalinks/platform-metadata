from google.cloud import monitoring_v3
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class MonitoringClient:
    def __init__(self):
        self.client = monitoring_v3.AlertPolicyServiceClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("monitoring.googleapis.com/")

    def get(self, resource_name: str, **kwargs):
        pol_name = resource_name.replace("//monitoring.googleapis.com/", "")
        try:
            policy = self.client.get_alert_policy(name=pol_name)
            return SimpleNamespace(name=resource_name, labels=dict(policy.user_labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Monitoring Alert Policy {pol_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        if self.dry_run: return True

        pol_name = resource_name.replace("//monitoring.googleapis.com/", "")
        try:
            policy = monitoring_v3.AlertPolicy(name=pol_name, user_labels=labels)
            self.client.update_alert_policy(alert_policy=policy, update_mask={"paths": ["user_labels"]})
            logger.info(f"Successfully patched Monitoring Alert Policy {pol_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Monitoring Alert Policy {pol_name}: {e}")
            return False
