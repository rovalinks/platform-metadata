from google.cloud import container_v1
from google.api_core.exceptions import (
    NotFound,
    FailedPrecondition,
)

from clients.base import ResourceClient
from models.resource import Resource
from utils.logger import logger


class GkeClient(ResourceClient):
    """Google Kubernetes Engine resource adapter."""

    def __init__(self):
        self.client = (
            container_v1.ClusterManagerClient()
        )

    def supports(
        self,
        asset_type: str,
    ):
        return [
            "container.googleapis.com/Cluster",
            "container.googleapis.com/NodePool",
        ].__contains__(asset_type)

    def labels(
        self,
        resource,
    ):
        #
        # Cluster
        #
        if (
            "/clusters/" in resource.name
            and "/nodePools/" not in resource.name
        ):

            try:

                cluster = self.client.get_cluster(
                    name=self._cluster_name(
                        resource.name
                    )
                )

            except NotFound:

                logger.warning(
                    "Cluster %s no longer exists. Skipping.",
                    resource.name,
                )

                return None

            return dict(
                cluster.resource_labels or {}
            )

        #
        # Node Pool
        #
        try:

            node_pool = self.client.get_node_pool(
                name=self._nodepool_name(
                    resource.name
                )
            )

        except NotFound:

            logger.warning(
                "Node pool %s no longer exists. Skipping.",
                resource.name,
            )

            return None

        return dict(
            node_pool.config.labels or {}
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource | None:

        #
        # Cluster
        #
        if (
            "/clusters/" in resource_name
            and "/nodePools/" not in resource_name
        ):

            try:

                cluster = self.client.get_cluster(
                    name=self._cluster_name(
                        resource_name
                    )
                )

            except NotFound:

                logger.warning(
                    "Cluster %s disappeared during discovery.",
                    resource_name,
                )

                return None

            parts = resource_name.split("/")

            return Resource(
                asset_type="container.googleapis.com/Cluster",
                name=resource_name,
                project=parts[1],
                location=parts[3],
                labels=dict(
                    cluster.resource_labels or {}
                ),
                tags={},
            )

        #
        # Node Pool
        #
        try:

            node_pool = self.client.get_node_pool(
                name=self._nodepool_name(
                    resource_name
                )
            )

        except NotFound:

            logger.warning(
                "Node pool %s disappeared during discovery.",
                resource_name,
            )

            return None

        parts = resource_name.split("/")

        return Resource(
            asset_type="container.googleapis.com/NodePool",
            name=resource_name,
            project=parts[1],
            location=parts[3],
            labels=dict(
                node_pool.config.labels or {}
            ),
            tags={},
        )

    def apply_labels(
        self,
        resource,
        labels: dict,
    ):

        #
        # Cluster
        #
        if (
            "/clusters/" in resource.name
            and "/nodePools/" not in resource.name
        ):

            try:

                cluster = self.client.get_cluster(
                    name=self._cluster_name(
                        resource.name
                    )
                )

            except NotFound:

                logger.warning(
                    "Cluster %s disappeared before remediation.",
                    resource.name,
                )

                return False

            merged = dict(
                cluster.resource_labels or {}
            )

            merged.update(labels)

            request = (
                container_v1.SetLabelsRequest(
                    name=cluster.name,
                    resource_labels=merged,
                    label_fingerprint=cluster.label_fingerprint,
                )
            )

            try:

                self.client.set_labels(
                    request=request
                )

            except FailedPrecondition:

                logger.warning(
                    "Cluster %s is currently updating.",
                    resource.name,
                )

                return False

            return True

        #
        # Node Pool
        #
        try:

            node_pool = self.client.get_node_pool(
                name=self._nodepool_name(
                    resource.name
                )
            )

        except NotFound:

            logger.warning(
                "Node pool %s disappeared before remediation.",
                resource.name,
            )

            return False

        merged = dict(
            node_pool.config.labels or {}
        )

        merged.update(labels)

        request = (
            container_v1.UpdateNodePoolRequest(
                name=node_pool.name,
                node_labels=merged,
            )
        )

        try:

            self.client.update_node_pool(
                request=request
            )

        except FailedPrecondition:

            logger.warning(
                "Node pool %s is currently updating.",
                resource.name,
            )

            return False

        return True

    @staticmethod
    def _cluster_name(
        asset_name: str,
    ):
        return asset_name.replace(
            "//container.googleapis.com/",
            "",
        )

    @staticmethod
    def _nodepool_name(
        asset_name: str,
    ):
        return asset_name.replace(
            "//container.googleapis.com/",
            "",
        )