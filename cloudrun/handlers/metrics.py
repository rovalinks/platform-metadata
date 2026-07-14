from flask import jsonify, request
from services.reporting import ReportingService

def metrics():
    """
    Returns remediation metrics.
    GET /metrics?scope=...&project_id=...
    """
    service = ReportingService()
    scope = request.args.get("scope", "organization")
    project_id = request.args.get("project_id")
    return jsonify(service.metrics(scope=scope, project_id=project_id))