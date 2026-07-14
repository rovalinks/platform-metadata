from flask import jsonify, request

from services.context import RequestContext
from services.planner import PlannerService


def plan():
    """
    Generate a remediation plan.

    GET /plan
        Generate remediation plans for all projects
        defined in the governance registry.

    GET /plan?project=<project-id>
        Generate a remediation plan for a single
        GCP project.
    """

    context = RequestContext()

    planner = PlannerService(
        context.discovery
    )

    project_id = request.args.get(
        "project"
    )

    result = planner.create(
        project_id
    )

    return jsonify(
        result
    )
