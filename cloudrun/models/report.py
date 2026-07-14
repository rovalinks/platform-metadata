from dataclasses import dataclass


@dataclass
class GovernanceReport:

    project: str
    total_resources: int
    supported_resources: int
    compliant_resources: int
    non_compliant_resources: int
    enforcement_candidates: int
    compliance_percentage: float

    def to_dict(self):
        return {
            "project": self.project,
            "total_resources": self.total_resources,
            "supported_resources": self.supported_resources,
            "compliant_resources": self.compliant_resources,
            "non_compliant_resources": self.non_compliant_resources,
            "enforcement_candidates": self.enforcement_candidates,
            "compliance_percentage": self.compliance_percentage,
        }