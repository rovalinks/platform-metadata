from models.audit_log_event import AuditLogEvent
from utils.logger import logger


class CloudEventParser:
    """
    Converts a Google Cloud Event into the
    internal AuditLogEvent model.
    """

    @staticmethod
    def parse(
        event: dict,
    ) -> AuditLogEvent:

        payload = event.get(
            "protoPayload",
            {}
        )

        resource_name = payload.get(
            "resourceName",
            "",
        )

        service_name = payload.get(
            "serviceName",
            "",
        )

        method_name = payload.get(
            "methodName",
            "",
        )

        #
        # Cloud SQL create events sometimes emit only the
        # project as the resource name. Attempt to build
        # the full instance resource.
        #
        if (
            service_name == "cloudsql.googleapis.com"
            and resource_name.count("/") == 1
        ):

            response = payload.get(
                "response",
                {}
            )

            request = payload.get(
                "request",
                {}
            )

            instance = (
                response.get("name")
                or response.get("instance")
                or response.get("targetId")
                or request.get("name")
                or request.get("instance")
            )

            if instance:

                resource_name = (
                    f"{resource_name}/instances/{instance}"
                )

                logger.info(
                    "Normalized Cloud SQL resource to %s",
                    resource_name,
                )
            else:

                logger.warning(
                    "Unable to determine Cloud SQL instance name."
                )

        resource = event.get(
            "resource",
            {}
        )

        labels = resource.get(
            "labels",
            {}
        )

        return AuditLogEvent(

            service_name=service_name,

            method_name=method_name,

            resource_name=resource_name,

            project_id=labels.get(
                "project_id",
                "",
            ),

            location=labels.get(
                "location",
            ),
        )