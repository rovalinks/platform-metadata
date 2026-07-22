from extractors.base import BaseExtractor
from models.resource import Resource

class BigQueryExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        if "DatasetService.InsertDataset" in method or "DatasetService.UpdateDataset" in method or "DatasetService.PatchDataset" in method:
            return [Resource(name=resource_name, asset_type="bigquery.googleapis.com/Dataset", project=project_id)]

        elif "TableService.InsertTable" in method or "TableService.UpdateTable" in method or "TableService.PatchTable" in method:
            return [Resource(name=resource_name, asset_type="bigquery.googleapis.com/Table", project=project_id)]
            
        elif "ModelService.InsertModel" in method or "ModelService.UpdateModel" in method or "ModelService.PatchModel" in method:
            return [Resource(name=resource_name, asset_type="bigquery.googleapis.com/Model", project=project_id)]

        return []


# from extractors.base import BaseExtractor
# from models.resource import Resource

# class BigQueryExtractor(BaseExtractor):
#     def extract(self, audit_event: dict) -> list:
#         resources = []
#         method = audit_event.get("method_name", "")
#         project_id = audit_event.get("project_id")
        
#         raw_payload = audit_event.get("raw_payload", {})
#         proto = raw_payload.get("protoPayload", {})
#         resource_name = audit_event.get("resource_name") or proto.get("resourceName", "")

#         # BigQuery Audit Logs use specific Service Methods
#         if "DatasetService.InsertDataset" in method or "datasets.create" in method.lower():
#             resources.append(Resource(name=resource_name, asset_type="bigquery.googleapis.com/Dataset", project=project_id))
            
#         elif "TableService.InsertTable" in method or "tables.create" in method.lower():
#             resources.append(Resource(name=resource_name, asset_type="bigquery.googleapis.com/Table", project=project_id))
            
#         elif "ModelService.InsertModel" in method or "models.create" in method.lower():
#             resources.append(Resource(name=resource_name, asset_type="bigquery.googleapis.com/Model", project=project_id))
            
#         return resources