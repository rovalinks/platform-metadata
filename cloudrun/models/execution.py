from dataclasses import dataclass


@dataclass
class ExecutionResult:

    resource: str

    asset_type: str

    action: str

    success: bool

    message: str