from datetime import datetime

from google.cloud import bigquery

import config
from utils.logger import logger


class RunStatusRepository:
    """
    Persists and retrieves remediation run status.
    """

    def __init__(self):
        self.client = bigquery.Client()
        self.table = (
            f"{config.BIGQUERY_DATASET}.run_status"
        )

    def create(
        self,
        run_id: str,
        project_id: str,
        planned: int,
    ):
        row = {
            "run_id": run_id,
            "project_id": project_id,
            "status": "RUNNING",
            "planned": planned,
            "successful": 0,
            "failed": 0,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
        }

        errors = self.client.insert_rows_json(
            self.table,
            [row],
        )

        if errors:
            raise RuntimeError(errors)

        logger.info(
            "Created run status %s",
            run_id,
        )

    def complete(
        self,
        run_id: str,
        successful: int,
        failed: int,
    ):
        query = f"""
        UPDATE `{self.table}`
        SET
            status='COMPLETED',
            successful=@successful,
            failed=@failed,
            completed_at=CURRENT_TIMESTAMP()
        WHERE run_id=@run_id
        """

        self.client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "successful",
                        "INT64",
                        successful,
                    ),
                    bigquery.ScalarQueryParameter(
                        "failed",
                        "INT64",
                        failed,
                    ),
                    bigquery.ScalarQueryParameter(
                        "run_id",
                        "STRING",
                        run_id,
                    ),
                ]
            ),
        ).result()

        logger.info(
            "Run %s marked COMPLETE",
            run_id,
        )

    def get(
        self,
        run_id: str,
    ):
        query = f"""
        SELECT *
        FROM `{self.table}`
        WHERE run_id=@run_id
        LIMIT 1
        """

        job = self.client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "run_id",
                        "STRING",
                        run_id,
                    )
                ]
            ),
        )

        for row in job.result():
            return dict(row.items())

        return None