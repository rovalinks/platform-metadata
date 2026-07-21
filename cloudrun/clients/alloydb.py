from google.cloud import alloydb_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class AlloyDBClient:
    def __init__(self):
        self.client = alloydb_v1.AlloyDBAdminClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("alloydb.googleapis.com/")

    def get(self, resource_name: str, **kwargs):
        res_path = resource_name.replace("//alloydb.googleapis.com/", "")
        try:
            if "/instances/" in res_path:
                inst = self.client.get_instance(name=res_path)
                return SimpleNamespace(name=resource_name, labels=dict(inst.labels) or {}, tags={})
            else:
                cluster = self.client.get_cluster(name=res_path)
                return SimpleNamespace(name=resource_name, labels=dict(cluster.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch AlloyDB {res_path}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        if self.dry_run: return True

        res_path = resource_name.replace("//alloydb.googleapis.com/", "")
        try:
            if "/instances/" in res_path:
                inst = alloydb_v1.Instance(name=res_path, labels=labels)
                self.client.update_instance(instance=inst, update_mask={"paths": ["labels"]})
            else:
                cluster = alloydb_v1.Cluster(name=res_path, labels=labels)
                self.client.update_cluster(cluster=cluster, update_mask={"paths": ["labels"]})
            logger.info(f"Successfully patched AlloyDB {res_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch AlloyDB {res_path}: {e}")
            return False
