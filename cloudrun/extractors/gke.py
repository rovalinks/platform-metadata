from extractors.base import BaseExtractor
from models.resource import Resource

class GKEExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        if "ClusterManager.CreateCluster" in method or "ClusterManager.UpdateCluster" in method:
            return [Resource(name=resource_name, asset_type="container.googleapis.com/Cluster", project=project_id)]
            
        return []
