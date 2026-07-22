from extractors.base import BaseExtractor
from models.resource import Resource

class AppEngineExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        if "Applications.CreateApplication" in method or "Applications.UpdateApplication" in method:
            return [Resource(name=resource_name, asset_type="appengine.googleapis.com/Application", project=project_id)]

        elif "Versions.CreateVersion" in method or "Versions.UpdateVersion" in method:
            return [Resource(name=resource_name, asset_type="appengine.googleapis.com/Version", project=project_id)]
            
        return []

# from extractors.base import BaseExtractor
# from models.resource import Resource

# class AppEngineExtractor(BaseExtractor):
#     def extract(self, audit_event: dict) -> list:
#         method = audit_event.get("method_name", "")
#         project_id = audit_event.get("project_id")
#         resource_name = audit_event.get("resource_name", "")

#         if "Applications.CreateApplication" in method:
#             return [Resource(name=resource_name, asset_type="appengine.googleapis.com/Application", project=project_id)]
#         return []
