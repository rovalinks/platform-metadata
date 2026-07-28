from google.cloud import resourcemanager_v3
from utils.logger import logger
import config

def get_all_active_projects():
    """Queries GCP to find active projects matching the current deployment environment."""
    logger.info("Fetching active projects from Resource Manager...")
    client = resourcemanager_v3.ProjectsClient()
    request = resourcemanager_v3.SearchProjectsRequest(query="state:ACTIVE")
    
    # 1. Determine environment suffix ('dev' or 'prod') from the engine's host project name
    engine_project = config.PROJECT_ID.lower()
    env_suffix = "dev" if "-dev" in engine_project else ("prod" if "-prod" in engine_project else "")
    
    project_ids = []
    for project in client.search_projects(request=request):
        pid = project.project_id
        
        # 2. Skip the host project running the governance engine
        if pid == config.PROJECT_ID:
            continue

        # 3. Filter strictly based on the environment tag in the project name
        if env_suffix:
            # Matches "-dev-" or ends with "-dev", etc.
            if f"-{env_suffix}-" in pid or pid.endswith(f"-{env_suffix}"):
                project_ids.append(pid)
            # --- FIX: Explicitly allow POC projects to show up in the Dev dashboard ---
            elif env_suffix == "dev" and ("-poc-" in pid or pid.endswith("-poc")):
                project_ids.append(pid)
        else:
            # Fallback if no env suffix is detected
            project_ids.append(pid)
            
    logger.info("Discovered %d active %s/poc projects.", len(project_ids), env_suffix.upper())
    return project_ids