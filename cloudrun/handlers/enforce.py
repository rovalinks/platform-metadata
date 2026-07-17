import logging
from models.resource_event import CAIEventPayload
from services.label_service import LabelService
from services.reporting import log_compliance_evaluation # <-- Add this import

logger = logging.getLogger(__name__)
label_service = LabelService()

def enforce_compliance(event: CAIEventPayload, app_record: dict, violation_detail: str):
    asset_name = event.asset.name
    
    logger.info(f"Applying violation label to {asset_name}")
    try:
        label_service.update_labels(
            asset_name=asset_name,
            asset_type=event.asset.assetType,
            labels={
                "compliance-status": "violation",
                "violation-detail": violation_detail,
                "action-required": "true"
            }
        )
        
        # Stream the violation event to BigQuery for Looker Studio
        log_compliance_evaluation(
            event=event,
            app_record=app_record,
            status="VIOLATION",
            violation_detail=violation_detail
        )
        
    except Exception as e:
        logger.error(f"Failed to apply label to {asset_name}: {e}")

    # ... (Keep your Terraform and auto_remediate safety checks below) ...

    # 2. Safety Check: Determine if we are allowed to change the actual configuration
    is_tf_labeled = event.is_terraform_managed
    
    # We check the app's YAML registry entry to see if auto-remediation is explicitly enabled
    registry_allows_remediation = app_record.get('auto_remediate', False)

    if is_tf_labeled:
        logger.info(f"Asset {asset_name} is marked as Terraform. Skipping configuration changes.")
        return

    if not registry_allows_remediation:
        logger.info(
            f"Asset {asset_name} lacks TF label, BUT 'auto_remediate' is not True "
            f"in app registry. Assuming it might be TF. Skipping configuration changes."
        )
        return

    # 3. Auto-Remediate (Only executes if opt-in is True AND TF label is absent)
    logger.warning(f"Auto-remediation approved and executing for {asset_name}!")
    # fix_resource_config(event, violation_detail)

    # In enforce.py
    def enforce():
        return enforce_compliance()