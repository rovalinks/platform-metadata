from google.cloud import asset_v1


class CloudAssetClient:
    """Wrapper around the Google Cloud Asset Inventory client."""

    def __init__(self):
        self.client = asset_v1.AssetServiceClient()

    def search_project_resources(self, project_id: str):

        request = asset_v1.SearchAllResourcesRequest(
            scope=f"projects/{project_id}"
        )

        return self.client.search_all_resources(request=request)