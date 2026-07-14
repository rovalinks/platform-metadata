from services.executor import (
    ExecutorService,
)


class WorkerService:
    """
    Executes one Cloud Tasks remediation batch.
    """

    def __init__(self):

        self.executor = ExecutorService()

    def execute(
        self,
        run_id: str,
        offset: int,
        batch_size: int,
    ):

        return self.executor.execute_batch(
            run_id=run_id,
            offset=offset,
            batch_size=batch_size,
        )