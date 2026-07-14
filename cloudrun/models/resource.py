from dataclasses import dataclass, field


@dataclass
class Resource:
    asset_type: str
    name: str
    project: str
    location: str | None = None
    labels: dict = field(default_factory=dict)
    tags: dict = field(default_factory=dict)

    def to_dict(self):
        return {
            "asset_type": self.asset_type,
            "name": self.name,
            "project": self.project,
            "location": self.location,
            "labels": self.labels,
            "tags": self.tags,
        }