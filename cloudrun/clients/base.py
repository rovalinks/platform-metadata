from abc import ABC, abstractmethod


class ResourceClient(ABC):
    """Base class for resource-specific metadata operations."""

    @abstractmethod
    def supports(self, asset_type: str) -> bool:
        pass

    @abstractmethod
    def apply_labels(self, resource, labels: dict):
        pass