from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    """Generic interface for all GCP Service Extractors. Must return a list of Resources."""
    @abstractmethod
    def extract(self, audit_event) -> list:
        pass