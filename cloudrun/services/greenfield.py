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
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
from services.notification_service import NotificationService

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
        self.notifications = NotificationService()

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
                # DO NOT save unsupported resources to the database to prevent bloat
                return {"status": "unsupported"}

            batch_results = []
            
            # Loop through all resources (Instance + Child Disks)
            for resource in resources:

                # ---> ADDING THIS GATEKEEPER <---
                if resource.asset_type not in SUPPORTED_LABEL_RESOURCES and resource.asset_type not in SUPPORTED_TAG_RESOURCES:
                    logger.info("Skipping Greenfield execution: %s is not in supported lists.", resource.asset_type)
                    batch_results.append({"resource": resource.name, "status": "unsupported"})
                    continue
                # -----------------------------

                resource_start = time.perf_counter()
                resource.project = project_id
                
                # ---> NEW SEED LABEL LOGIC (ENFORCING 'product') <---
                # 1. Try to get labels from the resource object
                developer_labels = getattr(resource, 'labels', {})
                
                # 2. If empty, dig into the GCP Audit Log API Request to find what the user typed
                if not developer_labels:
                    req_payload = audit_event.get("raw_payload", {}).get("protoPayload", {}).get("request", {})
                    
                    # Most APIs (like Compute Engine) put labels directly in the request
                    developer_labels = req_payload.get("labels", {})
                    
                    # Fallback for APIs that nest it deeper (like Storage/PubSub)
                    if not developer_labels:
                        for key, value in req_payload.items():
                            if isinstance(value, dict) and "labels" in value:
                                developer_labels = value.get("labels", {})
                                break

                # ---> THE LIST FIX <---
                # If Google formatted the labels as a list of dicts, convert them back!
                if isinstance(developer_labels, list):
                    developer_labels = {item.get("key"): item.get("value") for item in developer_labels if isinstance(item, dict)}
                # ----------------------
                
                seed_value = developer_labels.get("product")

                # Enforce mandatory 'product' label
                if not seed_value:
                    logger.warning(f"Resource {resource.name} is missing the mandatory 'product' seed label!")
                    
                    self._record_execution(audit_event, resource.asset_type, "FAILED", int((time.perf_counter() - resource_start) * 1000), "Missing mandatory 'product' label")
                    
                    # ---> FIRE THE ALERT HERE <---
                    # We extract the caller's email directly from the Google Cloud Audit Log!
                    caller_email = audit_event.get("raw_payload", {}).get("protoPayload", {}).get("authenticationInfo", {}).get("principalEmail", "Unknown User")
                    self.notifications.send_missing_label_alert(resource.name, project_id, caller_email)
                    
                    batch_results.append({"resource": resource.name, "status": "skipped", "reason": "Missing seed label: product"})
                    continue

                # Check Compliance
                compliance_results = self.compliance.evaluate([resource])
                if compliance_results and compliance_results[0].compliant:
                    self._record_execution(audit_event, resource.asset_type, "COMPLIANT", int((time.perf_counter() - resource_start) * 1000))
                    batch_results.append({"resource": resource.name, "status": "compliant"})
                    continue

                # ---> TWO-KEY LOOKUP LOGIC <---
                # Remediate (Uses the 'project' ID AND the 'product' seed value)
                labels = self.governance.expected_labels(resource.project, seed_value, resource.asset_type) if self.capability.supports_labels(resource.asset_type) else {}
                tags = {} if self.capability.supports_labels(resource.asset_type) else self.governance.expected_tags(resource.project, seed_value, resource.asset_type)
                
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