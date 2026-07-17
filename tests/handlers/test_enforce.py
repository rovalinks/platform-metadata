import pytest
from unittest.mock import patch
from handlers.enforce import enforce_compliance
from models.resource_event import CAIEventPayload, Asset, AssetResource, ResourceData

# 1. Patch the reporting function so we don't hit BigQuery during this test
@patch('handlers.enforce.log_compliance_evaluation')
# 2. Patch the LabelService
@patch('handlers.enforce.LabelService.update_labels')
def test_enforce_compliance_safely_skips_terraform(mock_update_labels, mock_log_compliance):
    
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
    
    # Assert the correct method was called with ALL arguments
    mock_update_labels.assert_called_once_with(
        asset_name="//compute.googleapis.com/projects/my-project/zones/us-central1-a/instances/tf-instance",
        asset_type="compute.googleapis.com/Instance",  # <-- ADDED THIS LINE
        labels={
            "compliance-status": "violation",
            "violation-detail": "Public IP detected",
            "action-required": "true"
        }
    )
    
    # Assert that the reporting function was also called
    mock_log_compliance.assert_called_once()