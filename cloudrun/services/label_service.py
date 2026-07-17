import logging
from cloudrun.clients.compute import ComputeClient
# TODO: Uncomment these as you ensure they follow the same ResourceClient pattern
# from cloudrun.clients.storage import StorageClient
# from cloudrun.clients.sql import SQLClient

logger = logging.getLogger(__name__)

class LabelService:
    """
    Routes label update requests to the correct GCP client based on the asset type.
    Dynamically discovers the correct client using the .supports() method.
    """
    def __init__(self):
        # Initialize all your resource clients here
        self.clients = [
            ComputeClient(),
            # StorageClient(),
            # SQLClient(),
        ]

    def update_labels(self, asset_name: str, asset_type: str, labels: dict):
        """
        Finds the correct client, fetches the resource, and applies the labels.
        """
        logger.info(f"Routing label update for {asset_type}: {asset_name}")
        
        # 1. Find the client that supports this asset type
        target_client = None
        for client in self.clients:
            if hasattr(client, 'supports') and client.supports(asset_type):
                target_client = client
                break
                
        if not target_client:
            logger.error(f"Unsupported asset type for labeling: {asset_type}")
            return

        try:
            # 2. Fetch the full Resource object (required by apply_labels)
            resource = target_client.get(asset_name)
            if not resource:
                logger.error(f"Could not fetch resource state for: {asset_name}")
                return
                
            # 3. Apply the labels using the client's built-in reconciliation logic
            target_client.apply_labels(resource, labels)
            logger.info(f"Successfully applied labels to {asset_name}")
            
        except Exception as e:
            logger.error(f"Error applying labels to {asset_name} via {target_client.__class__.__name__}: {e}")