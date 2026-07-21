from google.cloud import artifactregistry_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class ArtifactRegistryClient:
    def __init__(self):
        self.client = artifactregistry_v1.ArtifactRegistryClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.startswith("artifactregistry.googleapis.com/")

    def _parse_resource_name(self, resource_url: str):
        # CAI format: //artifactregistry.googleapis.com/projects/P/locations/L/repositories/R[cite: 4]
        parts = resource_url.replace("//artifactregistry.googleapis.com/", "").split("/")[cite: 4]
        
        # SAFELY BYPASS IF THIS IS JUST A LOCATION, NOT A REPOSITORY[cite: 4]
        if "repositories" not in parts:[cite: 4]
            return None[cite: 4]
            
        project = parts[parts.index("projects") + 1][cite: 4]
        location = parts[parts.index("locations") + 1][cite: 4]
        repo = parts[parts.index("repositories") + 1][cite: 4]
        return f"projects/{project}/locations/{location}/repositories/{repo}"[cite: 4]

    def get(self, resource_name: str, **kwargs):
        repo_name = self._parse_resource_name(resource_name)[cite: 4]
        if not repo_name: return None # <--- ADD THIS[cite: 4]
        try:
            repo = self.client.get_repository(name=repo_name)[cite: 4]
            return SimpleNamespace(name=resource_name, labels=dict(repo.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Artifact Registry {repo_name}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource[cite: 4]
        
        repo_name = self._parse_resource_name(resource_name)[cite: 4]
        if not repo_name: # <--- ADD THIS[cite: 4]
            return True[cite: 4]

        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Artifact Registry {resource_name} with {labels}")
            return True

        try:
            repo = self.client.get_repository(name=repo_name)
            repo.labels = labels
            
            self.client.update_repository(
                repository=repo,
                update_mask={"paths": ["labels"]}
            )
            logger.info(f"Successfully patched Artifact Registry {repo_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Artifact Registry {repo_name}: {e}")
            return False