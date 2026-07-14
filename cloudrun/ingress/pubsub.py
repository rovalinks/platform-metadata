import base64
import json
from flask import Response
from utils.logger import logger
from services.greenfield import GreenfieldService

class PubSubIngress:
    """
    Handles Pub/Sub push requests.

    Responsibilities:
    - Validate Pub/Sub envelope.
    - Decode Base64 payload.
    - Pass original Audit Log event to GreenfieldService.
    """
    def __init__(self):
        self.greenfield = GreenfieldService()

    def process(self, request):
        body = request.get_json(silent=True)
        logger.info("Incoming Pub/Sub request.")

        if body is None:
            logger.error("Pub/Sub request body is empty.")
            return Response("Invalid request", status=400)

        message = body.get("message")
        if message is None:
            logger.error("Missing Pub/Sub message.")
            return Response("Missing message", status=400)

        encoded_data = message.get("data")
        if not encoded_data:
            logger.error("Missing Pub/Sub message data.")
            return Response("Missing data", status=400)

        try:
            decoded = base64.b64decode(encoded_data).decode("utf-8")
            event = json.loads(decoded)
            logger.info("Pub/Sub event method: %s", event.get("protoPayload", {}).get("methodName"))
            
        except (ValueError, json.JSONDecodeError, TypeError) as exc:
            logger.exception("Failed to decode Pub/Sub payload: %s", exc)
            return Response("Invalid Pub/Sub payload", status=400)

        logger.info("Successfully decoded Pub/Sub Audit Log event.")
        result = self.greenfield.process(event)
        return result, 200