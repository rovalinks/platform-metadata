import logging

from google.cloud import storage

import config

from clients.base import ResourceClient
from config import EXCLUDED_BUCKETS
from models.resource import Resource

# Configure logger
logger = logging.getLogger(__name__)


class StorageClient(ResourceClient):
    """Cloud Storage resource adapter."""

    def __init__(self):

        self.client = storage.Client()

    def supports(
        self,
        asset_type: str,
    ):

        return asset_type == "storage.googleapis.com/Bucket"

    def labels(
        self,
        resource,
    ):

        bucket_name = resource.name.split("/")[-1]

        if bucket_name in EXCLUDED_BUCKETS:

            logger.info(
                "Skipping excluded bucket %s",
                bucket_name,
            )

            return {}

        bucket = self.client.get_bucket(
            bucket_name
        )

        return dict(
            bucket.labels or {}
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource:
        """
        Retrieves a Cloud Storage bucket and returns
        the platform Resource model.
        """

        bucket_name = resource_name.split("/")[-1]

        bucket = self.client.get_bucket(
            bucket_name
        )

        return Resource(

            asset_type="storage.googleapis.com/Bucket",

            name=resource_name,

            project="",

            location=bucket.location,

            labels=dict(
                bucket.labels or {}
            ),

            tags={},

        )

    def apply_labels(
        self,
        resource,
        labels: dict,
    ):

        bucket_name = resource.name.split("/")[-1]

        if bucket_name in EXCLUDED_BUCKETS:

            logger.info(
                "Skipping excluded bucket %s",
                bucket_name,
            )

            return False

        bucket = self.client.get_bucket(
            bucket_name
        )

        existing = dict(
            bucket.labels or {}
        )

        if config.PRESERVE_EXISTING_LABELS:

            merged = existing.copy()

            for key, value in labels.items():

                if key not in merged:

                    merged[key] = value

        else:

            merged = existing.copy()

            merged.update(labels)

        #
        # Nothing to update
        #
        if merged == existing:

            logger.info(
                "Bucket %s already compliant.",
                bucket_name,
            )

            return True

        bucket.labels = merged

        bucket.patch()

        logger.info(
            "Updated labels on bucket %s",
            bucket_name,
        )

        return True