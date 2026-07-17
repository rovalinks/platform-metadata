import json
import base64
from models.resource_event import CAIEventPayload

def parse_pubsub_message(envelope: dict) -> CAIEventPayload:
    """
    Parses a Pub/Sub envelope triggered by a Cloud Asset Inventory feed,
    decodes the base64 data, and validates it against the CAIEventPayload model.
    """
    if not envelope or 'message' not in envelope:
        raise ValueError("Invalid Pub/Sub envelope format: Missing 'message' key.")
        
    pubsub_message = envelope['message']
    
    if 'data' not in pubsub_message:
        raise ValueError("Pub/Sub message is missing the 'data' payload.")
        
    try:
        decoded_data = base64.b64decode(pubsub_message['data']).decode('utf-8')
        raw_payload = json.loads(decoded_data)
        return CAIEventPayload(**raw_payload)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse decoded Pub/Sub data as JSON: {e}")

# THIS MUST BE AT THE ROOT LEVEL (NOT INDENTED)
class CloudEventParser:
    @staticmethod
    def parse(event: dict):
        return parse_pubsub_message(event)