from google.cloud import bigquery
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
from clients.base import ResourceClient
import config
from types import SimpleNamespace

class BigQueryClient(ResourceClient):
    def __init__(self):
        self.client = bigquery.Client()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("bigquery.googleapis.com/")

    def _parse_resource_name(self, resource_name: str):
        # Format: //bigquery.googleapis.com/projects/P/datasets/D/tables/T
        parts = resource_name.removeprefix("//bigquery.googleapis.com/", "").split("/")
        project = parts[parts.index("projects") + 1]
        dataset = parts[parts.index("datasets") + 1]
        return project, dataset

    def get(self, resource_name: str, **kwargs):
        project, dataset = self._parse_resource_name(resource_name)
        try:
            if "/tables/" in resource_name:
                table_id = resource_name.split("/tables/")[1]
                table_ref = f"{project}.{dataset}.{table_id}"
                table = self.client.get_table(table_ref)
                return SimpleNamespace(name=resource_name, labels=dict(table.labels) if table.labels else {}, tags={})
            
            elif "/models/" in resource_name:
                model_id = resource_name.split("/models/")[1]
                model_ref = f"{project}.{dataset}.{model_id}"
                model = self.client.get_model(model_ref)
                return SimpleNamespace(name=resource_name, labels=dict(model.labels) if model.labels else {}, tags={})
            
            else:
                dataset_ref = f"{project}.{dataset}"
                ds = self.client.get_dataset(dataset_ref)
                return SimpleNamespace(name=resource_name, labels=dict(ds.labels) if ds.labels else {}, tags={})
                
        except Exception as e:
            logger.error(f"Failed to fetch BigQuery resource {resource_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        project, dataset = self._parse_resource_name(resource_name)

        try:
            if "/tables/" in resource_name:
                table_id = resource_name.split("/tables/")[1]
                table_ref = f"{project}.{dataset}.{table_id}"
                table = self.client.get_table(table_ref)
                table.labels = labels
                self.client.update_table(table, ["labels"])
                
            elif "/models/" in resource_name:
                model_id = resource_name.split("/models/")[1]
                model_ref = f"{project}.{dataset}.{model_id}"
                model = self.client.get_model(model_ref)
                model.labels = labels
                self.client.update_model(model, ["labels"])

            else:
                dataset_ref = f"{project}.{dataset}"
                ds = self.client.get_dataset(dataset_ref)
                ds.labels = labels
                self.client.update_dataset(ds, ["labels"])

            logger.info(f"Successfully patched BigQuery resource {resource_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch BigQuery resource {resource_name}: {e}")
            return False

            

# from google.cloud import bigquery
# from utils.logger import logger
# from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
# import config
# from types import SimpleNamespace

# class BigQueryClient:
#     def __init__(self):
#         self.client = bigquery.Client()
#         self.dry_run = config.DRY_RUN

#     def supports(self, asset_type: str) -> bool:
#         supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
#         return asset_type in supported_types and asset_type.startswith("bigquery.googleapis.com/")

#     def _parse_resource_name(self, resource_url: str):
#         parts = resource_url.removeprefix("//bigquery.googleapis.com/", "").split("/")
#         project = parts[parts.index("projects") + 1] if "projects" in parts else None
#         dataset = parts[parts.index("datasets") + 1] if "datasets" in parts else None
#         table = parts[parts.index("tables") + 1] if "tables" in parts else None
#         model = parts[parts.index("models") + 1] if "models" in parts else None
        
#         if table:
#             return f"{project}.{dataset}.{table}", "Table"
#         elif model:
#             return f"{project}.{dataset}.{model}", "Model"
#         else:
#             return f"{project}.{dataset}", "Dataset"

#     def get(self, resource_name: str, **kwargs):
#         bq_id, res_type = self._parse_resource_name(resource_name)
#         try:
#             if res_type == "Dataset":
#                 dataset = self.client.get_dataset(bq_id)
#                 return SimpleNamespace(name=resource_name, labels=dataset.labels or {}, tags={})
#             elif res_type in ["Table", "Model"]:
#                 table = self.client.get_table(bq_id)
#                 return SimpleNamespace(name=resource_name, labels=table.labels or {}, tags={})
#         except Exception as e:
#             logger.error(f"Failed to fetch BigQuery {res_type} {bq_id}: {e}")
#             raise

#     # EXACT METHOD SIGNATURE EXPECTED BY EXECUTOR.PY
#     def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
#         # Safely extract the string URL whether executor passed the object or the string
#         resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
#         if self.dry_run:
#             logger.info(f"[DRY RUN] Would patch BigQuery {resource_name} with {labels}")
#             return True

#         bq_id, res_type = self._parse_resource_name(resource_name)
#         try:
#             if res_type == "Dataset":
#                 dataset = self.client.get_dataset(bq_id)
#                 dataset.labels = labels
#                 self.client.update_dataset(dataset, ["labels"])
#             elif res_type in ["Table", "Model"]:
#                 table = self.client.get_table(bq_id)
#                 table.labels = labels
#                 self.client.update_table(table, ["labels"])
                
#             logger.info(f"Successfully patched BigQuery {res_type} {bq_id}")
#             return True
#         except Exception as e:
#             logger.error(f"Failed to patch BigQuery {res_type} {bq_id}: {e}")
#             return False