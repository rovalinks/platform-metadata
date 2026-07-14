from dataclasses import dataclass


@dataclass(frozen=True)
class GCPBinding:
    project_id: str
    region: str
    environment: str
    business_criticality: str


@dataclass(frozen=True)
class ApplicationRegistry:
    schema_version: str
    product: str
    team: str
    owner: str
    budget_owner: str
    organization: str
    department: str
    cost_center: str
    bindings: list[GCPBinding]