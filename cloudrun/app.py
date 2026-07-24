from flask import (Flask,request,render_template)

from dispatcher import Dispatcher
from routes.pubsub import handle as pubsub_handler
from utils.org_helper import get_all_active_projects

app = Flask(__name__)


@app.get("/")
def dashboard_ui():
    return render_template("dashboard.html")

@app.post("/")
def greenfield_endpoint():
    return Dispatcher.dispatch(
        "greenfield",
        request.get_json(),
    )

@app.post("/events/pubsub")
def pubsub_endpoint():
    return pubsub_handler(request)

@app.get("/brownfield")
def brownfield_endpoint():
    project_id = request.args.get("project")
    
    if project_id:
        # Single project scan context
        project_ids = [project_id]
    else:
        # Org scan context: automatically fetch projects matching dev/prod suffix
        project_ids = get_all_active_projects()
        
    if not project_ids:
        return jsonify({"status": "SKIPPED", "reason": "No active environment projects discovered"}), 200

    # Pass the list cleanly to the brownfield engine orchestrator
    return Dispatcher.dispatch("brownfield", project_ids=project_ids)

@app.get("/")
def root():
    return Dispatcher.dispatch("health")


@app.get("/health")
def health():
    return Dispatcher.dispatch("health")


@app.get("/discover")
def discover():
    return Dispatcher.dispatch("discover")


@app.get("/compliance")
def compliance_endpoint():
    return Dispatcher.dispatch("compliance")


@app.get("/plan")
def plan_endpoint():
    return Dispatcher.dispatch("plan")


@app.get("/execute")
def execute_endpoint():
    return Dispatcher.dispatch("execute")

@app.route(
    "/runs/<run_id>",
    methods=["GET"],
)
def run_status_endpoint(run_id):

    return Dispatcher.dispatch(
        "run_status",
        run_id=run_id,
    )

@app.get("/enforce")
def enforce_endpoint():
    return Dispatcher.dispatch("enforce")


@app.get("/verify")
def verify_endpoint():
    return Dispatcher.dispatch("verify")


@app.get("/report")
def report_endpoint():
    return Dispatcher.dispatch("report")


#
# Reporting APIs
#

@app.get("/reports/dashboard")
def dashboard_endpoint():
    return Dispatcher.dispatch("dashboard")

@app.get("/reports/compliance")
def compliance_report_endpoint():
    return Dispatcher.dispatch("compliance_report")

@app.get("/reports/runs")
def runs_endpoint():
    return Dispatcher.dispatch("runs")


@app.get("/reports/run/<run_id>")
def run_endpoint(run_id):
    return Dispatcher.dispatch(
        "run",
        run_id=run_id,
    )

@app.post("/worker")
def worker_endpoint():
    return Dispatcher.dispatch("worker")

@app.get("/reports/history")
def history_endpoint():
    return Dispatcher.dispatch("history")


@app.get("/reports/metrics")
def metrics_endpoint():
    return Dispatcher.dispatch("metrics")

@app.get("/reports/resources")
def resources_endpoint():
    return Dispatcher.dispatch(
        "resources"
    )

@app.get("/reports/non-compliant")
def non_compliant_endpoint():
    return Dispatcher.dispatch(
        "non_compliant"
    )

@app.route('/projects_list', methods=['GET'])
def projects_list_endpoint():
    return Dispatcher.dispatch("projects_list")
    
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",  # nosec B104
        port=8080,
        debug=False
    )