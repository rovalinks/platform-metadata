from dataclasses import dataclass


@dataclass(slots=True)
class ExecutionRequest:
    """
    Canonical execution request.

    Used by both Brownfield and
    Greenfield workflows.
    """

    project_id: str

    asset_type: str

    resource_name: str

    labels: dict

