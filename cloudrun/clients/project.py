from google.cloud.resourcemanager_v3 import ProjectsClient 
from google.protobuf.field_mask_pb2 import FieldMask

import config

from clients.base import ResourceClient
from models.resource import Resource


class ProjectClient(ResourceClient):
    """Cloud Resource Manager Project resource adapter."""

    def __init__(self):
        self.client = (
            ProjectsClient()
        )

    def _project_name(
        self,
        resource_name: str,
    ) -> str:
        if resource_name.split("//")[-1].split("/")[0] == "cloudresourcemanager.googleapis.com":
            return resource_name.replace(
                "//cloudresourcemanager.googleapis.com/",
                "",
                1,
            )
        return resource_name

    def supports(
        self,
        asset_type: str,
    ):
        return (
            asset_type
            == "cloudresourcemanager.googleapis.com/Project"
        )

    def labels(
        self,
        resource,
    ):
        project = self.client.get_project(
            name=self._project_name(
                resource.name
            )
        )

        return dict(
            project.labels or {}
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource:
        """
        Retrieves a Cloud Resource Manager Project
        and returns the platform Resource model.
        """
        project = self.client.get_project(
            name=self._project_name(
                resource_name
            )
        )

        return Resource(
            asset_type="cloudresourcemanager.googleapis.com/Project",
            name=resource_name,
            project=project.project_id,
            location="global",
            labels=dict(
                project.labels or {}
            ),
            tags={},
        )

    def apply_labels(
        self,
        resource,
        labels: dict,
    ):
        project = self.client.get_project(
            name=self._project_name(
                resource.name
            )
        )

        existing = dict(
            project.labels or {}
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

        project.labels = merged

        operation = self.client.update_project(
            project=project,
            update_mask=FieldMask(
                paths=["labels"],
            ),
        )

        operation.result()

        return True