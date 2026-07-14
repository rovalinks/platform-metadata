from repositories.execution_repository import ExecutionRepository
from repositories.remediation_repository import RemediationRepository


class RunStatusService:
    """
    Returns the current status of a remediation run.
    """

    def __init__(self):
        self.remediation = RemediationRepository()
        self.execution = ExecutionRepository()

    def get_status(
        self,
        run_id: str,
    ):

        plan_counts = self.remediation.count_by_status(
            run_id
        )

        execution_counts = self.execution.count_by_status(
            run_id
        )

        planned = (
            plan_counts.get("PLANNED", 0)
            + plan_counts.get("IN_PROGRESS", 0)
            + plan_counts.get("SUCCESS", 0)
            + plan_counts.get("FAILED", 0)
        )

        successful = execution_counts.get(
            "SUCCESS",
            0,
        )

        failed = execution_counts.get(
            "FAILED",
            0,
        )

        processed = successful + failed

        remaining = max(
            planned - processed,
            0,
        )

        progress = (
            round(
                (processed / planned) * 100,
                2,
            )
            if planned
            else 100
        )

        if planned == 0:
            status = "EMPTY"

        elif remaining == 0:
            status = "COMPLETED"

        else:
            status = "RUNNING"

        return {
            "run_id": run_id,
            "planned": planned,
            "processed": processed,
            "successful": successful,
            "failed": failed,
            "remaining": remaining,
            "progress": progress,
            "status": status,
        }