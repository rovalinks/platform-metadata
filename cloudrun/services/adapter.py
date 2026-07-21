import logging

from services.tag_service import TagService
from services.capability import CapabilityService
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
from clients.compute import ComputeClient
from clients.bigquery import BigQueryClient
from clients.storage import StorageClient
from clients.resourcemanager import ResourceManagerClient
from clients.kms import KMSClient
from clients.pubsub import PubSubClient
from clients.project import ProjectClient
from clients.gke import GKEClient
from clients.cloudrun import CloudRunClient
from clients.cloudsql import CloudSQLClient
from clients.artifactregistry import ArtifactRegistryClient
from clients.cloudfunctions import CloudFunctionsClient
from clients.vertex import VertexClient
from clients.dataplex import DataplexClient
from clients.appengine import AppEngineClient
from clients.redis import RedisClient

# from clients.bigquery_reservation import BigQueryReservationClient
# from clients.secret_manager import SecretManagerClient
#from clients.apikeys import ApiKeysClient
from clients.functions import FunctionsClient


logger = logging.getLogger(__name__)


class AdapterService:

    def __init__(self):
        self.tag_service = TagService()
        self.capability = CapabilityService()
        
        self.clients = [
            ComputeClient(),
            BigQueryClient(),
            # BigQueryReservationClient(),
            StorageClient(),
            ResourceManagerClient(),
            KMSClient(),
            PubSubClient(),
            ProjectClient(),
            GkeClient(),
            CloudRunClient(),
            CloudSqlClient(),
            ArtifactRegistryClient(),
            CloudFunctionsClient(),
            VertexClient(),
            DataplexClient(),
            AppEngineClient(),
            RedisClient(),

            # SecretManagerClient(),
            # KmsClient(),
            # ApiKeysClient(),
            FunctionsClient(),
        ]

    def client_for(self, asset_type: str):
        for client in self.clients:
            if client.supports(asset_type):
                return client
        return None

    def enrich(self, resource):
        """
        Populate a discovered resource with live metadata and tags 
        only if it is a supported resource type.
        """
        
        # Determine if the resource is supported for either labels or tags
        is_label_supported = resource.asset_type in SUPPORTED_LABEL_RESOURCES
        is_tag_supported = resource.asset_type in SUPPORTED_TAG_RESOURCES

        # If the resource is not in either list, skip enrichment entirely to avoid unnecessary calls
        if not is_label_supported and not is_tag_supported:
            return resource

        client = self.client_for(resource.asset_type)

        if client is None:
            return resource

        try:
            # Only perform label enrichment if it is supported
            if is_label_supported:
                logger.info("=" * 80)
                logger.info("Enriching resource: %s", resource.name)
                
                labels = client.labels(resource)
                
                if labels is None:
                    logger.warning("Skipping resource (labels returned None): %s", resource.name)
                    return None
                
                resource.labels = labels

            # Apply tags if the resource supports them
            if is_tag_supported:
                resource.tags = self.tag_service.get_tags(resource.name)

        except Exception:
            logger.exception("Failed to enrich %s", resource.asset_type)
            return None

        return resource