from extractors.base import BaseExtractor
from models.resource import Resource

class StorageExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        # GCP Audit Log method for bucket creation
        if "storage.buckets.create" in method.lower():
            return [Resource(name=resource_name, asset_type="storage.googleapis.com/Bucket", project=project_id)]
            
        return []