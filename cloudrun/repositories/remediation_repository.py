import json

from google.cloud import bigquery

import config
from models.remediation import RemediationPlan
from utils.logger import logger


class RemediationRepository:
    """
    Persists remediation plans.

    This repository is responsible only for
    storing and retrieving remediation plans.
    """

    DEFAULT_BATCH_SIZE = 500

    def __init__(self):
        self.client = bigquery.Client()
        self.dataset = config.BIGQUERY_DATASET
        self.table = "remediation_plan"

    @property
    def table_id(self):
        return f"{self.dataset}.{self.table}"

    @staticmethod
    def _json_value(value):
        """
        BigQuery JSON columns are returned as native Python
        objects, while STRING columns are returned as text.

        Support both representations.
        """
        if isinstance(value, str):
            return json.loads(value)

        return value

    def save(
        self,
        plans: list[RemediationPlan],
    ) -> int:
        if not plans:
            return 0

        rows = []
        for plan in plans:
            rows.append(
                {
                    "run_id": plan.run_id,
                    "project_id": plan.project_id,
                    "asset_type": plan.asset_type,
                    "resource_name": plan.resource_name,
                    "missing_labels": json.dumps(
                        plan.missing_labels
                    ),
                    "planned_labels": json.dumps(
                        plan.planned_labels
                    ),
                    "planned_tags": json.dumps(
                        plan.planned_tags
                    ),
                    "status": plan.status,
                    "created_at": (
                        plan.created_at.isoformat()
                    ),
                }
            )

        errors = self.client.insert_rows_json(
            self.table_id,
            rows,
        )

        if errors:
            logger.error(
                "Failed writing remediation plan: %s",
                errors,
            )
            raise RuntimeError(
                "Failed to persist remediation plan."
            )

        logger.info(
            "Stored %d remediation plans",
            len(rows),
        )

        return len(rows)

    def get_planned(
        self,
        run_id: str,
    ) -> list[RemediationPlan]:
        """
        Returns all remediation actions that are still
        in the PLANNED state.
        """
        query = f"""
        SELECT *
        FROM `{self.table_id}`
        WHERE run_id = @run_id
        AND status = 'PLANNED'
        ORDER BY created_at
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

        plans = []
        for row in job.result():
            plans.append(
                RemediationPlan(
                    run_id=row.run_id,
                    project_id=row.project_id,
                    asset_type=row.asset_type,
                    resource_name=row.resource_name,
                    missing_labels=self._json_value(
                        row.missing_labels
                    ),
                    planned_labels=self._json_value(
                        row.planned_labels
                    ),
                    planned_tags=self._json_value(
                        row.planned_tags
                    ),
                    status=row.status,
                    created_at=row.created_at,
                )
            )
        return plans

    def get_planned_batch(
        self,
        run_id: str,
        offset: int,
        batch_size: int,
    ) -> list[RemediationPlan]:
        """
        Returns one batch of planned remediation actions.
        """

        query = f"""
        SELECT *
        FROM `{self.table_id}`
        WHERE run_id = @run_id
        AND status = 'PLANNED'
        ORDER BY created_at
        LIMIT @batch_size
        OFFSET @offset
        """

        job = self.client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "run_id",
                        "STRING",
                        run_id,
                    ),
                    bigquery.ScalarQueryParameter(
                        "batch_size",
                        "INT64",
                        batch_size,
                    ),
                    bigquery.ScalarQueryParameter(
                        "offset",
                        "INT64",
                        offset,
                    ),
                ]
            ),
        )

        plans = []

        for row in job.result():
            plans.append(
                RemediationPlan(
                    run_id=row.run_id,
                    project_id=row.project_id,
                    asset_type=row.asset_type,
                    resource_name=row.resource_name,
                    missing_labels=self._json_value(
                        row.missing_labels
                    ),
                    planned_labels=self._json_value(
                        row.planned_labels
                    ),
                    planned_tags=self._json_value(
                        row.planned_tags
                    ),
                    status=row.status,
                    created_at=row.created_at,
                )
            )

        return plans

    def update_status(
        self,
        run_id: str,
        resource_name: str,
        status: str,
    ):
        """
        Status updates are intentionally disabled.

        BigQuery does not allow UPDATEs against rows still in the
        streaming buffer. Execution status is recorded in the
        remediation_execution table instead.
        """

        logger.info(
            "Skipping remediation_plan update for %s -> %s",
            resource_name,
            status,
        )

    def reset_in_progress(
        self,
        run_id: str,
    ):
        """
        Disabled.

        Recovery is handled from remediation_execution.
        """

        logger.info(
            "Skipping remediation recovery for run %s",
            run_id,
        )

    def count_by_status(
        self,
        run_id: str,
    ) -> dict:
        """
        Returns remediation counts grouped by status.
        """

        query = f"""
        SELECT
            status,
            COUNT(*) AS total
        FROM `{self.table_id}`
        WHERE run_id = @run_id
        GROUP BY status
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

        counts = {}

        for row in job.result():
            counts[row.status] = row.total

        return counts

    def mark_in_progress(
        self,
        run_id: str,
        resource_name: str,
    ):
        """
        Marks a remediation action as IN_PROGRESS.
        """

        self.update_status(
            run_id=run_id,
            resource_name=resource_name,
            status="IN_PROGRESS",
        )

    def mark_success(
        self,
        run_id: str,
        resource_name: str,
    ):
        """
        Marks a remediation action as SUCCESS.
        """

        self.update_status(
            run_id=run_id,
            resource_name=resource_name,
            status="SUCCESS",
        )

    def mark_failed(
        self,
        run_id: str,
        resource_name: str,
    ):
        """
        Marks a remediation action as FAILED.
        """

        self.update_status(
            run_id=run_id,
            resource_name=resource_name,
            status="FAILED",
        )