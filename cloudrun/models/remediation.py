from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class RemediationPlan:
    """
    Represents a planned remediation action.

    A plan is created from a compliance result and
    persisted before any changes are made to GCP.
    """

    run_id: str

    project_id: str

    asset_type: str

    resource_name: str

    missing_labels: list[str] = field(default_factory=list)

    planned_labels: dict[str, Any] = field(default_factory=dict)

    planned_tags: dict[str, Any] = field(default_factory=dict)

    status: str = "PLANNED"

    created_at: datetime = field(
        default_factory=datetime.utcnow
    )

    def to_dict(self) -> dict:

        return {
            "run_id": self.run_id,
            "project_id": self.project_id,
            "asset_type": self.asset_type,
            "resource_name": self.resource_name,
            "missing_labels": self.missing_labels,
            "planned_labels": self.planned_labels,
            "planned_tags": self.planned_tags,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }
