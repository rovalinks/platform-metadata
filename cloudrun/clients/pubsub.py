from google.cloud import pubsub_v1
from google.protobuf.field_mask_pb2 import FieldMask

from clients.base import ResourceClient
from models.resource import Resource


class PubSubClient(ResourceClient):
    """Pub/Sub Topic adapter."""

    def __init__(self):

        self.client = pubsub_v1.PublisherClient()

    def supports(
        self,
        asset_type: str,
    ):

        return (
            asset_type
            == "pubsub.googleapis.com/Topic"
        )

    def labels(
        self,
        resource,
    ):

        topic = self.client.get_topic(
            topic=self._topic_name(
                resource.name
            )
        )

        return dict(
            topic.labels or {}
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource:
        """
        Retrieves a Pub/Sub Topic and returns
        the platform Resource model.
        """

        topic = self.client.get_topic(
            topic=self._topic_name(
                resource_name
            )
        )

        return Resource(

            asset_type="pubsub.googleapis.com/Topic",

            name=resource_name,

            #
            # GreenfieldService injects the
            # authoritative project ID.
            #
            project="",

            location="global",

            labels=dict(
                topic.labels or {}
            ),

            tags={},

        )

    def apply_labels(
        self,
        resource,
        labels,
    ):

        topic = self.client.get_topic(
            topic=self._topic_name(
                resource.name
            )
        )

        merged = dict(
            topic.labels or {}
        )

        merged.update(labels)

        topic.labels.clear()

        topic.labels.update(merged)

        self.client.update_topic(
            topic=topic,
            update_mask=FieldMask(
                paths=["labels"]
            ),
        )

        return True

    @staticmethod
    def _topic_name(
        asset_name: str,
    ):

        #
        # Accept both:
        #
        # //pubsub.googleapis.com/projects/<project>/topics/<topic>
        #
        # and
        #
        # projects/<project>/topics/<topic>
        #

        if asset_name.startswith(
            "//pubsub.googleapis.com/"
        ):

            return asset_name.replace(
                "//pubsub.googleapis.com/",
                "",
            )

        return asset_name