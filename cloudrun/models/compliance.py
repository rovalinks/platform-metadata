from dataclasses import dataclass, field


@dataclass
class ComplianceResult:

    asset_type: str
    name: str
    project: str
    compliant: bool
    missing_labels: list[str] = field(default_factory=list)
    incorrect_labels: list[str] = field(default_factory=list)

    def to_dict(self):
        return {
            "asset_type": self.asset_type,
            "name": self.name,
            "project": self.project,
            "compliant": self.compliant,
            "missing_labels": self.missing_labels,
            "incorrect_labels": self.incorrect_labels,
        }


@dataclass
class ComplianceSummary:

    total_resources: int
    compliant_resources: int
    non_compliant_resources: int
    compliance_percentage: float

    def to_dict(self):
        return {
            "total_resources": self.total_resources,
            "compliant_resources": self.compliant_resources,
            "non_compliant_resources": self.non_compliant_resources,
            "compliance_percentage": self.compliance_percentage,
        }