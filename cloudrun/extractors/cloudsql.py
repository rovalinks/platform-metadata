from extractors.base import BaseExtractor
from models.resource import Resource

class CloudSQLExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        # Catches Cloud SQL creation events
        if "cloudsql.instances.create" in method:
            return [Resource(name=resource_name, asset_type="sqladmin.googleapis.com/Instance", project=project_id)]
            
        return []