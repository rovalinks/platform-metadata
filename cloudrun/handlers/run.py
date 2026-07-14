from flask import jsonify, request

from services.reporting import ReportingService


def run():
    """
    Returns summary for a remediation run.

    GET /reports/run?run_id=<run-id>
    """

    run_id = request.args.get(
        "run_id"
    )

    if not run_id:

        return (
            jsonify(
                {
                    "error":
                        "Missing required query parameter: run_id"
                }
            ),
            400,
        )

    service = ReportingService()

    return jsonify(
        service.run(
            run_id
        )
    )