from google.cloud import resourcemanager_v3
from utils.logger import logger
import config

def get_all_active_projects():
    """Queries GCP to find all ACTIVE projects the engine has access to."""
    logger.info("Fetching all active projects from Resource Manager...")
    client = resourcemanager_v3.ProjectsClient()
    request = resourcemanager_v3.SearchProjectsRequest(query="state:ACTIVE")
    
    project_ids = []
    for project in client.search_projects(request=request):
        # Dynamically ignore the project the engine is running in
        if project.project_id != config.PROJECT_ID:
            project_ids.append(project.project_id)
            
    logger.info("Discovered %d active projects.", len(project_ids))
    return project_ids
