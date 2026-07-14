from google.cloud import secretmanager

import config

from clients.base import ResourceClient
from models.resource import Resource


class SecretManagerClient(ResourceClient):
    """Secret Manager resource adapter."""

    def __init__(self):
        self.client = (
            secretmanager.SecretManagerServiceClient()
        )

    def _secret_name(
        self,
        resource_name: str,
    ) -> str:
        """Normalizes the secret resource name."""
        if resource_name.startswith(
            "//secretmanager.googleapis.com/"
        ):
            return resource_name.replace(
                "//secretmanager.googleapis.com/",
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
            == "secretmanager.googleapis.com/Secret"
        )

    def labels(
        self,
        resource,
    ):
        secret = self.client.get_secret(
            request={
                "name": self._secret_name(resource.name),
            }
        )

        return dict(
            secret.labels or {}
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource:
        """
        Retrieves a Secret Manager Secret and returns
        the platform Resource model.
        """
        normalized_name = self._secret_name(resource_name)

        secret = self.client.get_secret(
            request={
                "name": normalized_name,
            }
        )

        location = ""

        parts = normalized_name.split("/")

        if "locations" in parts:
            location = parts[
                parts.index("locations") + 1
            ]

        project = ""

        if "projects" in parts:
            project = parts[
                parts.index("projects") + 1
            ]

        return Resource(
            asset_type=(
                "secretmanager.googleapis.com/Secret"
            ),
            name=resource_name,
            project=project,
            location=location,
            labels=dict(
                secret.labels or {}
            ),
            tags={},
        )

    def apply_labels(
        self,
        resource,
        labels: dict,
    ):
        secret = self.client.get_secret(
            request={
                "name": self._secret_name(resource.name),
            }
        )

        existing = dict(
            secret.labels or {}
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

        secret.labels.clear()
        secret.labels.update(
            merged
        )

        self.client.update_secret(
            request={
                "secret": secret,
                "update_mask": {
                    "paths": [
                        "labels",
                    ]
                },
            }
        )

        return True