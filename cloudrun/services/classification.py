from utils.logger import logger
from extractors.compute import ComputeExtractor
from extractors.bigquery import BigQueryExtractor
from extractors.storage import StorageExtractor
from extractors.resourcemanager import ResourceManagerExtractor
from extractors.kms import KMSExtractor
from extractors.pubsub import PubSubExtractor
from extractors.cloudsql import CloudSQLExtractor
from extractors.gke import GKEExtractor
from extractors.cloudrun import CloudRunExtractor
from extractors.artifactregistry import ArtifactRegistryExtractor
from extractors.cloudfunctions import CloudFunctionsExtractor
from extractors.vertex import VertexExtractor
from extractors.dataplex import DataplexExtractor
from extractors.appengine import AppEngineExtractor
from extractors.redis import RedisExtractor

class ClassificationService:
    def __init__(self):
        # Register new GCP services here as you expand
        self.extractors = {
            "compute.googleapis.com": ComputeExtractor(),
            "bigquery.googleapis.com": BigQueryExtractor(),
            "storage.googleapis.com": StorageExtractor(),
            "cloudresourcemanager.googleapis.com": ResourceManagerExtractor(),
            "cloudkms.googleapis.com": KMSExtractor(),
            "pubsub.googleapis.com": PubSubExtractor(),
            "sqladmin.googleapis.com": CloudSQLExtractor(),
            "container.googleapis.com": GKEExtractor(),
            "run.googleapis.com": CloudRunExtractor(),
            "artifactregistry.googleapis.com": ArtifactRegistryExtractor(),
            "cloudfunctions.googleapis.com": CloudFunctionsExtractor(),
            "aiplatform.googleapis.com": VertexExtractor(),
            "dataplex.googleapis.com": DataplexExtractor(),
            "appengine.googleapis.com": AppEngineExtractor(),
            "redis.googleapis.com": RedisExtractor(),
        }

    def classify(self, audit_event: dict) -> list:
        """Routes the event dictionary to the correct generic extractor."""
        service_name = audit_event.get("service_name")
        extractor = self.extractors.get(service_name)
        
        if not extractor:
            logger.warning(f"No extractor registered for service: {service_name}")
            return []
            
        return extractor.extract(audit_event)