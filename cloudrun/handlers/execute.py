from flask import jsonify, request

from services.executor import ExecutorService


def execute():
    """
    Execute a previously generated remediation plan.

    GET /execute?run_id=<run-id>
    """

    run_id = request.args.get(
        "run_id"
    )

    if not run_id:

        return (
            jsonify(
                {
                    "error": (
                        "Missing required query parameter: run_id"
                    )
                }
            ),
            400,
        )

    executor = ExecutorService()

    try:

        return jsonify(
            executor.execute_run(
                run_id
            )
        )

    except RuntimeError as error:

        message = str(error)

        if "already been executed" in message:

            return (
                jsonify(
                    {
                        "error": message
                    }
                ),
                409,
            )

        if "was not found" in message:

            return (
                jsonify(
                    {
                        "error": message
                    }
                ),
                404,
            )

        return (
            jsonify(
                {
                    "error": message
                }
            ),
            500,
        )