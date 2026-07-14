from googleapiclient.discovery import build

from clients.base import ResourceClient
from models.resource import Resource


class CloudSqlClient(ResourceClient):
    """Cloud SQL resource adapter."""

    def __init__(self):
        self.client = build(
            "sqladmin",
            "v1beta4",
            cache_discovery=False,
        )

    def supports(self, asset_type: str):
        return asset_type == "sqladmin.googleapis.com/Instance"

    def labels(self, resource):

        info = self._parse(resource.name)

        instance = (
            self.client.instances()
            .get(
                project=info["project"],
                instance=info["instance"],
            )
            .execute()
        )

        return dict(
            instance.get("settings", {}).get(
                "userLabels", {}
            )
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource:

        info = self._parse(resource_name)

        instance = (
            self.client.instances()
            .get(
                project=info["project"],
                instance=info["instance"],
            )
            .execute()
        )

        return Resource(

            asset_type="sqladmin.googleapis.com/Instance",

            name=resource_name,

            project=info["project"],

            location=instance.get(
                "region",
                "global",
            ),

            labels=dict(
                instance.get(
                    "settings",
                    {},
                ).get(
                    "userLabels",
                    {},
                )
            ),

            tags={},
        )

    def apply_labels(
        self,
        resource,
        labels,
    ):

        info = self._parse(resource.name)

        instance = (
            self.client.instances()
            .get(
                project=info["project"],
                instance=info["instance"],
            )
            .execute()
        )

        merged = dict(
            instance.get(
                "settings",
                {},
            ).get(
                "userLabels",
                {},
            )
        )

        merged.update(labels)

        body = {
            "settings": {
                "settingsVersion":
                    instance["settings"]["settingsVersion"],
                "userLabels":
                    merged,
            }
        }

        self.client.instances().patch(
            project=info["project"],
            instance=info["instance"],
            body=body,
        ).execute()

        return True

    @staticmethod
    def _parse(name: str):

        #
        # Audit logs sometimes send:
        # projects/<project>
        #
        # instead of
        # projects/<project>/instances/<instance>
        #

        parts = name.split("/")

        if "instances" in parts:

            return {
                "project": parts[1],
                "instance": parts[3],
            }

        raise ValueError(
            f"Unexpected Cloud SQL resource: {name}"
        )