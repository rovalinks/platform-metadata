import json
from datetime import datetime
from google.cloud import bigquery
from utils.logger import logger
from config import BIGQUERY_DATASET

class SnapshotService:
    """Persists and retrieves governance snapshots."""

    def __init__(self, run_id):
        self.client = bigquery.Client()
        self.dataset = BIGQUERY_DATASET
        self.resource_table = "resource_snapshot"
        self.compliance_table = "compliance_snapshot"
        self.run_id = run_id

    def save_resources(self, resources):
        """Persists resource inventory with serialized JSON strings."""
        rows_to_insert = []
        for resource in resources:
            rows_to_insert.append({
                "run_id": self.run_id,
                "snapshot_time": datetime.utcnow().isoformat(),
                "project_id": resource.project_id,
                "asset_type": resource.asset_type,
                "resource_name": resource.name,
                "location": resource.location,
                # Explicit serialization to STRING for cross-platform compatibility
                "labels": json.dumps(resource.labels or {}),
                "tags": json.dumps(resource.tags or {}),
            })
        
        errors = self.client.insert_rows_json(
            f"{self.dataset}.{self.resource_table}", 
            rows_to_insert
        )
        if errors:
            logger.error(f"Errors inserting resources: {errors}")

    def save_compliance(self, results):
        """Persists compliance results with serialized JSON strings."""
        rows_to_insert = []
        for res in results:
            rows_to_insert.append({
                "run_id": self.run_id,
                "evaluated_time": datetime.utcnow().isoformat(),
                "project_id": res.project_id,
                "asset_type": res.asset_type,
                "resource_name": res.resource_name,
                "compliant": res.compliant,
                # Serializing lists/dicts to STRING
                "missing_labels": json.dumps(res.missing_labels or []),
                "incorrect_labels": json.dumps(res.incorrect_labels or {}),
            })
            
        errors = self.client.insert_rows_json(
            f"{self.dataset}.{self.compliance_table}", 
            rows_to_insert
        )
        if errors:
            logger.error(f"Errors inserting compliance data: {errors}")