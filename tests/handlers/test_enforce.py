import pytest
from unittest.mock import patch
from cloudrun.handlers.enforce import enforce_compliance
from cloudrun.models.resource_event import CAIEventPayload, Asset, AssetResource, ResourceData

# Point the patch to the new LabelService class we just created
@patch('cloudrun.handlers.enforce.LabelService.update_labels')
def test_enforce_compliance_safely_skips_terraform(mock_update_labels):
    
    mock_event = CAIEventPayload(
        asset=Asset(
            name="//compute.googleapis.com/projects/my-project/zones/us-central1-a/instances/tf-instance",
            assetType="compute.googleapis.com/Instance",
            resource=AssetResource(
                data=ResourceData(
                    labels={"provisioned-by": "terraform"}
                )
            )
        ),
        deleted=False
    )
    
    mock_app_record = {"auto_remediate": True, "owner": "platform-team"}
    
    enforce_compliance(mock_event, mock_app_record, "Public IP detected")
    
    # Assert the correct method was called
    mock_update_labels.assert_called_once_with(
        asset_name="//compute.googleapis.com/projects/my-project/zones/us-central1-a/instances/tf-instance",
        labels={
            "compliance-status": "violation",
            "violation-detail": "Public IP detected",
            "action-required": "true"
        }
    )