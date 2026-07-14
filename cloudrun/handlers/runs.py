from flask import jsonify, request
from services.reporting import ReportingService

def runs():
    """
    Returns remediation runs.
    GET /runs?scope=...&project_id=...&limit=...
    """
    scope = request.args.get("scope", "organization")
    project_id = request.args.get("project_id")
    limit = request.args.get("limit", default=100, type=int)

    # Validate limit to prevent excessive resource usage
    if limit < 1:
        limit = 1
    if limit > 1000:
        limit = 1000

    service = ReportingService()
    return jsonify(service.runs(scope=scope, project_id=project_id, limit=limit))