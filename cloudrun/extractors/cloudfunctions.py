from extractors.base import BaseExtractor
from models.resource import Resource

class CloudFunctionsExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        if "CloudFunctionsService.CreateFunction" in method or "FunctionService.CreateFunction" in method:
            return [Resource(name=resource_name, asset_type="cloudfunctions.googleapis.com/Function", project=project_id)]
        return []
