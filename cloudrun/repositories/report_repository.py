from google.cloud import bigquery
import config
from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES

class ReportRepository:
    """Read-only repository used for governance reporting."""
    
    # DYNAMICALLY COMBINE ALL SUPPORTED RESOURCES
    # Convert to a tuple so Python string formatting natively creates the SQL ( 'a', 'b' ) syntax
    VALID_ASSETS = tuple([*SUPPORTED_LABEL_RESOURCES, *SUPPORTED_TAG_RESOURCES])

    def __init__(self):
        self.client = bigquery.Client()
        self.dataset = config.BIGQUERY_DATASET

    # --- Private Helpers ---
    def _scope_filter(self, scope: str, project_id: str | None, column: str = "project_id") -> tuple[str, list]:
        match scope:
            case "organization": return "", []
            case "project":
                if not project_id: raise ValueError("project_id required")
                return f"WHERE {column}=@project_id", [bigquery.ScalarQueryParameter("project_id", "STRING", project_id)]
            case _: raise ValueError(f"Unsupported scope '{scope}'")

    def _project_filter(self, scope: str, project_id: str | None, column: str = "project_id") -> tuple[str, list]:
        match scope:
            case "organization": return "", []
            case "project":
                if not project_id: raise ValueError("project_id required")
                return f"AND {column}=@project_id", [bigquery.ScalarQueryParameter("project_id", "STRING", project_id)]
            case _: raise ValueError(f"Unsupported scope '{scope}'")

    def _limit_parameter(self, limit: int) -> bigquery.ScalarQueryParameter:
        return bigquery.ScalarQueryParameter("limit", "INT64", limit)

    def _job(self, query: str, params: list | None = None):
        return self.client.query(query, job_config=bigquery.QueryJobConfig(query_parameters=params or []))

    def _rows(self, job):
        return [dict(row.items()) for row in job.result()]

    def _first(self, job):
        return next(job.result())

    # --- Public Methods ---
    def executive_summary(self, scope="organization", project_id=None):
        return {
            "estate": self._dashboard_summary(scope, project_id),
            "brownfield": self.brownfield_summary(scope, project_id),
            "greenfield": self.greenfield_summary(scope, project_id),
        }

    def _dashboard_summary(self, scope: str, project_id: str | None):
        where_clause, params = self._scope_filter(scope, project_id, "r.project_id")
        comp_where = where_clause.replace("r.project_id", "c.project_id")
        comp_prefix = "WHERE" if not comp_where else f"{comp_where} AND"
        
        query = f"""
        WITH 
        latest_resources AS (SELECT * FROM `{self.dataset}.resource_snapshot` QUALIFY ROW_NUMBER() OVER(PARTITION BY project_id, resource_name ORDER BY snapshot_time DESC) = 1),
        latest_compliance AS (SELECT * FROM `{self.dataset}.compliance_snapshot` QUALIFY ROW_NUMBER() OVER(PARTITION BY project_id, resource_name ORDER BY evaluated_time DESC) = 1),
        resources AS (SELECT COUNT(*) AS total_resources, COUNT(DISTINCT project_id) AS total_projects FROM latest_resources r {where_clause}),
        compliance AS (SELECT COUNT(*) AS supported_resources, COUNTIF(compliant = TRUE) AS compliant_resources, COUNTIF(FALSE) AS non_compliant_resources FROM latest_compliance c {comp_prefix} c.asset_type IN {self.VALID_ASSETS}),
        plans AS (SELECT COUNT(*) AS planned_remediations FROM `{self.dataset}.remediation_plan` {where_clause.replace("r.project_id", "project_id")}),
        latest_execution AS (SELECT status, ROW_NUMBER() OVER(PARTITION BY run_id, resource_name ORDER BY executed_at DESC) as rn FROM `{self.dataset}.remediation_execution` {where_clause.replace("r.project_id", "project_id")}),
        executions AS (SELECT COUNT(*) AS executed_remediations, COUNTIF(status = 'SUCCESS') AS successful_remediations, COUNTIF(status = 'FAILED') AS failed_remediations, COUNTIF(status = 'IN_PROGRESS') AS in_progress_remediations FROM latest_execution WHERE rn = 1)
        SELECT * FROM resources CROSS JOIN compliance CROSS JOIN plans CROSS JOIN executions
        """
        row = self._first(self._job(query, params))
        return {
            "projects": row.total_projects, "total_resources": row.total_resources,
            "supported_resources": row.supported_resources, "compliant_resources": row.compliant_resources,
            "non_compliant_resources": row.non_compliant_resources,
            "compliance_percentage": round((row.compliant_resources / row.supported_resources) * 100, 2) if row.supported_resources > 0 else 100,
            "planned_remediations": row.planned_remediations, "remaining_remediations": (row.planned_remediations - row.executed_remediations),
            "in_progress_remediations": row.in_progress_remediations, "executed_remediations": row.executed_remediations,
            "successful_remediations": row.successful_remediations, "failed_remediations": row.failed_remediations,
            "success_rate": round((row.successful_remediations / row.executed_remediations) * 100, 2) if row.executed_remediations > 0 else 100,
        }

    def dashboard(self, scope: str = "organization", project_id: str | None = None, mode: str = "brownfield"):
        if mode == "greenfield":
            return {
                "mode": "greenfield",
                "executive_summary": {
                    "estate": self._dashboard_summary(scope, project_id),
                    "brownfield": self.brownfield_summary(scope, project_id),
                    "greenfield": self.greenfield_summary(scope, project_id)
                },
                "projects": self.greenfield_projects(),
                "all_projects": [],
                "resource_types": self.greenfield_resource_types(),
                "top_non_compliant": [],
                "recent_activity": self.greenfield_recent_activity()
            }
        
        return {
            "mode": "brownfield",
            "executive_summary": self.executive_summary(scope, project_id),
            "projects": self.project_summary(scope, project_id),
            "all_projects": self.project_summary("organization", None),
            "resource_types": self.compliance_breakdown(scope, project_id),
            "top_non_compliant": self.top_non_compliant(scope, project_id),
            "recent_activity": self.remediation_runs(scope, project_id, 5),
        }

    def resources(self, scope: str = "organization", project_id: str | None = None, limit: int = 100):
        where_clause, params = self._scope_filter(scope, project_id, "r.project_id")
        params.append(self._limit_parameter(limit))
        query = f"""
        WITH latest_resources AS (SELECT * FROM `{self.dataset}.resource_snapshot` QUALIFY ROW_NUMBER() OVER(PARTITION BY project_id, resource_name ORDER BY snapshot_time DESC) = 1)
        SELECT r.project_id, r.asset_type, r.resource_name, r.location, r.labels
        FROM latest_resources r {where_clause} ORDER BY r.project_id, r.asset_type LIMIT @limit
        """
        return self._rows(self._job(query, params))

    def non_compliant(self, scope: str = "organization", project_id: str | None = None, limit: int = 100):
        and_clause, params = self._project_filter(scope, project_id, "c.project_id")
        params.append(self._limit_parameter(limit))
        comp_prefix = "WHERE" if not and_clause else f"{and_clause} AND"
        query = f"""
        WITH latest_compliance AS (SELECT * FROM `{self.dataset}.compliance_snapshot` QUALIFY ROW_NUMBER() OVER(PARTITION BY project_id, resource_name ORDER BY evaluated_time DESC) = 1)
        SELECT c.project_id, c.asset_type, c.resource_name FROM latest_compliance c WHERE c.compliant = FALSE {and_clause} AND c.asset_type IN {self.VALID_ASSETS}
        ORDER BY c.asset_type, c.resource_name LIMIT @limit
        """
        return self._rows(self._job(query, params))

    def top_non_compliant(self, scope: str = "organization", project_id: str | None = None, limit: int = 10):
        and_clause, params = self._project_filter(scope, project_id, "c.project_id")
        params.append(self._limit_parameter(limit))
        query = f"""
        WITH latest_compliance AS (SELECT * FROM `{self.dataset}.compliance_snapshot` QUALIFY ROW_NUMBER() OVER(PARTITION BY project_id, resource_name ORDER BY evaluated_time DESC) = 1)
        SELECT c.project_id, c.asset_type, c.resource_name, c.missing_labels, c.incorrect_labels
        FROM latest_compliance c WHERE c.compliant = FALSE {and_clause} AND c.asset_type IN {self.VALID_ASSETS} LIMIT @limit
        """
        return self._rows(self._job(query, params))

    def compliance_breakdown(self, scope: str = "organization", project_id: str | None = None):
        where_clause, params = self._scope_filter(scope, project_id, "c.project_id")
        comp_prefix = "WHERE" if not where_clause else f"{where_clause} AND"
        query = f"""
        WITH latest_compliance AS (SELECT * FROM `{self.dataset}.compliance_snapshot` QUALIFY ROW_NUMBER() OVER(PARTITION BY project_id, resource_name ORDER BY evaluated_time DESC) = 1)
        SELECT c.asset_type, COUNT(*) AS total, COUNTIF(c.compliant) AS compliant, COUNTIF(NOT c.compliant) AS non_compliant
        FROM latest_compliance c {comp_prefix} c.asset_type IN {self.VALID_ASSETS} GROUP BY c.asset_type ORDER BY total DESC
        """
        results = []
        for row in self._job(query, params).result():
            results.append({
                "asset_type": row.asset_type, "total": row.total, "compliant": row.compliant,
                "non_compliant": row.non_compliant, "compliance_percentage": round(row.compliant * 100 / row.total, 2) if row.total > 0 else 100,
            })
        return results

    def project_summary(self, scope: str = "organization", project_id: str | None = None):
        where_clause, params = self._scope_filter(scope, project_id, "c.project_id")
        comp_prefix = "WHERE" if not where_clause else f"{where_clause} AND"
        query = f"""
        WITH latest_compliance AS (SELECT * FROM `{self.dataset}.compliance_snapshot` QUALIFY ROW_NUMBER() OVER(PARTITION BY project_id, resource_name ORDER BY evaluated_time DESC) = 1)
        SELECT c.project_id, COUNT(*) AS total_resources, COUNTIF(c.compliant) AS compliant_resources, COUNTIF(NOT c.compliant) AS non_compliant_resources
        FROM latest_compliance c {comp_prefix} c.asset_type IN {self.VALID_ASSETS} GROUP BY c.project_id ORDER BY total_resources DESC
        """
        results = []
        for row in self._job(query, params).result():
            total = row.total_resources
            results.append({
                "project_id": row.project_id, "total_resources": total, "compliant_resources": row.compliant_resources,
                "non_compliant_resources": row.non_compliant_resources, "compliance_percentage": (round(row.compliant_resources * 100 / total, 2) if total else 100),
            })
        return results

    def remediation_runs(self, scope: str = "organization", project_id: str | None = None, limit: int = 100):
        where_clause, params = self._scope_filter(scope, project_id, "project_id")
        query = f"""
        WITH plan_counts AS (SELECT run_id, COUNT(*) AS planned_total, MIN(created_at) AS started FROM `{self.dataset}.remediation_plan` {where_clause} GROUP BY run_id),
        latest_execution AS (SELECT run_id, status, ROW_NUMBER() OVER(PARTITION BY run_id, resource_name ORDER BY executed_at DESC) as rn FROM `{self.dataset}.remediation_execution` {where_clause}),
        exec_counts AS (SELECT run_id, COUNTIF(status='SUCCESS') AS completed, COUNTIF(status='FAILED') AS failed, COUNTIF(status='IN_PROGRESS') AS in_progress FROM latest_execution WHERE rn = 1 GROUP BY run_id)
        SELECT p.run_id, p.planned_total AS planned, COALESCE(e.completed, 0) AS completed, COALESCE(e.failed, 0) AS failed, COALESCE(e.in_progress, 0) AS in_progress, (p.planned_total - COALESCE(e.completed, 0) - COALESCE(e.failed, 0) - COALESCE(e.in_progress, 0)) AS remaining, p.started
        FROM plan_counts p LEFT JOIN exec_counts e ON p.run_id = e.run_id ORDER BY p.started DESC LIMIT @limit
        """
        params.append(self._limit_parameter(limit))
        results = []
        for row in self._job(query, params).result():
            data = dict(row.items())
            total = data['planned']
            data['success_rate'] = round((data['completed'] / total) * 100, 2) if total > 0 else 100.0
            results.append(data)
        return results

    # --- Greenfield Methods ---
    def greenfield_summary(self, scope: str = "organization", project_id: str | None = None):
        where_clause, params = self._scope_filter(scope, project_id, "project_id")
        prefix = "WHERE" if not where_clause else "AND"
        query = f"""
        SELECT 
            COUNT(*) AS total_events,
            COUNTIF(status='SUCCESS') AS successful,
            COUNTIF(status='FAILED') AS failed,
            COUNTIF(status='UNSUPPORTED') AS unsupported,
            AVG(duration_ms) AS average_duration_ms,
            MAX(executed_at) AS last_event
        FROM `{self.dataset}.remediation_execution`
        {where_clause} {prefix} execution_mode='GREENFIELD'
        """
        row = self._first(self._job(query, params))
        return {
            "total_events": row.total_events,
            "successful": row.successful,
            "failed": row.failed,
            "unsupported": row.unsupported,
            "average_duration_ms": round(row.average_duration_ms or 0, 2),
            "last_event": row.last_event
        }

    def greenfield_projects(self):
        query = f"""SELECT project_id, COUNT(*) AS total_events, COUNTIF(status='SUCCESS') AS successful, COUNTIF(status='FAILED') AS failed FROM `{self.dataset}.remediation_execution` WHERE execution_mode='GREENFIELD' GROUP BY project_id ORDER BY total_events DESC"""
        return self._rows(self._job(query))

    def greenfield_resource_types(self):
        query = f"""SELECT asset_type, COUNT(*) AS total_events, COUNTIF(status='SUCCESS') AS successful, COUNTIF(status='FAILED') AS failed FROM `{self.dataset}.remediation_execution` WHERE execution_mode='GREENFIELD' GROUP BY asset_type ORDER BY total_events DESC"""
        return self._rows(self._job(query))

    def greenfield_recent_activity(self):
        query = f"""SELECT executed_at, project_id, asset_type, resource_name, status, duration_ms FROM `{self.dataset}.remediation_execution` WHERE execution_mode='GREENFIELD' ORDER BY executed_at DESC LIMIT 20"""
        return self._rows(self._job(query))

    # --- Brownfield Methods ---
    def brownfield_summary(self, scope: str = "organization", project_id: str | None = None):
        where_clause, params = self._scope_filter(scope, project_id, "project_id")
        prefix = "WHERE" if not where_clause else "AND"
        query = f"""
        WITH plan_counts AS (SELECT run_id, COUNT(*) AS planned_total FROM `{self.dataset}.remediation_plan` {where_clause} GROUP BY run_id),
        latest_execution AS (SELECT run_id, status, ROW_NUMBER() OVER(PARTITION BY run_id, resource_name ORDER BY executed_at DESC) as rn FROM `{self.dataset}.remediation_execution` {where_clause} {prefix} execution_mode = 'BROWNFIELD'),
        exec_counts AS (SELECT run_id, COUNTIF(status='SUCCESS') AS completed, COUNTIF(status='FAILED') AS failed, COUNTIF(status='IN_PROGRESS') AS in_progress FROM latest_execution WHERE rn = 1 GROUP BY run_id)
        SELECT SUM(p.planned_total) AS planned, SUM(COALESCE(e.completed, 0)) AS completed, SUM(COALESCE(e.failed, 0)) AS failed, 
        SUM(p.planned_total - COALESCE(e.completed, 0) - COALESCE(e.failed, 0) - COALESCE(e.in_progress, 0)) AS remaining
        FROM plan_counts p LEFT JOIN exec_counts e ON p.run_id = e.run_id
        """
        row = self._first(self._job(query, params))
        total_completed = row.completed or 0
        total_failed = row.failed or 0
        total_executed = total_completed + total_failed
        return {
            "planned": row.planned or 0, "completed": total_completed, "failed": total_failed, "remaining": row.remaining or 0,
            "success_rate": round((total_completed / total_executed) * 100, 2) if total_executed > 0 else 100.0,
        }