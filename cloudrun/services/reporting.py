from repositories.report_repository import ReportRepository

class ReportingService:
    """Provides governance reporting."""

    def __init__(self):
        self.repository = ReportRepository()

    def dashboard(self, scope="organization", project_id=None):
        return self.repository.dashboard(scope, project_id)

    def compliance(self, scope: str = "organization", project_id: str | None = None):
        """Returns compliance breakdown by resource type."""
        return self.repository.compliance_breakdown(scope=scope, project_id=project_id)

    def resources(self, scope: str = "organization", project_id: str | None = None, limit: int = 100):
        """Returns a list of resources."""
        return self.repository.resources(scope=scope, project_id=project_id, limit=limit)

    def non_compliant(self, scope: str = "organization", project_id: str | None = None, limit: int = 100):
        """Returns a list of non-compliant resources."""
        return self.repository.non_compliant(scope=scope, project_id=project_id, limit=limit)

    def metrics(self, scope: str = "organization", project_id: str | None = None):
        return self.repository.metrics(scope=scope, project_id=project_id)

    def runs(self, scope: str = "organization", project_id: str | None = None, limit: int = 100):
        return self.repository.remediation_runs(scope=scope, project_id=project_id, limit=limit)

    def run(self, run_id: str):
        """Returns summary for a remediation run."""
        return self.repository.remediation_run_summary(run_id)

    def history(self, run_id: str):
        return {
            "run_id": run_id,
            "resources": self.repository.execution_history(run_id),
        }