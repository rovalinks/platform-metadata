from flask import jsonify, request
from services.reporting import ReportingService

def dashboard():
    """
    Returns governance dashboard KPIs.
    GET /dashboard
    """
    service = ReportingService()
    scope = request.args.get("scope", "organization")
    project_id = request.args.get("project_id")
    return jsonify(service.dashboard(scope=scope, project_id=project_id))