from models.audit_log_event import AuditLogEvent
from models.resource_event import ResourceEvent
from services.adapter import AdapterService
from services.capability import CapabilityService


class ResourceResolver:
    """
    Resolves a Cloud Audit Log event into
    a canonical ResourceEvent understood
    by the governance platform.
    """

    def __init__(self):

        self.adapters = AdapterService()

        self.capabilities = (
            CapabilityService()
        )

    def resolve(
        self,
        event: AuditLogEvent,
    ) -> ResourceEvent:

        asset_type = (
            event.service_name
        )

        if not self.capabilities.supports_labels(
            asset_type
        ):
            raise ValueError(
                f"{asset_type} does not support labels."
            )

        return ResourceEvent(

            project_id=event.project_id,

            asset_type=asset_type,

            resource_name=event.resource_name,

            service_name=event.service_name,

            method_name=event.method_name,

            location=event.location,

        )
