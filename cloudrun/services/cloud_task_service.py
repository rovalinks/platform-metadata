import json
import google.auth
from google.cloud import tasks_v2
from google.api_core import retry

import config
from utils.logger import logger

class CloudTaskService:
    """
    Creates Cloud Tasks for asynchronous operations.
    """

    def __init__(self):
        # --- Diagnostic Logging ---
        credentials, project = google.auth.default()
        logger.info("ADC project: %s", project)
        logger.info("ADC credentials: %s", type(credentials).__name__)
        logger.info(
            "ADC service account: %s",
            getattr(credentials, "service_account_email", "UNKNOWN"),
        )
        # --------------------------

        self.client = tasks_v2.CloudTasksClient()
        self.parent = self.client.queue_path(
            config.PROJECT_ID,
            config.REGION,
            config.TASK_QUEUE,
        )

    @retry.Retry()
    def enqueue_remediation_batch(
        self,
        run_id: str,
        batch_number: int,
        total_batches: int,
        offset: int,
        batch_size: int,
    ):
        """
        Creates a task for a specific remediation batch.
        """
        payload = json.dumps(
            {
                "run_id": run_id,
                "batch_number": batch_number,
                "total_batches": total_batches,
                "offset": offset,
                "batch_size": batch_size,
            }
        ).encode()

        task = {
            "http_request": {
                "http_method": tasks_v2.HttpMethod.POST,
                "url": f"{config.CLOUD_RUN_URL}/worker",
                "headers": {"Content-Type": "application/json"},
                "oidc_token": {
                    "service_account_email": config.SERVICE_ACCOUNT_EMAIL
                },
                "body": payload,
            }
        }

        # --- Diagnostic Logging ---
        logger.info("Cloud Tasks parent: %s", self.parent)
        logger.info("Runtime PROJECT_ID: %s", config.PROJECT_ID)
        logger.info("Runtime REGION: %s", config.REGION)
        logger.info("Runtime TASK_QUEUE: %s", config.TASK_QUEUE)
        logger.info("Runtime Service Account: %s", config.SERVICE_ACCOUNT_EMAIL)
        logger.info("Task URL: %s", task["http_request"]["url"])
        # --------------------------

        return self.client.create_task(
            parent=self.parent,
            task=task,
        )
