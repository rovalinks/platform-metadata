from dataclasses import dataclass


@dataclass
class VerificationResult:

    resource: str
    asset_type: str
    verified: bool
    message: str

    def to_dict(self):
        return {
            "resource": self.resource,
            "asset_type": self.asset_type,
            "verified": self.verified,
            "message": self.message,
        }