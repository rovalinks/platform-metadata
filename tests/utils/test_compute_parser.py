import json
import base64
import pytest
from utils.cloudevent_parser import parse_pubsub_message

def test_parse_valid_cai_pubsub_message():
    """
    Tests that our parser correctly unpacks a base64 Pub/Sub envelope
    and maps the CAI data to our Pydantic models.
    """
    # 1. Define the raw CAI event (what CAI actually generates)
    raw_cai_event = {
        "asset": {
            "name": "//compute.googleapis.com/projects/my-project/zones/us-central1-a/instances/my-instance",
            "assetType": "compute.googleapis.com/Instance",
            "resource": {
                "data": {
                    "labels": {
                        "app_id": "APP000001",
                        "provisioned-by": "terraform"
                    },
                    "machineType": "n1-standard-1"
                }
            }
        },
        "deleted": False
    }

    # 2. Encode it exactly how Pub/Sub wraps messages before sending via HTTP Push
    encoded_data = base64.b64encode(json.dumps(raw_cai_event).encode('utf-8')).decode('utf-8')
    
    mock_pubsub_envelope = {
        "message": {
            "data": encoded_data,
            "messageId": "1234567890",
            "publishTime": "2026-07-17T20:28:46Z"
        }
    }

    # 3. Execute the function we are testing
    parsed_event = parse_pubsub_message(mock_pubsub_envelope)

    # 4. Assertions: Prove our Pydantic properties work perfectly
    assert parsed_event.asset.name == "//compute.googleapis.com/projects/my-project/zones/us-central1-a/instances/my-instance"
    assert parsed_event.asset.assetType == "compute.googleapis.com/Instance"
    assert parsed_event.deleted is False
    
    # Prove our helper properties extracted the labels correctly
    assert parsed_event.app_id == "APP000001"
    assert parsed_event.is_terraform_managed is True