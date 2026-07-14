from flask import jsonify, request
from services.reporting import ReportingService

def non_compliant():
    service = ReportingService()
    scope = request.args.get("scope", "organization")
    project_id = request.args.get("project_id")
    limit = request.args.get("limit", default=100, type=int)
    return jsonify(service.non_compliant(scope=scope, project_id=project_id, limit=limit))