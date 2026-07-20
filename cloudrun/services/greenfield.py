import time
import base64
import json
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
        audit_event: dict,
        asset_type: str,
        status: str,
        duration_ms: int,
        error_message: str | None = None,
    ):
        self.execution_repository.save(
            run_id="GREENFIELD",
            project_id=audit_event.get("project_id"),
            asset_type=asset_type,
            resource_name=audit_event.get("resource_name", "UNKNOWN"),
            status=status,
            execution_mode="GREENFIELD",
            duration_ms=duration_ms,
            error_message=error_message
        )

    def process(self, audit_event: dict):
        import time
        start = time.perf_counter()
        project_id = audit_event.get("project_id")
        
        try:
            # Now returns a list containing parent + all implicit children
            resources = self.classification.classify(audit_event)
            
            if not resources:
                self._record_execution(audit_event, "UNKNOWN", "UNSUPPORTED", int((time.perf_counter() - start) * 1000))
                return {"status": "unsupported"}

            batch_results = []

            for resource in resources:
                resource_start = time.perf_counter()
                resource.project = project_id
                
                # Check Compliance
                compliance_results = self.compliance.evaluate([resource])
                if compliance_results and compliance_results[0].compliant:
                    self._record_execution(audit_event, resource.asset_type, "COMPLIANT", int((time.perf_counter() - resource_start) * 1000))
                    batch_results.append({"resource": resource.name, "status": "compliant"})
                    continue

                # Execute Remediation
                labels = self.governance.expected_labels(resource.project) if self.capability.supports_labels(resource.asset_type) else {}
                tags = {} if self.capability.supports_labels(resource.asset_type) else self.governance.expected_tags(resource.project)
                
                app_metadata = self.governance.get_application_for_resource(resource.project, resource)
                if app_metadata:
                    labels.update(self.governance._extract_labels(app_metadata, {}))
                
                result = self.executor.execute_single_action({
                    "resource": resource.name,
                    "asset_type": resource.asset_type,
                    "labels": labels,
                    "tags": tags
                })
                
                self._record_execution(audit_event, resource.asset_type, "SUCCESS", int((time.perf_counter() - resource_start) * 1000))
                batch_results.append({"resource": resource.name, "status": "remediated", "result": result})

            return {"status": "processed", "results": batch_results}

        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            from utils.logger import logger
            logger.exception("Greenfield execution failed")
            self._record_execution(audit_event, "UNKNOWN", "FAILED", duration_ms, str(exc))
            return {"status": "failed", "error": str(exc)}