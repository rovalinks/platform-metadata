from extractors.base import BaseExtractor
from models.resource import Resource

class VertexExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        if "DatasetService.CreateDataset" in method:
            return [Resource(name=resource_name, asset_type="aiplatform.googleapis.com/Dataset", project=project_id)]
        elif "ModelService.UploadModel" in method:
            return [Resource(name=resource_name, asset_type="aiplatform.googleapis.com/Model", project=project_id)]
        elif "JobService.CreateCustomJob" in method:
            return [Resource(name=resource_name, asset_type="aiplatform.googleapis.com/CustomJob", project=project_id)]
        elif "PipelineService.CreatePipelineJob" in method:
            return [Resource(name=resource_name, asset_type="aiplatform.googleapis.com/PipelineJob", project=project_id)]
            
        return []
