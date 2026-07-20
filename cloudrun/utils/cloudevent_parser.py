import base64
import json
from utils.logger import logger

class CloudEventParser:
    """Parses incoming Eventarc/PubSub messages into a standard dictionary."""

    @staticmethod
    def parse(request_payload: dict) -> dict:
        """
        Unwraps the Pub/Sub message and extracts core audit fields.
        Returns a dictionary to be passed to the ClassificationService.
        """
        try:
            # 1. Unwrap the Pub/Sub base64 payload
            message = request_payload.get("message", {})
            data_b64 = message.get("data")
            
            if not data_b64:
                logger.error("No data payload found in Pub/Sub message.")
                return {}

            data_str = base64.b64decode(data_b64).decode("utf-8")
            audit_log = json.loads(data_str)

            # 2. Extract the core protoPayload
            proto_payload = audit_log.get("protoPayload", {})
            
            # 3. Extract the critical routing fields
            service_name = proto_payload.get("serviceName")
            method_name = proto_payload.get("methodName")
            
            # Org-level sinks sometimes put the resource name at the root, sometimes in protoPayload
            resource_name = audit_log.get("resourceName") or proto_payload.get("resourceName", "UNKNOWN")
            
            # Extract project_id securely (Check labels first, then fallback to parsing the resource name)
            project_id = None
            resource_labels = audit_log.get("resource", {}).get("labels", {})
            if "project_id" in resource_labels:
                project_id = resource_labels["project_id"]
            elif "projects/" in resource_name:
                # Extract project_id from strings like "projects/my-project/zones/..."
                parts = resource_name.split("/")
                try:
                    project_id = parts[parts.index("projects") + 1]
                except ValueError:
                    pass

            if not project_id:
                logger.error(f"Could not determine project_id from event. Resource: {resource_name}")
                project_id = "UNKNOWN_PROJECT"

            logger.info(f"Parsed Event -> Service: {service_name}, Method: {method_name}, Project: {project_id}")

            # 4. Return the standardized dictionary
            return {
                "service_name": service_name,
                "method_name": method_name,
                "resource_name": resource_name,
                "project_id": project_id,
                "raw_payload": audit_log # Pass the whole thing so Extractors can dig into it
            }

        except Exception as e:
            logger.exception("Failed to parse CloudEvent payload.")
            return {}