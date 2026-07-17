import json
import base64
from models.audit_log_event import AuditLogEvent

def parse_pubsub_message(envelope: dict) -> AuditLogEvent:
    """
    Parses a Pub/Sub envelope containing a Cloud Audit Log event.
    """
    if not envelope or 'message' not in envelope:
        raise ValueError("Invalid Pub/Sub envelope format.")
        
    data = json.loads(base64.b64decode(envelope['message']['data']).decode('utf-8'))
    proto = data.get("protoPayload", {})
    
    return AuditLogEvent(
        service_name=data.get("serviceName"),
        method_name=proto.get("methodName"),
        resource_name=proto.get("resourceName"),
        project_id=data.get("resource", {}).get("labels", {}).get("project_id", "unknown"),
        location=data.get("resource", {}).get("labels", {}).get("zone")
    )