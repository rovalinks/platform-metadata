from extractors.base import BaseExtractor
from models.resource import Resource

class DataplexExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        if "DataplexService.CreateEntryGroup" in method:
            return [Resource(name=resource_name, asset_type="dataplex.googleapis.com/EntryGroup", project=project_id)]
        elif "DataScanService.CreateDataScan" in method:
            return [Resource(name=resource_name, asset_type="dataplex.googleapis.com/DataScan", project=project_id)]
            
        return []
