from google.cloud import functions_v2
from google.protobuf.field_mask_pb2 import FieldMask

import config

from clients.base import ResourceClient
from models.resource import Resource
from utils.functions import parse_function_name


class FunctionsClient(ResourceClient):
    """Cloud Functions (Gen2) resource adapter."""

    def __init__(self):
        self.client = functions_v2.FunctionServiceClient()

    def supports(
        self,
        asset_type: str,
    ):
        return (
            asset_type
            == "cloudfunctions.googleapis.com/Function"
        )

    def labels(
        self,
        resource,
    ):
        function = self.client.get_function(
            name=resource.name.replace(
                "//cloudfunctions.googleapis.com/",
                "",
                1,
            )
        )

        return dict(
            function.labels or {}
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource:
        function = self.client.get_function(
            name=resource_name.replace(
                "//cloudfunctions.googleapis.com/",
                "",
                1,
            )
        )

        info = parse_function_name(
            resource_name
        )

        return Resource(
            asset_type="cloudfunctions.googleapis.com/Function",
            name=resource_name,
            project=info["project"],
            location=info["location"],
            labels=dict(
                function.labels or {}
            ),
            tags={},
        )

    def apply_labels(
        self,
        resource,
        labels: dict,
    ):
        function = self.client.get_function(
            name=resource.name.replace(
                "//cloudfunctions.googleapis.com/",
                "",
                1,
            )
        )

        existing = dict(
            function.labels or {}
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

        function.labels = merged

        operation = self.client.update_function(
            function=function,
            update_mask=FieldMask(
                paths=["labels"],
            ),
        )

        operation.result()

        return True