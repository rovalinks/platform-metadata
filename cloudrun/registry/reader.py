from io import StringIO

import yaml
from google.cloud import storage

from cache.registry_cache import RegistryCache
from config import REGISTRY_BUCKET, REGISTRY_PREFIX
from utils.logger import logger


class RegistryReader:
    """
    Reads application registry YAML files
    from Cloud Storage.
    """

    def __init__(self):

        self.client = storage.Client()

    def load_all(self):

        applications = RegistryCache.get()

        if applications is not None:
            return applications

        logger.info(
            "========== REGISTRY READER START =========="
        )

        logger.info(
            "Bucket: %s",
            REGISTRY_BUCKET,
        )

        logger.info(
            "Prefix: %s",
            REGISTRY_PREFIX,
        )

        applications = []

        blobs = list(

            self.client.list_blobs(

                REGISTRY_BUCKET,

                prefix=REGISTRY_PREFIX,

            )

        )

        logger.info(
            "Blob count: %d",
            len(blobs),
        )

        for blob in blobs:

            if not blob.name.endswith(".yaml"):
                continue

            logger.info(
                "Blob: %s",
                blob.name,
            )

            applications.append(

                yaml.safe_load(

                    StringIO(

                        blob.download_as_text()

                    )

                )

            )

        logger.info(
            "Applications loaded: %d",
            len(applications),
        )

        logger.info(
            "========== REGISTRY READER END =========="
        )

        RegistryCache.set(applications)

        return applications