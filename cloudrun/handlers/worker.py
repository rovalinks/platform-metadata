from flask import (
    jsonify,
    request,
)

from services.worker import (
    WorkerService,
)


def worker():
    """
    Executes one remediation batch.

    Called only by Cloud Tasks.
    """

    payload = request.get_json()

    if not payload:
        return (
            jsonify(
                {
                    "error": "Missing request body"
                }
            ),
            400,
        )

    required = [
        "run_id",
        "batch_number",
        "total_batches",
        "offset",
        "batch_size",
    ]

    missing = [
        field
        for field in required
        if field not in payload
    ]

    if missing:
        return (
            jsonify(
                {
                    "error": (
                        "Missing fields: "
                        + ", ".join(missing)
                    )
                }
            ),
            400,
        )

    service = WorkerService()

    result = service.execute(
        run_id=payload["run_id"],
        offset=payload["offset"],
        batch_size=payload["batch_size"],
    )

    return jsonify(
        {
            "run_id": payload["run_id"],
            "batch_number": payload["batch_number"],
            "total_batches": payload["total_batches"],
            "processed": result["processed"],
            "successful": result["successful"],
            "failed": result["failed"],
        }
    )