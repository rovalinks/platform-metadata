from extractors.base import BaseExtractor
from models.resource import Resource

class ComputeExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        resources = []
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        
        raw_payload = audit_event.get("raw_payload", {})
        payload = raw_payload.get("protoPayload", {})
        
        # Clean the raw name
        raw_name = audit_event.get("resource_name", "")
        parent_name = raw_name.removeprefix("//compute.googleapis.com/", "")
            
        # Extract Instance AND its Implicit Disks
        if "instances.insert" in method:
            resources.append(Resource(name=parent_name, asset_type="compute.googleapis.com/Instance", project=project_id))
            
            request = payload.get("request", {})
            zone = parent_name.split("/zones/")[1].split("/")[0] if "/zones/" in parent_name else "global"
            
            for disk in request.get("disks", []):
                disk_name = disk.get("initializeParams", {}).get("diskName") or parent_name.split("/")[-1]
                disk_url = f"projects/{project_id}/zones/{zone}/disks/{disk_name}"
                resources.append(Resource(name=disk_url, asset_type="compute.googleapis.com/Disk", project=project_id))

        # Handle standalone creations
        elif "disks.insert" in method:
            resources.append(Resource(name=parent_name, asset_type="compute.googleapis.com/Disk", project=project_id))
        elif "routers.insert" in method:
            resources.append(Resource(name=parent_name, asset_type="compute.googleapis.com/Router", project=project_id))

        return resources