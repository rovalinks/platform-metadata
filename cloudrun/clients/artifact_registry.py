from google.cloud import artifactregistry_v1
from google.protobuf.field_mask_pb2 import FieldMask

from clients.base import ResourceClient
from models.resource import Resource


class ArtifactRegistryClient(ResourceClient):
    """Artifact Registry repository adapter."""

    def __init__(self):

        self.client = artifactregistry_v1.ArtifactRegistryClient()

    def supports(
        self,
        asset_type: str,
    ):

        return (
            asset_type
            == "artifactregistry.googleapis.com/Repository"
        )

    def labels(
        self,
        resource,
    ):

        repository = self.client.get_repository(
            name=self._repository_name(
                resource.name
            )
        )

        return dict(
            repository.labels or {}
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource:
        """
        Retrieves an Artifact Registry repository.
        """

        repository = self.client.get_repository(
            name=self._repository_name(
                resource_name
            )
        )

        return Resource(

            asset_type="artifactregistry.googleapis.com/Repository",

            name=resource_name,

            project="",

            location=repository.name.split("/")[3],

            labels=dict(
                repository.labels or {}
            ),

            tags={},

        )

    def apply_labels(
        self,
        resource,
        labels,
    ):

        repository = self.client.get_repository(
            name=self._repository_name(
                resource.name
            )
        )

        merged = dict(
            repository.labels or {}
        )

        merged.update(labels)

        repository.labels = merged

        self.client.update_repository(
            repository=repository,
            update_mask=FieldMask(
                paths=["labels"]
            ),
        )

        return True

    @staticmethod
    def _repository_name(
        asset_name: str,
    ):

        #
        # Brownfield:
        # //artifactregistry.googleapis.com/projects/p/locations/l/repositories/r
        #
        if asset_name.startswith(
            "//artifactregistry.googleapis.com/"
        ):

            return asset_name.replace(
                "//artifactregistry.googleapis.com/",
                "",
            )

        #
        # Greenfield:
        # projects/p/locations/l/repositories/r
        #

        return asset_name