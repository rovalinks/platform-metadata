from google.cloud import container_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class GKEClient:
    def __init__(self):
        self.client = container_v1.ClusterManagerClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("container.googleapis.com/")

    def _parse_resource_name(self, resource_url: str):
        # Format: //container.googleapis.com/projects/P/locations/L/clusters/C
        parts = resource_url.removeprefix("//container.googleapis.com/", "").split("/")
        project = parts[parts.index("projects") + 1]
        
        if "locations" in parts:
            location = parts[parts.index("locations") + 1]
        elif "zones" in parts: # CAI sometimes returns zones for zonal clusters
            location = parts[parts.index("zones") + 1]
        else:
            raise ValueError(f"Could not parse location from GKE cluster: {resource_url}")
            
        cluster = parts[parts.index("clusters") + 1]
        return f"projects/{project}/locations/{location}/clusters/{cluster}"

    def get(self, resource_name: str, **kwargs):
        cluster_name = self._parse_resource_name(resource_name)
        try:
            cluster = self.client.get_cluster(name=cluster_name)
            # Map GKE's 'resource_labels' to the standard 'labels' expected by executor.py
            return SimpleNamespace(name=resource_name, labels=dict(cluster.resource_labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch GKE Cluster {cluster_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch GKE Cluster {resource_name} with {labels}")
            return True

        cluster_name = self._parse_resource_name(resource_name)
        try:
            # We must fetch the cluster first to get the label_fingerprint for optimistic locking
            cluster = self.client.get_cluster(name=cluster_name)
            
            request = container_v1.SetLabelsRequest(
                name=cluster_name,
                resource_version=cluster.label_fingerprint,
                resource_labels=labels
            )
            
            self.client.set_labels(request=request)
            logger.info(f"Successfully patched GKE Cluster {cluster_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch GKE Cluster {cluster_name}: {e}")
            return False
