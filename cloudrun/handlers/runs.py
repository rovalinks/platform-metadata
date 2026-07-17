from flask import jsonify, request
from services.reporting import ReportingService

def runs():
    scope = request.args.get("scope", "organization")
    project_id = request.args.get("project_id")
    limit = request.args.get("limit", default=100, type=int)
    service = ReportingService()
    return jsonify(service.runs(scope=scope, project_id=project_id, limit=limit))