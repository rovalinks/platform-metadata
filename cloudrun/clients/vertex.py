from google.cloud import aiplatform_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class VertexClient:
    def __init__(self):
        self.dataset_client = aiplatform_v1.DatasetServiceClient()
        self.model_client = aiplatform_v1.ModelServiceClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.split("/")[0] == "aiplatform.googleapis.com"

    def _parse_resource_name(self, resource_url: str):
        parts = resource_url.split("//")[-1].split("/")[1:]
        project = parts[parts.index("projects") + 1]
        location = parts[parts.index("locations") + 1]
        res_id = parts[-1]
        
        if "datasets" in parts: return f"projects/{project}/locations/{location}/datasets/{res_id}", "Dataset"
        elif "models" in parts: return f"projects/{project}/locations/{location}/models/{res_id}", "Model"
        
        return resource_url, "ImmutableJob"

    def get(self, resource_name: str, **kwargs):
        res_path, res_type = self._parse_resource_name(resource_name)
        
        # Bypassing immutable resources
        if res_type == "ImmutableJob":
            return None

        try:
            if res_type == "Dataset":
                dataset = self.dataset_client.get_dataset(name=res_path)
                return SimpleNamespace(name=resource_name, labels=dict(dataset.labels) or {}, tags={})
            elif res_type == "Model":
                model = self.model_client.get_model(name=res_path)
                return SimpleNamespace(name=resource_name, labels=dict(model.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Vertex {res_type} {res_path}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        res_path, res_type = self._parse_resource_name(resource_name)

        if res_type == "ImmutableJob":
            logger.info(f"Vertex AI Jobs are immutable post-creation. Bypassing {resource_name}.")
            return True
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Vertex {res_type} {res_path} with {labels}")
            return True

        try:
            if res_type == "Dataset":
                dataset = aiplatform_v1.Dataset(name=res_path, labels=labels)
                self.dataset_client.update_dataset(dataset=dataset, update_mask={"paths": ["labels"]})
            elif res_type == "Model":
                model = aiplatform_v1.Model(name=res_path, labels=labels)
                self.model_client.update_model(model=model, update_mask={"paths": ["labels"]})
                
            logger.info(f"Successfully patched Vertex {res_type} {res_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Vertex {res_type} {res_path}: {e}")
            return False
