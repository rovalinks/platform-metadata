from google.cloud import bigquery
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("bigquery.googleapis.com/")

    def _parse_resource_name(self, resource_url: str):
        parts = resource_url.replace("//bigquery.googleapis.com/", "").split("/")
        project = parts[parts.index("projects") + 1] if "projects" in parts else None
        dataset = parts[parts.index("datasets") + 1] if "datasets" in parts else None
        table = parts[parts.index("tables") + 1] if "tables" in parts else None
        model = parts[parts.index("models") + 1] if "models" in parts else None
        
        if table:
            return f"{project}.{dataset}.{table}", "Table"
        elif model:
            return f"{project}.{dataset}.{model}", "Model"
        else:
            return f"{project}.{dataset}", "Dataset"

    def get(self, resource_name: str, **kwargs):
        bq_id, res_type = self._parse_resource_name(resource_name)
        try:
            if res_type == "Dataset":
                dataset = self.client.get_dataset(bq_id)
                return SimpleNamespace(name=resource_name, labels=dataset.labels or {}, tags={})
            elif res_type in ["Table", "Model"]:
                table = self.client.get_table(bq_id)
                return SimpleNamespace(name=resource_name, labels=table.labels or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch BigQuery {res_type} {bq_id}: {e}")
            raise

    # EXACT METHOD SIGNATURE EXPECTED BY EXECUTOR.PY
    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        # Safely extract the string URL whether executor passed the object or the string
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch BigQuery {resource_name} with {labels}")
            return True

        bq_id, res_type = self._parse_resource_name(resource_name)
        try:
            if res_type == "Dataset":
                dataset = self.client.get_dataset(bq_id)
                dataset.labels = labels
                self.client.update_dataset(dataset, ["labels"])
            elif res_type in ["Table", "Model"]:
                table = self.client.get_table(bq_id)
                table.labels = labels
                self.client.update_table(table, ["labels"])
                
            logger.info(f"Successfully patched BigQuery {res_type} {bq_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch BigQuery {res_type} {bq_id}: {e}")
            return False