import config
from flask import (jsonify,request,)
from services.brownfield import BrownfieldService


def brownfield():

    project = request.args.get("project") or config.PROJECT_ID

    if not project:
        return (
            jsonify(
                {
                    "error": "Missing project parameter."
                }
            ),
            400,
        )

    service = BrownfieldService()

    result = service.execute(
        project
    )

    # Check if 'batches' exists in the result
    if "batches" not in result:
        return jsonify(
            {
                "message": "Brownfield remediation complete: No actions were required.",
                "run_id": result.get("run_id"),
                "status": "COMPLETED_NO_ACTIONS"
            }
        ), 200

    return jsonify(result)