import json
import config
from google.cloud import bigquery
from datetime import datetime

class LabelOwnershipRepository:
    """
    Persists platform ownership information using an append-only pattern.

    Every save operation inserts a new row. The 'load' method fetches 
    the most recent record for a given resource.
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
        Returns the most recent managed labels and tags.
        """

        # Append-only fix: Fetch only the latest record based on updated_at
        query = f"""
        SELECT
            managed_labels,
            managed_tags
        FROM `{self.table_id}`
        WHERE resource_name = @resource_name
        ORDER BY updated_at DESC
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
            if isinstance(row.managed_labels, list)
            else json.loads(row.managed_labels or "[]")
        )

        managed_tags = (
            row.managed_tags
            if isinstance(row.managed_tags, list)
            else json.loads(row.managed_tags or "[]")
        )

        return managed_labels, managed_tags

    def save(
        self,
        resource_name: str,
        managed_labels: list[str],
        managed_tags: list[str],
    ):
        """
        Always inserts a new record. 
        Updates are handled by appending new state.
        """
        
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
            raise RuntimeError(f"Failed to insert ownership record: {errors}")

    # Note: exists, _insert, and _update methods are no longer needed
    # and have been removed to prevent future usage of UPDATE operations.