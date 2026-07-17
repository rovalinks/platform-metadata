from pydantic import BaseModel, Field
from typing import Dict, Optional, Any

class ResourceData(BaseModel):
    """Represents the actual configuration data of the GCP resource."""
    labels: Dict[str, str] = Field(default_factory=dict)
    name: Optional[str] = None
    
    # Allow capturing any other raw configuration data CAI sends
    model_config = {"extra": "allow"}

class AssetResource(BaseModel):
    """Wrapper for the resource data in the CAI payload."""
    data: Optional[ResourceData] = None
    model_config = {"extra": "allow"}

class Asset(BaseModel):
    """The core asset object sent by Cloud Asset Inventory."""
    name: str
    assetType: str
    resource: Optional[AssetResource] = None

class CAIEventPayload(BaseModel):
    """The root structure of a CAI feed event."""
    asset: Asset
    deleted: bool = False
    
    @property
    def labels(self) -> Dict[str, str]:
        """Helper to safely extract labels from the nested CAI payload."""
        if self.asset.resource and self.asset.resource.data:
            return self.asset.resource.data.labels
        return {}
        
    @property
    def app_id(self) -> Optional[str]:
        """Helper to extract the specific app_id label for registry matching."""
        return self.labels.get('app_id')
        
    @property
    def is_terraform_managed(self) -> bool:
        """Checks the provenance tag to determine enforcement strategy."""
        return self.labels.get('provisioned-by') == 'terraform'