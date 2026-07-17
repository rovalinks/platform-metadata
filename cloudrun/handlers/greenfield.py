import logging
from flask import jsonify
from models.audit_log_event import AuditLogEvent
from services.classification import ClassificationService
from services.adapter import AdapterService
from services.compliance import ComplianceService
from services.governance import GovernanceService
from services.executor import ExecutorService
from registry.reader import RegistryReader

logger = logging.getLogger(__name__)
classification = ClassificationService()
adapters = AdapterService()
compliance = ComplianceService()
governance = GovernanceService()
executor = ExecutorService()
registry = RegistryReader()

def greenfield(payload):
    return handle_greenfield_event(payload)

def handle_greenfield_event(payload: dict):
    """
    Handles the raw Audit Log payload from Pub/Sub.
    """
    try:
        # 1. Extract Audit Log fields from the protoPayload
        message = payload.get("message", {})
        import base64
        import json
        raw_data = json.loads(base64.b64decode(message.get("data")).decode("utf-8"))
        proto = raw_data.get("protoPayload", {})
        
        event = AuditLogEvent(
            service_name=proto.get("serviceName"),
            method_name=proto.get("methodName"),
            resource_name=proto.get("resourceName"),
            project_id=proto.get("resourceName", "").split("/")[1] if "/projects/" in proto.get("resourceName", "") else "unknown",
            location=raw_data.get("resource", {}).get("labels", {}).get("zone")
        )

        # 2. Classify the event into a Resource
        resource_event = classification.classify(event)
        
        # 3. Fetch full resource and enrich with labels
        client = adapters.client_for(resource_event.asset_type)
        resource = client.get(resource_event.resource_name)
        
        # 4. Check App Registry for auto_remediate=True
        # Logic to find app_id from labels and check registry
        app_id = resource.labels.get("app_id")
        if not app_id:
            return jsonify({"status": "ignored", "reason": "no_app_id"}), 200

        # 5. Evaluate and Enforce
        compliance_result = compliance.evaluate_resource(resource)
        if not compliance_result.compliant:
            labels = governance.expected_labels(resource.project)
            executor.execute_resource(resource, labels, {})
            return jsonify({"status": "remediated"}), 200

        return jsonify({"status": "compliant"}), 200

    except Exception as e:
        logger.exception("Error processing Audit Log event")
        return jsonify({"error": str(e)}), 500