from extractors.base import BaseExtractor
from models.resource import Resource

class DataformExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        if "Dataform.CreateRepository" in method:
            return [Resource(name=resource_name, asset_type="dataform.googleapis.com/Repository", project=project_id)]
        return []
