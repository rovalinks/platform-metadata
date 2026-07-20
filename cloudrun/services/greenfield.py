import time
import base64
import json
from utils.logger import logger

from services.adapter import AdapterService
from services.capability import CapabilityService
from services.classification import ClassificationService
from services.compliance import ComplianceService
from services.discovery import DiscoveryService
from services.executor import ExecutorService
from services.governance import GovernanceService
from repositories.execution_repository import ExecutionRepository

class GreenfieldService:
    """Handles real-time governance for newly created GCP resources."""

    def __init__(self):
        self.classification = ClassificationService()
        self.adapters = AdapterService()
        self.discovery = DiscoveryService()
        self.compliance = ComplianceService()
        self.governance = GovernanceService()
        self.executor = ExecutorService()
        self.capability = CapabilityService()
        self.execution_repository = ExecutionRepository()

    def _record_execution(self, audit_event: dict, asset_type: str, status: str, duration_ms: int, error_message: str = None):
        self.execution_repository.save(
            run_id="GREENFIELD",
            project_id=audit_event.get("project_id", "UNKNOWN"),
            asset_type=asset_type,
            resource_name=audit_event.get("resource_name", "UNKNOWN"),
            status=status,
            execution_mode="GREENFIELD",
            duration_ms=duration_ms,
            error_message=error_message
        )

    def process(self, raw_payload: dict):
        start = time.perf_counter()
        
        # 1. FOOLPROOF UNWRAPPING (Decodes the Pub/Sub envelope safely)
        try:
            message = raw_payload.get("message", {})
            data_b64 = message.get("data")
            if not data_b64:
                logger.error("No base64 data found in payload. Ignoring.")
                return {"status": "unsupported"}
                
            data_str = base64.b64decode(data_b64).decode("utf-8")
            audit_log = json.loads(data_str)
        except Exception as e:
            logger.exception("Failed to decode Pub/Sub message")
            return {"status": "error", "error": str(e)}

        # 2. EXTRACT CORE FIELDS FROM AUDIT LOG
        proto = audit_log.get("protoPayload", {})
        service_name = proto.get("serviceName")
        
        # Extract project_id securely (Handles both Org and Project Sinks)
        project_id = audit_log.get("resource", {}).get("labels", {}).get("project_id")
        if not project_id:
            res_name = audit_log.get("resourceName", "")
            if "projects/" in res_name:
                try: 
                    parts = res_name.split("/")
                    project_id = parts[parts.index("projects") + 1]
                except: 
                    pass
        if not project_id:
            project_id = "UNKNOWN_PROJECT"

        # 3. BUILD THE CLEAN EVENT DICTIONARY
        audit_event = {
            "service_name": service_name,
            "method_name": proto.get("methodName"),
            "project_id": project_id,
            "resource_name": audit_log.get("resourceName") or proto.get("resourceName") or "UNKNOWN",
            "raw_payload": audit_log
        }
        
        # 4. EXECUTE PIPELINE
        try:
            # Pass the clean dictionary to the classifier we built earlier
            resources = self.classification.classify(audit_event)
            
            if not resources:
                self._record_execution(audit_event, "UNKNOWN", "UNSUPPORTED", int((time.perf_counter() - start) * 1000))
                return {"status": "unsupported"}

            batch_results = []
            
            # Loop through all resources (Instance + Child Disks)
            for resource in resources:
                resource_start = time.perf_counter()
                resource.project = project_id
                
                # Check Compliance
                compliance_results = self.compliance.evaluate([resource])
                if compliance_results and compliance_results[0].compliant:
                    self._record_execution(audit_event, resource.asset_type, "COMPLIANT", int((time.perf_counter() - resource_start) * 1000))
                    batch_results.append({"resource": resource.name, "status": "compliant"})
                    continue

               # Remediate (Updated to match your exact governance.py)
                labels = self.governance.expected_labels(resource.project) if self.capability.supports_labels(resource.asset_type) else {}
                tags = {} if self.capability.supports_labels(resource.asset_type) else self.governance.expected_tags(resource.project)
                
                result = self.executor._execute_single_action({
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
            logger.exception("Greenfield execution failed")
            self._record_execution(audit_event, "UNKNOWN", "FAILED", duration_ms, str(exc))
            return {"status": "failed", "error": str(exc)}