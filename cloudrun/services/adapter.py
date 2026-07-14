import logging

from services.tag_service import TagService
from services.capability import CapabilityService
from clients.compute import ComputeClient
# from clients.bigquery import BigQueryClient
# from clients.storage import StorageClient
# from clients.sql import CloudSqlClient
# from clients.artifact_registry import ArtifactRegistryClient
# from clients.pubsub import PubSubClient
# from clients.gke import GkeClient
# from clients.bigquery_reservation import BigQueryReservationClient
# from clients.secret_manager import SecretManagerClient
#from clients.project import ProjectClient
# from clients.kms import KmsClient
#from clients.apikeys import ApiKeysClient
from clients.appengine import AppEngineClient
from clients.functions import FunctionsClient

logger = logging.getLogger(__name__)


class AdapterService:

    def __init__(self):
        self.tag_service = TagService()
        self.capability = CapabilityService()
        
        self.clients = [
            ComputeClient(),
            # BigQueryClient(),
            # BigQueryReservationClient(),
            # StorageClient(),
            # CloudSqlClient(),
            # ArtifactRegistryClient(),
            # PubSubClient(),
            # GkeClient(),
            # SecretManagerClient(),
            # ProjectClient(),
            # KmsClient(),
            # ApiKeysClient(),
            AppEngineClient(),
            FunctionsClient(),
        ]

    def client_for(
        self,
        asset_type: str,
    ):
        for client in self.clients:
            if client.supports(asset_type):
                return client

        return None

    def enrich(
        self,
        resource,
    ):
        """
        Populate a discovered resource with live metadata and tags.
        """
        client = self.client_for(
            resource.asset_type
        )

        if client is None:
            return resource

        try:
            logger.info("=" * 80)
            logger.info("Enriching resource")
            logger.info(
                "Asset Type : %s",
                resource.asset_type,
            )
            logger.info(
                "Name       : %s",
                resource.name,
            )

            labels = client.labels(
                resource
            )

        except Exception:
            logger.exception(
                "Failed to enrich %s",
                resource.asset_type,
            )
            return None

        if labels is None:
            logger.warning(
                "Skipping resource because labels() returned None: %s",
                resource.name,
            )
            return None

        resource.labels = labels

        # Apply tags if the resource supports them
        if self.capability.supports_tags(
            resource.asset_type,
        ):
            resource.tags = self.tag_service.get_tags(
                resource.name,
            )

        return resource