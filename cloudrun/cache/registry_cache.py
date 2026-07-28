from datetime import datetime, timedelta

from config import REGISTRY_CACHE_TTL
from utils.logger import logger


class RegistryCache:
    """
    In-memory registry cache.

    Cloud Storage remains the source of truth.
    The cache only avoids downloading the same
    registry repeatedly during a short time window.
    """

    _applications = None
    _expires_at = None

    @classmethod
    def get(cls):

        if (
            cls._applications is None
            or cls._expires_at is None
            or datetime.utcnow() >= cls._expires_at
        ):

            logger.info(
                "Registry cache expired."
            )

            return None

        logger.info(
            "Using cached registry."
        )

        return cls._applications

    @classmethod
    def set(cls, applications):

        cls._applications = applications

        cls._expires_at = (
            datetime.utcnow()
            + timedelta(seconds=REGISTRY_CACHE_TTL)
        )

        logger.info(
            "Registry cache refreshed. Expires in %s seconds.",
            REGISTRY_CACHE_TTL,
        )