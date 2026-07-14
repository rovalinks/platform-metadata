from flask import jsonify
from services.reporting import ReportingService

def compliance_report():
    service = ReportingService()
    return jsonify(service.compliance())