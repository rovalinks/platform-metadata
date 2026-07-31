from google.cloud import resourcemanager_v3
from utils.logger import logger
import config

def get_all_active_projects():
    """Returns all active projects matching the current deployment environment."""
    logger.info("Fetching active projects from Resource Manager...")

    client = resourcemanager_v3.ProjectsClient()
    request = resourcemanager_v3.SearchProjectsRequest(
        query="state:ACTIVE"
    )

    engine_project = config.PROJECT_ID.lower()

    if "dev" in engine_project:
        environment = "dev"
    elif "prod" in engine_project:
        environment = "prod"
    else:
        environment = None

    logger.info(
        "Current engine project: %s | Environment: %s",
        config.PROJECT_ID,
        environment or "ALL"
    )

    project_ids = []

    for project in client.search_projects(request=request):
        pid = project.project_id
        pid_lower = pid.lower()

        # Skip the governance engine project itself
        if pid_lower == engine_project:
            continue

        # No environment detected - return everything
        if environment is None:
            project_ids.append(pid)
            continue

        # Match any occurrence of dev/prod anywhere in the project ID
        if environment in pid_lower:
            project_ids.append(pid)

    project_ids.sort()

    logger.info(
        "Discovered %d active %s project(s).",
        len(project_ids),
        environment or "ALL"
    )

    return project_ids