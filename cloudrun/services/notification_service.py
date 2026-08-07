import requests
from utils.logger import logger
import config

class NotificationService:
    """Handles sending alerts to Slack or Microsoft Teams via Webhooks."""

    def __init__(self):
        # The URL will be pulled from your environment variables
        self.webhook_url = getattr(config, 'ALERT_WEBHOOK_URL', None)

    def send_missing_label_alert(self, resource_name: str, project_id: str, creator_email: str = "Unknown User"):
        """Fires an alert to the configured chat platform."""
        
        if not self.webhook_url:
            logger.warning("No ALERT_WEBHOOK_URL configured. Skipping notification.")
            return

        # 1. Format the standard message
        message = (
            f"🚨 *FinOps Governance Alert*\n"
            f"User `{creator_email}` just deployed `{resource_name}` in project `{project_id}` "
            f"without the mandatory `product` label.\n"
            f"Please attach the label so the governance engine can map it to the correct billing owner."
        )

        # 2. Dynamically build the payload based on the platform
        if "slack.com" in self.webhook_url:
            # Slack Payload
            payload = {"text": message}
        else:
            # Microsoft Teams Payload (Adaptive MessageCard)
            payload = {
                "@type": "MessageCard",
                "@context": "http://schema.org/extensions",
                "themeColor": "DC2626", # Red warning color
                "summary": "FinOps Governance Alert",
                "sections": [{
                    "activityTitle": "🚨 FinOps Governance Alert",
                    "text": message.replace("\n", "<br>") # Teams uses HTML line breaks
                }]
            }

        # 3. Fire the Webhook
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Governance alert sent successfully!")
        except Exception as e:
            logger.error("Failed to send webhook alert: %s", str(e))