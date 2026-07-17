from pydantic import BaseModel, Field
from typing import Dict, Optional, Any
from dataclasses import dataclass

# 1. The class the Classification Engine expects
@dataclass(slots=True)
class ResourceEvent:
    project_id: str
    asset_type: str
    resource_name: str
    service_name: str
    method_name: str
    location: str | None = None

# 2. Existing CAI models for Greenfield
class ResourceData(BaseModel):
    labels: Dict[str, str] = Field(default_factory=dict)
    name: Optional[str] = None
    model_config = {"extra": "allow"}

class AssetResource(BaseModel):
    data: Optional[ResourceData] = None
    model_config = {"extra": "allow"}

class Asset(BaseModel):
    name: str
    assetType: str
    resource: Optional[AssetResource] = None

class CAIEventPayload(BaseModel):
    asset: Asset
    deleted: bool = False
    
    @property
    def labels(self) -> Dict[str, str]:
        if self.asset.resource and self.asset.resource.data:
            return self.asset.resource.data.labels
        return {}
        
    @property
    def app_id(self) -> Optional[str]:
        return self.labels.get('app_id')
        
    @property
    def is_terraform_managed(self) -> bool:
        return self.labels.get('provisioned-by') == 'terraform'