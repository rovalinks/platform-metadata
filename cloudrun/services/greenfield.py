import time
import base64
import json
from google.api_core.exceptions import NotFound

from utils.logger import logger
from utils.cloudevent_parser import CloudEventParser # Now this will work!

from services.adapter import AdapterService
from services.capability import CapabilityService
from services.classification import ClassificationService
from services.compliance import ComplianceService
from services.discovery import DiscoveryService
from services.executor import ExecutorService
from services.governance import GovernanceService
from repositories.execution_repository import ExecutionRepository

class GreenfieldService:
    """
    Handles real-time governance for newly
    created GCP resources.
    """

    def __init__(self):
        self.classification = ClassificationService()
        self.adapters = AdapterService()
        self.discovery = DiscoveryService()
        self.compliance = ComplianceService()
        self.governance = GovernanceService()
        self.executor = ExecutorService()
        self.capability = CapabilityService()
        self.execution_repository = ExecutionRepository()

    def _record_execution(
        self,
        audit_event,
        asset_type: str,
        status: str,
        duration_ms: int,
        error_message: str | None = None,
    ):
        self.execution_repository.save(
            run_id="GREENFIELD",
            project_id=audit_event.project_id,
            asset_type=asset_type,
            resource_name=audit_event.resource_name,
            execution_mode="GREENFIELD",
            service_name=audit_event.service_name,
            method_name=audit_event.method_name,
            duration_ms=duration_ms,
            status=status,
            error_message=error_message,
        )

    def process(self, event: dict):
        start = time.perf_counter()
        if isinstance(event, list):
            event = event[0]

        # =====================================================================
        # PUBSUB PAYLOAD UNWRAPPER
        # =====================================================================
        raw_data = None
        if isinstance(event, dict) and "message" in event and isinstance(event["message"], dict) and "data" in event["message"]:
            raw_data = event["message"]["data"]
        elif isinstance(event, dict) and "data" in event and isinstance(event["data"], dict) and "message" in event["data"] and isinstance(event["data"]["message"], dict) and "data" in event["data"]["message"]:
            raw_data = event["data"]["message"]["data"]

        if raw_data:
            try:
                decoded_payload = base64.b64decode(raw_data).decode("utf-8")
                event = json.loads(decoded_payload)
                logger.info("Successfully unwrapped and parsed incoming Pub/Sub CloudEvent.")
            except Exception as exc:
                logger.error("Failed to decode base64 Pub/Sub payload: %s", exc)

        audit_event = CloudEventParser.parse(event)

        try:
            # 1. Classification
            try:
                resource_event = self.classification.classify(audit_event)
            except ValueError as exc:
                self._record_execution(audit_event, "UNSUPPORTED", "UNSUPPORTED", int((time.perf_counter() - start) * 1000), str(exc))
                return {"status": "ignored"}

            # 2. Retrieval
            client = self.adapters.client_for(resource_event.asset_type)
            resource = client.get(resource_event.resource_name) if hasattr(client, "get") else None
            if not resource:
                self._record_execution(audit_event, resource_event.asset_type, "NOT_FOUND", int((time.perf_counter() - start) * 1000))
                return {"status": "not_found"}

            resource.project = resource_event.project_id
            
            # 3. Compliance
            compliance_results = self.compliance.evaluate([resource])
            if not compliance_results:
                self._record_execution(audit_event, resource.asset_type, "SKIPPED", int((time.perf_counter() - start) * 1000))
                return {"status": "skipped"}

            if compliance_results[0].compliant:
                self._record_execution(audit_event, resource.asset_type, "COMPLIANT", int((time.perf_counter() - start) * 1000))
                return {"status": "compliant"}

            # 4. Remediation
            exec_start = time.perf_counter()
            labels = self.governance.expected_labels(resource.project) if self.compliance.capability.supports_labels(resource.asset_type) else {}
            tags = {} if self.compliance.capability.supports_labels(resource.asset_type) else self.governance.expected_tags(resource.project)
            
            result = self.executor.execute_resource(resource, labels, tags)
            
            duration_ms = int((time.perf_counter() - start) * 1000)
            self._record_execution(audit_event, resource.asset_type, "SUCCESS", duration_ms)
            return {"status": "remediated", "result": result}

        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            self._record_execution(audit_event, "UNKNOWN", "FAILED", duration_ms, str(exc))
            raise