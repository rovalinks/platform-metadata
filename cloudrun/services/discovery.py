from utils.logger import logger
from clients.cloud_asset import CloudAssetClient
from models.resource import Resource
from services.adapter import AdapterService
from repositories.snapshot_repository import SnapshotRepository
import config

class DiscoveryService:
    """Discovers Google Cloud resources and enriches them with live metadata."""

    def __init__(self):
        self.client = CloudAssetClient()
        self.adapter = AdapterService()
        self.snapshot = SnapshotRepository()

    def discover(self, project_id: str, run_id: str | None = None):
        """Discovers Google Cloud resources and enriches them with live metadata."""
        logger.info("Starting resource discovery for project %s", project_id)

        resources = []

        # Hardcode exclusion for platform project
        if project_id == "platform-metadata":
            logger.info("Skipping excluded platform project.")
            return []

        for asset in self.client.search_project_resources(project_id):
            # 1. Map CAI labels directly (Bypassing N+1 API calls)
            cai_labels = dict(asset.labels) if hasattr(asset, 'labels') and asset.labels else {}

            resource = Resource(
                asset_type=asset.asset_type,
                name=asset.name,
                project=project_id,
                location=asset.location,
            )

            # Check if the bucket should be excluded
            if (
                resource.asset_type == "storage.googleapis.com/Bucket"
                and any(bucket.lower() in resource.name.lower() for bucket in config.EXCLUDED_BUCKETS)
            ):
                logger.info("Skipping excluded bucket %s", resource.name)
                continue

            # resource = self.adapter.enrich(resource)

            if resource is None:
                continue

            resources.append(resource)

        logger.info("Discovered %d resources", len(resources))

        if run_id:
            self.snapshot.save_inventory(resources, run_id)
            logger.info("Discovery snapshot saved. Run ID: %s", run_id)

        return resources