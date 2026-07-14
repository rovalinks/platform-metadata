from flask import jsonify, request

from services.context import RequestContext
from services.compliance import ComplianceService
import config

context = RequestContext()

# Updated initialization: service no longer accepts discovery in constructor
service = ComplianceService()


def compliance():
    """
    Evaluates compliance.

    Behaviour:
      - GET /compliance
            Evaluate every registered GCP project.

      - GET /compliance?project=<project-id>
            Evaluate only the supplied project.
    """

    project_id = (
        request.args.get("project")
        or config.PROJECT_ID
    )
    
    # Discovery call now handles the optional run_id internally.
    # No changes required here as discover() now defaults run_id to None.
    resources = context.discovery.discover(project_id)

    # Evaluate and summarize based on the discovered resources
    results = service.evaluate(resources)
    summary = service.summary(resources)

    return jsonify(
        {
            "summary": summary.to_dict(),
            "results": [
                result.to_dict()
                for result in results
            ],
        }
    )