import os
import logging
from flask import Flask, request, render_template, jsonify

from dispatcher import Dispatcher
from routes.pubsub import handle as pubsub_handler
from utils.org_helper import get_all_active_projects

app = Flask(__name__)

# =====================================================
# UI & Webhook Endpoints
# =====================================================

@app.get("/")
def dashboard_ui():
    return render_template("dashboard.html")

@app.post("/")
def greenfield_endpoint():
    return Dispatcher.dispatch("greenfield", request.get_json())

@app.post("/events/pubsub")
def pubsub_endpoint():
    return pubsub_handler(request)

@app.get("/brownfield")
def brownfield_endpoint():
    project_id = request.args.get("project")
    
    if project_id:
        project_ids = [project_id]
    else:
        project_ids = get_all_active_projects()
        
    if not project_ids:
        return jsonify({"status": "SKIPPED", "reason": "No environment active projects found"}), 200

    from services.brownfield import BrownfieldService
    service = BrownfieldService()
    result = service.execute(project_ids=project_ids)
    
    return jsonify(result)

@app.post("/worker")
def worker_endpoint():
    return Dispatcher.dispatch("worker")

# =====================================================
# Core Engine Dispatchers
# =====================================================

@app.get("/health")
def health():
    return Dispatcher.dispatch("health")

@app.get("/discover")
def discover_endpoint():
    return Dispatcher.dispatch("discover")

@app.get("/verify")
def verify_endpoint():
    return Dispatcher.dispatch("verify")

# =====================================================
# Reporting & Dashboard Data APIs
# =====================================================

@app.get("/report")
def report_endpoint():
    return Dispatcher.dispatch("report")

@app.get("/reports/dashboard")
def dashboard_endpoint():
    return Dispatcher.dispatch("dashboard")

@app.get("/reports/compliance")
def compliance_report_endpoint():
    return Dispatcher.dispatch("compliance_report")

@app.get("/reports/runs")
def runs_endpoint():
    return Dispatcher.dispatch("runs")

@app.route("/runs/<run_id>", methods=["GET"])
def run_status_endpoint(run_id):
    return Dispatcher.dispatch("run_status", run_id=run_id)

@app.get("/reports/run/<run_id>")
def run_endpoint(run_id):
    return Dispatcher.dispatch("run", run_id=run_id)

@app.get("/reports/history")
def history_endpoint():
    return Dispatcher.dispatch("history")

@app.get("/reports/metrics")
def metrics_endpoint():
    return Dispatcher.dispatch("metrics")

@app.get("/reports/resources")
def resources_endpoint():
    return Dispatcher.dispatch("resources")

@app.get("/reports/non-compliant")
def non_compliant_endpoint():
    return Dispatcher.dispatch("non_compliant")

@app.route('/projects_list', methods=['GET'])
def projects_list_endpoint():
    return Dispatcher.dispatch("projects_list")

# =====================================================
# Security & Error Handling (CodeQL Compliant)
# =====================================================

@app.errorhandler(Exception)
def handle_global_error(error):
    """Catches all unhandled exceptions and prevents stack trace exposure."""
    logging.exception("An unhandled exception occurred during a request.")
    return jsonify({"error": "An internal server error occurred. Please check server logs."}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # debug=False strictly enforced to prevent CWE-209 Stack Trace Exposure
    app.run(host="0.0.0.0", port=port, debug=False)