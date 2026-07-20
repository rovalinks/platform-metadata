from google.cloud import bigquery
from utils.logger import logger
import config

class BigQueryClient:
    def __init__(self):
        self.client = bigquery.Client()
        self.dry_run = config.DRY_RUN

    def _parse_resource_name(self, resource_url: str):
        """Converts CAI/Eventarc URL to BQ SDK format (project.dataset.table)"""
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

    def get(self, resource_name: str, asset_type: str) -> dict:
        bq_id, res_type = self._parse_resource_name(resource_name)
        
        try:
            if res_type == "Dataset":
                dataset = self.client.get_dataset(bq_id)
                return dataset.labels or {}
            elif res_type in ["Table", "Model"]:
                table = self.client.get_table(bq_id)
                return table.labels or {}
        except Exception as e:
            logger.error(f"Failed to fetch BigQuery {res_type} {bq_id}: {e}")
            raise

    def patch(self, resource_name: str, asset_type: str, expected_labels: dict, expected_tags: dict) -> bool:
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch BigQuery {asset_type} {resource_name} with {expected_labels}")
            return True

        bq_id, res_type = self._parse_resource_name(resource_name)

        try:
            if res_type == "Dataset":
                dataset = self.client.get_dataset(bq_id)
                dataset.labels = self._merge_labels(dataset.labels, expected_labels)
                self.client.update_dataset(dataset, ["labels"])
                
            elif res_type in ["Table", "Model"]:
                table = self.client.get_table(bq_id)
                table.labels = self._merge_labels(table.labels, expected_labels)
                self.client.update_table(table, ["labels"])
                
            logger.info(f"Successfully patched BigQuery {res_type} {bq_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch BigQuery {res_type} {bq_id}: {e}")
            return False

    def _merge_labels(self, existing: dict, expected: dict) -> dict:
        if not existing:
            return expected
        merged = existing.copy()
        merged.update(expected)
        return merged