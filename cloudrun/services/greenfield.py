import time
from google.api_core.exceptions import NotFound

from utils.logger import logger
from utils.cloudevent_parser import CloudEventParser

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

        audit_event = CloudEventParser.parse(event)

        logger.info(
            "Greenfield Event | service=%s method=%s project=%s resource=%s",
            audit_event.service_name,
            audit_event.method_name,
            audit_event.project_id,
            audit_event.resource_name,
        )

        try:
            try:
                resource_event = self.classification.classify(audit_event)
            except ValueError as exc:
                duration_ms = int((time.perf_counter() - start) * 1000)
                self._record_execution(
                    audit_event,
                    asset_type="UNSUPPORTED",
                    status="UNSUPPORTED",
                    duration_ms=duration_ms,
                    error_message=str(exc),
                )
                logger.warning("Ignoring unsupported audit event. %s", exc)
                return {"status": "ignored", "service": audit_event.service_name, "method": audit_event.method_name, "resource": audit_event.resource_name}

            logger.info("Classification | asset=%s", resource_event.asset_type)

            client = self.adapters.client_for(resource_event.asset_type)
            if client is None:
                raise RuntimeError(f"No adapter registered for {resource_event.asset_type}")

            try:
                if hasattr(client, "get"):
                    resource = client.get(resource_event.resource_name)
                else:
                    logger.warning("Adapter for %s is missing a '.get()' method!", resource_event.asset_type)
                    resources = self.discovery.discover(resource_event.project_id)
                    resource = next((r for r in resources if r.name == resource_event.resource_name), None)

                if resource is None:
                    raise NotFound("Resource not found")
            except NotFound as exc:
                duration_ms = int((time.perf_counter() - start) * 1000)
                self._record_execution(audit_event, asset_type=resource_event.asset_type, status="NOT_FOUND", duration_ms=duration_ms)
                logger.warning("Resource %s no longer exists.", resource_event.resource_name)
                return {"status": "not_found", "resource": resource_event.resource_name}

            resource.project = resource_event.project_id
            if self.capability.supports_tags(resource.asset_type):
                resource.tags = self.adapters.tag_service.get_tags(resource.name)

            compliance = self.compliance.evaluate([resource])[0]
            duration_ms = int((time.perf_counter() - start) * 1000)

            if compliance.compliant:
                self._record_execution(audit_event, asset_type=resource.asset_type, status="COMPLIANT", duration_ms=duration_ms)
                return {"status": "compliant", "resource": resource.name}

            if self.compliance.capability.supports_labels(resource.asset_type):
                labels, tags = self.governance.expected_labels(resource.project), {}
            else:
                labels, tags = {}, self.governance.expected_tags(resource.project)

            result = self.executor.execute_resource(resource, labels, tags)
            self._record_execution(audit_event, asset_type=resource.asset_type, status="SUCCESS", duration_ms=duration_ms)
            
            return {"status": "remediated", "resource": resource.name, "result": result}

        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            self._record_execution(
                audit_event=audit_event,
                asset_type="UNKNOWN",
                status="FAILED",
                duration_ms=duration_ms,
                error_message=str(exc),
            )
            raise