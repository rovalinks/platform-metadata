from flask import (Flask,request,render_template)

from dispatcher import Dispatcher
from routes.pubsub import handle as pubsub_handler

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
    return Dispatcher.dispatch("brownfield")

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
    
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080,
    )