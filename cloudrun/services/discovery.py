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

            # Check if the bucket should be explicitly excluded from config
            if (
                resource.asset_type == "storage.googleapis.com/Bucket"
                and any(bucket.lower() in resource.name.lower() for bucket in config.EXCLUDED_BUCKETS)
            ):
                logger.info("Skipping excluded bucket %s", resource.name)
                continue

            # =================================================================
            # COMPREHENSIVE DEFAULT GCP RESOURCE FILTER
            # =================================================================
            is_default = False
            asset_type_lower = resource.asset_type.lower()
            res_name_lower = resource.name.lower()

            # 1. Compute Engine Defaults
            if "compute.googleapis.com" in asset_type_lower:
                if res_name_lower.endswith("/networks/default"): is_default = True
                elif "/subnetworks/default" in res_name_lower: is_default = True
                elif "/firewalls/default-" in res_name_lower: is_default = True
                elif "/routes/default-route" in res_name_lower: is_default = True

            # 2. Cloud Storage Defaults (Google Managed)
            elif "storage.googleapis.com/bucket" in asset_type_lower:
                if "artifacts." in res_name_lower and ".appspot.com" in res_name_lower: is_default = True
                elif "gcf-sources-" in res_name_lower: is_default = True
                elif "cloud-build-logs-" in res_name_lower: is_default = True
                elif res_name_lower.endswith("_cloudbuild"): is_default = True

            # 3. IAM / Service Accounts (Compute and AppEngine defaults)
            elif "iam.googleapis.com/serviceaccount" in asset_type_lower:
                if "-compute@developer.gserviceaccount.com" in res_name_lower: is_default = True
                elif "@appspot.gserviceaccount.com" in res_name_lower: is_default = True

            if is_default:
                logger.info("Skipping default Google-managed resource: %s", resource.name)
                continue
            # =================================================================

            if resource is None:
                continue

            resources.append(resource)

        logger.info("Discovered %d real resources", len(resources))

        if run_id:
            self.snapshot.save_inventory(resources, run_id)
            logger.info("Discovery snapshot saved. Run ID: %s", run_id)

        return resources