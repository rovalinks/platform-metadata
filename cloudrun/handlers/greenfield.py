import logging
from flask import Request, jsonify
from utils.cloudevent_parser import parse_pubsub_message
from registry.reader import RegistryReader

logger = logging.getLogger(__name__)
registry = RegistryReader()

def greenfield(payload):
    # This acts as the wrapper to match what dispatcher.py expects
    return handle_greenfield_event(payload)
    
def handle_greenfield_event(request: Request):
    """
    Entry point for real-time CAI feed events via Pub/Sub Push.
    """
    try:
        envelope = request.get_json()
        
        # 1. Parse the incoming Pub/Sub CAI event
        event = parse_pubsub_message(envelope)
        
        # 2. Drop deletion events (the resource is already gone)
        if event.deleted:
            logger.info(f"Ignored asset deletion: {event.asset.name}")
            return jsonify({"status": "ignored", "reason": "deleted_asset"}), 200

        # 3. Check for the Application ID label
        if not event.app_id:
            logger.info(f"Ignored {event.asset.name}: No app_id label found.")
            return jsonify({"status": "ignored", "reason": "missing_app_id"}), 200

        # 4. Validate against the YAML App Registry
        app_record = registry.get_application(event.app_id)
        if not app_record:
            logger.info(f"Ignored {event.asset.name}: App '{event.app_id}' is not in the registry.")
            return jsonify({"status": "ignored", "reason": "unregistered_app"}), 200

        # 5. Asset is registered! Route to compliance evaluation
        logger.info(f"Evaluating registered asset: {event.asset.name} (App: {event.app_id})")
        
        # TODO: Call your compliance and enforcement services here
        # evaluate_compliance(event, app_record)
        
        return jsonify({"status": "processed"}), 200

    except ValueError as e:
        logger.warning(f"Payload validation error: {e}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.exception("Unexpected error processing CAI event")
        return jsonify({"error": "Internal Server Error"}), 500