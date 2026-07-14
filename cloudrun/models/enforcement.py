from dataclasses import dataclass


@dataclass
class EnforcementAction:

    asset_type: str

    name: str

    project: str

    labels: dict

    action: str