from google.cloud import appengine_admin_v1
from google.protobuf.field_mask_pb2 import FieldMask

import config

from clients.base import ResourceClient
from models.resource import Resource
from utils.appengine import parse_name


class AppEngineClient(ResourceClient):
    """App Engine resource adapter."""

    def __init__(self):
        self.applications = appengine_admin_v1.ApplicationsClient()
        self.services = appengine_admin_v1.ServicesClient()
        self.versions = appengine_admin_v1.VersionsClient()

    def supports(
        self,
        asset_type: str,
    ):
        return asset_type in (
            "appengine.googleapis.com/Application",
            "appengine.googleapis.com/Service",
            "appengine.googleapis.com/Version",
        )

    def labels(
        self,
        resource,
    ):
        if (
            resource.asset_type
            == "appengine.googleapis.com/Application"
        ):
            application = self.applications.get_application(
                name=parse_name(resource.name)
            )

            return dict(
                application.labels or {}
            )

        if (
            resource.asset_type
            == "appengine.googleapis.com/Service"
        ):
            service = self.services.get_service(
                name=parse_name(resource.name)
            )

            return dict(
                service.labels or {}
            )

        service_name = (
            parse_name(resource.name)
            .split("/versions/")[0]
        )

        service = self.services.get_service(
            name=service_name
        )

        return dict(
            service.labels or {}
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource:
        project_id = parse_name(
            resource_name
        ).split("/")[1]

        if "/services/" not in resource_name:
            application = self.applications.get_application(
                name=parse_name(resource_name)
            )

            labels = dict(
                application.labels or {}
            )

            asset_type = (
                "appengine.googleapis.com/Application"
            )

        elif "/versions/" not in resource_name:
            service = self.services.get_service(
                name=parse_name(resource_name)
            )

            labels = dict(
                service.labels or {}
            )

            asset_type = (
                "appengine.googleapis.com/Service"
            )

        else:
            service_name = (
                parse_name(resource_name)
                .split("/versions/")[0]
            )

            service = self.services.get_service(
                name=service_name
            )

            labels = dict(
                service.labels or {}
            )

            asset_type = (
                "appengine.googleapis.com/Version"
            )

        return Resource(
            asset_type=asset_type,
            name=resource_name,
            project=project_id,
            location="global",
            labels=labels,
            tags={},
        )

    def apply_labels(
        self,
        resource,
        labels: dict,
    ):
        if (
            resource.asset_type
            == "appengine.googleapis.com/Application"
        ):
            application = self.applications.get_application(
                name=parse_name(resource.name)
            )

            existing = dict(
                application.labels or {}
            )

            if config.PRESERVE_EXISTING_LABELS:
                merged = existing.copy()

                for key, value in labels.items():
                    if key not in merged:
                        merged[key] = value
            else:
                merged = existing.copy()
                merged.update(labels)

            if merged == existing:
                return True

            application.labels = merged

            operation = self.applications.update_application(
                application=application,
                update_mask=FieldMask(
                    paths=["labels"]
                ),
            )

            operation.result()

            return True

        if (
            resource.asset_type
            == "appengine.googleapis.com/Service"
        ):
            raise NotImplementedError(
                "App Engine Service labels are not supported by the App Engine Admin API."
            )

        if (
            resource.asset_type
            == "appengine.googleapis.com/Version"
        ):
            raise NotImplementedError(
                "App Engine Version labels are not supported by the App Engine Admin API."
            )

        raise ValueError(
            f"Unsupported App Engine resource: {resource.asset_type}"
        )