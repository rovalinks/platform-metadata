import json
import config
from google.cloud import bigquery
from datetime import datetime

class LabelOwnershipRepository:
    """
    Persists platform ownership information.

    One row exists per resource.
    """

    def __init__(self):
        self.client = bigquery.Client()
        self.dataset = config.BIGQUERY_DATASET
        self.table = "label_ownership"

    @property
    def table_id(self):
        return f"{self.dataset}.{self.table}"

    def load(
        self,
        resource_name: str,
    ) -> tuple[list[str], list[str]]:
        """
        Returns previously managed labels and tags.
        """

        query = f"""
        SELECT
            managed_labels,
            managed_tags
        FROM `{self.table_id}`
        WHERE resource_name = @resource_name
        LIMIT 1
        """

        job = self.client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "resource_name",
                        "STRING",
                        resource_name,
                    )
                ]
            ),
        )

        row = next(job.result(), None)

        if row is None:
            return [], []

        managed_labels = (
            row.managed_labels
            if isinstance(
                row.managed_labels,
                list,
            )
            else json.loads(
                row.managed_labels or "[]"
            )
        )

        managed_tags = (
            row.managed_tags
            if isinstance(
                row.managed_tags,
                list,
            )
            else json.loads(
                row.managed_tags or "[]"
            )
        )

        return managed_labels, managed_tags

    def exists(
        self,
        resource_name: str,
    ) -> bool:

        query = f"""
        SELECT COUNT(*) AS total
        FROM `{self.table_id}`
        WHERE resource_name = @resource_name
        """

        job = self.client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "resource_name",
                        "STRING",
                        resource_name,
                    )
                ]
            ),
        )

        row = next(job.result())

        return row.total > 0

    def save(
        self,
        resource_name: str,
        managed_labels: list[str],
        managed_tags: list[str],
    ):
        """
        Inserts a new ownership record or updates
        an existing one.
        """

        if self.exists(resource_name):
            self._update(
                resource_name,
                managed_labels,
                managed_tags,
            )
        else:
            self._insert(
                resource_name,
                managed_labels,
                managed_tags,
            )

    def _insert(
        self,
        resource_name: str,
        managed_labels: list[str],
        managed_tags: list[str],
    ):

        errors = self.client.insert_rows_json(
            self.table_id,
            [
                {
                    "resource_name": resource_name,
                    "managed_labels": json.dumps(managed_labels),
                    "managed_tags": json.dumps(managed_tags),
                    "updated_at": datetime.utcnow().isoformat(),
                }
            ],
        )

        if errors:
            raise RuntimeError(errors)

    def _update(
        self,
        resource_name: str,
        managed_labels: list[str],
        managed_tags: list[str],
    ):

        query = f"""
        UPDATE `{self.table_id}`
        SET
            managed_labels = @managed_labels,
            managed_tags = @managed_tags,
            updated_at = CURRENT_TIMESTAMP()
        WHERE resource_name = @resource_name
        """

        self.client.query(
            query,
            job_config=bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter(
                        "resource_name",
                        "STRING",
                        resource_name,
                    ),
                    bigquery.ScalarQueryParameter(
                        "managed_labels",
                        "JSON",
                        json.dumps(
                            managed_labels
                        ),
                    ),
                    bigquery.ScalarQueryParameter(
                        "managed_tags",
                        "JSON",
                        json.dumps(
                            managed_tags
                        ),
                    ),
                ]
            ),
        ).result()