import logging
from datetime import datetime, timezone
from clients.bigquery import BigQueryClient
from models.resource_event import CAIEventPayload

logger = logging.getLogger(__name__)

# Initialize your custom BigQuery client
bq_client = BigQueryClient()

# These should ideally be set in your environment variables / config
DATASET_ID = "governance_metrics"
TABLE_ID = "compliance_log"

def log_compliance_evaluation(event: CAIEventPayload, app_record: dict, status: str, violation_detail: str = ""):
    """
    Streams the compliance evaluation result to BigQuery for dashboard reporting.
    """
    try:
        # Construct the row matching your BigQuery schema
        row_to_insert = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "app_id": event.app_id,
            "team_owner": app_record.get("owner", "unassigned"), # Pulled from the YAML registry
            "resource_name": event.asset.name,
            "resource_type": event.asset.assetType,
            "provisioning_method": "terraform" if event.is_terraform_managed else "manual/cli",
            "compliance_status": status,  # e.g., "COMPLIANT" or "VIOLATION"
            "violation_detail": violation_detail
        }
        
        # Stream the data into BigQuery
        # (Assuming your custom BigQuery client has a method like 'insert_rows' or 'stream_data')
        bq_client.insert_rows(DATASET_ID, TABLE_ID, [row_to_insert])
        
        logger.info(f"Successfully logged {status} status for {event.asset.name} to BigQuery.")
        
    except Exception as e:
        # We catch the exception so a reporting failure doesn't crash the actual enforcement loop
        logger.error(f"Failed to write compliance log to BigQuery: {e}")