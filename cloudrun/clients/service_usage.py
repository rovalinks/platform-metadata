from google.cloud import service_usage_v1
from utils.logger import logger

class ServiceUsageClient:
    def __init__(self):
        self.client = service_usage_v1.ServiceUsageClient()

    def get_enabled_apis(self, project_id: str) -> set:
        """Returns a set of enabled API domain names (e.g., {'compute.googleapis.com', 'storage.googleapis.com'})."""
        logger.info(f"Fetching enabled APIs for project {project_id}...")
        try:
            request = service_usage_v1.ListServicesRequest(
                parent=f"projects/{project_id}",
                filter="state:ENABLED"
            )
            
            enabled_apis = set()
            for service in self.client.list_services(request=request):
                # service.config.name looks like "compute.googleapis.com"
                enabled_apis.add(service.config.name)
                
            logger.info(f"Found {len(enabled_apis)} enabled APIs for {project_id}.")
            return enabled_apis
            
        except Exception as e:
            logger.error(f"Failed to fetch enabled APIs for {project_id}: {e}")
            # Fail open: if we can't fetch the list, return empty so we don't accidentally block everything
            return set()

