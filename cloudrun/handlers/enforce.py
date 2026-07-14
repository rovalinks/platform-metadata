from flask import jsonify, request

from services.context import RequestContext
from services.governance import GovernanceService
from services.enforcement import EnforcementService


def enforce():
    """
    Executes label enforcement.

    GET /enforce
        Execute enforcement for every registered project.

    GET /enforce?project=<project-id>
        Execute enforcement for a single project.
    """

    context = RequestContext()
    governance = GovernanceService()
    service = EnforcementService(context.discovery)

    project_id = request.args.get("project")

    if project_id:

        result = service.execute(project_id)

    else:

        result = []

        for project in governance.projects():

            result.extend(
                service.execute(
                    project["projectId"]
                )
            )

    return jsonify(result)