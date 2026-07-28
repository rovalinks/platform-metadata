from google.cloud import pubsub_v1
from utils.logger import logger
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES
import config
from types import SimpleNamespace

class PubSubClient:
    def __init__(self):
        # Pub/Sub requires separate clients for publishing (Topics) and subscribing (Subscriptions)
        self.publisher = pubsub_v1.PublisherClient()
        self.subscriber = pubsub_v1.SubscriberClient()
        self.dry_run = config.DRY_RUN

    def supports(self, asset_type: str) -> bool:
        supported_types = SUPPORTED_LABEL_RESOURCES.union(SUPPORTED_TAG_RESOURCES)
        return asset_type in supported_types and asset_type.split("/")[0] == "pubsub.googleapis.com"

    def _parse_resource_name(self, resource_url: str):
        # Handle CAI format: //pubsub.googleapis.com/projects/PROJECT/topics/TOPIC
        parts = resource_url.split("//")[-1].split("/")[1:]
        project = parts[parts.index("projects") + 1]
        
        if "topics" in parts:
            topic = parts[parts.index("topics") + 1]
            return self.publisher.topic_path(project, topic), "Topic"
        elif "subscriptions" in parts:
            sub = parts[parts.index("subscriptions") + 1]
            return self.subscriber.subscription_path(project, sub), "Subscription"
            
        raise ValueError(f"Unknown Pub/Sub resource format: {resource_url}")

    def get(self, resource_name: str, **kwargs):
        pubsub_id, res_type = self._parse_resource_name(resource_name)
        try:
            if res_type == "Topic":
                topic = self.publisher.get_topic(request={"topic": pubsub_id})
                return SimpleNamespace(name=resource_name, labels=dict(topic.labels) or {}, tags={})
            elif res_type == "Subscription":
                sub = self.subscriber.get_subscription(request={"subscription": pubsub_id})
                return SimpleNamespace(name=resource_name, labels=dict(sub.labels) or {}, tags={})
        except Exception as e:
            logger.error(f"Failed to fetch Pub/Sub {res_type} {pubsub_id}: {e}")
            raise

    def apply_labels(self, resource, labels: dict, **kwargs) -> bool:
        resource_name = getattr(resource, "name", resource) if not isinstance(resource, str) else resource
        
        if self.dry_run:
            logger.info(f"[DRY RUN] Would patch Pub/Sub {resource_name} with {labels}")
            return True

        pubsub_id, res_type = self._parse_resource_name(resource_name)
        try:
            if res_type == "Topic":
                topic = self.publisher.get_topic(request={"topic": pubsub_id})
                topic.labels = labels
                self.publisher.update_topic(
                    request={"topic": topic, "update_mask": {"paths": ["labels"]}}
                )
            elif res_type == "Subscription":
                sub = self.subscriber.get_subscription(request={"subscription": pubsub_id})
                sub.labels = labels
                self.subscriber.update_subscription(
                    request={"subscription": sub, "update_mask": {"paths": ["labels"]}}
                )
                
            logger.info(f"Successfully patched Pub/Sub {res_type} {pubsub_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to patch Pub/Sub {res_type} {pubsub_id}: {e}")
            return False
