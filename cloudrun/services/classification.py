from utils.logger import logger
from extractors.compute import ComputeExtractor

class ClassificationService:
    def __init__(self):
        # Register new GCP services here as you expand
        self.extractors = {
            "compute.googleapis.com": ComputeExtractor(),
        }

    def classify(self, audit_event) -> list:
        """Routes the event to the correct generic extractor."""
        extractor = self.extractors.get(audit_event.service_name)
        
        if not extractor:
            logger.warning(f"No extractor registered for service: {audit_event.service_name}")
            return []
            
        return extractor.extract(audit_event)