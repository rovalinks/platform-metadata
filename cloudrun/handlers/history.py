from flask import jsonify, request

from services.reporting import ReportingService


def history():
    """
    Returns execution history for one remediation run.

    GET /history?run_id=<run-id>
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
        service.history(
            run_id
        )
    )