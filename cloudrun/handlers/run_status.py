from flask import jsonify

from services.run_status import RunStatusService


service = RunStatusService()


def run_status(
    run_id: str,
):
    """
    Returns the current status of a remediation run.
    """

    return jsonify(
        service.get_status(
            run_id,
        )
    )