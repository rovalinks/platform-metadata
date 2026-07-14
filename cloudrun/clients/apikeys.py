from google.cloud import api_keys_v2

from clients.base import ResourceClient
from models.resource import Resource
from utils.apikeys import parse_key_name

class ApiKeysClient(ResourceClient):
    """
    API Keys adapter.
    """

    def __init__(self):
        self.client = api_keys_v2.ApiKeysClient()

    def supports(self, asset_type: str):
        return asset_type == "apikeys.googleapis.com/Key"

    def labels(self, resource):
        return {}

    def get(self, resource_name: str) -> Resource:
        key = self.client.get_key(
            name=parse_key_name(resource_name)
        )

        project = resource_name.split("/")[3]

        return Resource(
            asset_type="apikeys.googleapis.com/Key",
            name=resource_name,
            project=project,
            location="global",
            labels={},
            tags={},
        )

    def apply_labels(self, resource, labels: dict):
        raise NotImplementedError(
            "API Keys do not support labels."
        )