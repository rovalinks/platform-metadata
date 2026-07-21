from extractors.base import BaseExtractor
from models.resource import Resource

class PubSubExtractor(BaseExtractor):
    def extract(self, audit_event: dict) -> list:
        method = audit_event.get("method_name", "")
        project_id = audit_event.get("project_id")
        resource_name = audit_event.get("resource_name", "")

        if "google.pubsub.v1.Publisher.CreateTopic" in method:
            return [Resource(name=resource_name, asset_type="pubsub.googleapis.com/Topic", project=project_id)]
        elif "google.pubsub.v1.Subscriber.CreateSubscription" in method:
            return [Resource(name=resource_name, asset_type="pubsub.googleapis.com/Subscription", project=project_id)]
            
        return []
