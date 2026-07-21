from google.cloud import dataplex_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class DataplexClient:
    def __init__(self):
        self.client = dataplex_v1.DataplexServiceClient()
        # FIX: EntryGroups require the CatalogServiceClient
        self.catalog_client = dataplex_v1.CatalogServiceClient() 
        self.datascan_client = dataplex_v1.DataScanServiceClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("dataplex.googleapis.com/")

    def _parse_resource_name(self, resource_url: str):
        parts = resource_url.replace("//dataplex.googleapis.com/", "").split("/")
        project = parts[parts.index("projects") + 1]
        location = parts[parts.index("locations") + 1]
        res_id = parts[-1]
        
        if "entryGroups" in parts: return f"projects/{project}/locations/{location}/entryGroups/{res_id}", "EntryGroup"
        elif "dataScans" in parts: return f"projects/{project}/locations/{location}/dataScans/{res_id}", "DataScan"
        return None, None

    def get(self, resource_name: str, **kwargs):
        res_path, res_type = self._parse_resource_name(resource_name)
        try:
            if res_type == "EntryGroup":
                # FIX: Use catalog_client
                group = self.catalog_client.get_entry_group(name=res_path)
                return SimpleNamespace(name=resource_name, labels=dict(group.labels) or {}, tags={})
            elif res_type == "DataScan":
                scan = self.datascan_client.get_data_scan(name=res_path)
                return SimpleNamespace(name=resource_name, labels=dict(scan.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Dataplex {res_type} {res_path}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Dataplex {resource_name} with {labels}")
            return True

        res_path, res_type = self._parse_resource_name(resource_name)
        try:
            if res_type == "EntryGroup":
                group = dataplex_v1.EntryGroup(name=res_path, labels=labels)
                # FIX: Use catalog_client
                self.catalog_client.update_entry_group(entry_group=group, update_mask={"paths": ["labels"]})
            elif res_type == "DataScan":
                scan = dataplex_v1.DataScan(name=res_path, labels=labels)
                self.datascan_client.update_data_scan(data_scan=scan, update_mask={"paths": ["labels"]})
                
            logger.info(f"Successfully patched Dataplex {res_type} {res_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Dataplex {res_type} {res_path}: {e}")
            return False