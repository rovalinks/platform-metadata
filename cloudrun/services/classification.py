from utils.logger import logger
from extractors.compute import ComputeExtractor
from extractors.bigquery import BigQueryExtractor
from extractors.storage import StorageExtractor
from extractors.resourcemanager import ResourceManagerExtractor
from extractors.kms import KMSExtractor

class ClassificationService:
    def __init__(self):
        # Register new GCP services here as you expand
        self.extractors = {
            "compute.googleapis.com": ComputeExtractor(),
            "bigquery.googleapis.com": BigQueryExtractor(),
            "storage.googleapis.com": StorageExtractor(),
            "cloudresourcemanager.googleapis.com": ResourceManagerExtractor(),
            "cloudkms.googleapis.com": KMSExtractor(),
        }

    def classify(self, audit_event: dict) -> list:
        """Routes the event dictionary to the correct generic extractor."""
        service_name = audit_event.get("service_name")
        extractor = self.extractors.get(service_name)
        
        if not extractor:
            logger.warning(f"No extractor registered for service: {service_name}")
            return []
            
        return extractor.extract(audit_event)