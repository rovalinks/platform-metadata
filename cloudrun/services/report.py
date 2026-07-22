from google.cloud import bigquery
from config import config
from utils.logger import logger
from models.report import GovernanceReport
from services.discovery import DiscoveryService
from services.compliance import ComplianceService
from services.enforcement import EnforcementService

class ReportService:

    def __init__(self, repository, discovery):
        self.repository = repository 
        self.discovery = discovery
        self.compliance = ComplianceService()
        self.enforcement = EnforcementService(discovery)

    def run(self, run_id: str):
        """
        Returns a complete summary for a remediation run.
        """
        return self.repository.remediation_run_summary(run_id)

    def get_dashboard_metrics(self, run_id: str, scope: str = "organization", project_id: str = None):
        
        # 1. FIX THE SCOPE FILTER
        # If Organization scope is selected, just query the run_id across ALL projects.
        scope_filter = ""
        query_params = [bigquery.ScalarQueryParameter("run_id", "STRING", run_id)]
        
        if scope == "project" and project_id:
            scope_filter = "AND project_id = @project_id"
            query_params.append(bigquery.ScalarQueryParameter("project_id", "STRING", project_id))

        # 2. FIX THE COMPLIANCE MATH
        # Ensure we are counting the raw execution statuses correctly.
        summary_query = f"""
            SELECT 
                COUNT(*) as total_evaluated,
                COUNTIF(status = 'SUCCESS' OR is_compliant = TRUE) as compliant,
                COUNTIF(status != 'SUCCESS' AND is_compliant = FALSE) as non_compliant
            FROM `{config.PROJECT_ID}.{config.BIGQUERY_DATASET}.compliance_evaluations`
            WHERE run_id = @run_id {scope_filter}
        """
        
        # 3. FIX THE PROJECT BREAKDOWN TABLE
        project_query = f"""
            SELECT 
                project_id,
                COUNT(*) as total,
                COUNTIF(status = 'SUCCESS' OR is_compliant = TRUE) as compliant,
                COUNTIF(status != 'SUCCESS' AND is_compliant = FALSE) as non_compliant
            FROM `{config.PROJECT_ID}.{config.BIGQUERY_DATASET}.compliance_evaluations`
            WHERE run_id = @run_id {scope_filter}
            GROUP BY project_id
        """

        # 4. FIX THE SERVICE BREAKDOWN TABLE
        service_query = f"""
            SELECT 
                asset_type as service,
                COUNT(*) as total,
                COUNTIF(status = 'SUCCESS' OR is_compliant = TRUE) as compliant,
                COUNTIF(status != 'SUCCESS' AND is_compliant = FALSE) as non_compliant
            FROM `{config.PROJECT_ID}.{config.BIGQUERY_DATASET}.compliance_evaluations`
            WHERE run_id = @run_id {scope_filter}
            GROUP BY asset_type
        """

        # Client execution logic placeholder or return structure matching implementation
        client = bigquery.Client()
        
        summary_job = client.query(summary_query, job_config=bigquery.QueryJobConfig(query_parameters=query_params))
        summary_results = [dict(row) for row in summary_job.result()]

        project_job = client.query(project_query, job_config=bigquery.QueryJobConfig(query_parameters=query_params))
        project_results = [dict(row) for row in project_job.result()]

        service_job = client.query(service_query, job_config=bigquery.QueryJobConfig(query_parameters=query_params))
        service_results = [dict(row) for row in service_job.result()]

        return {
            "summary": summary_results[0] if summary_results else {},
            "by_project": project_results,
            "by_service": service_results
        }

    def report(self, project_id: str):
        logger.info("Generating governance report")

        # Step 1: Discover resources first
        resources = self.discovery.discover(project_id)
        
        # Step 2: Pass resources to compliance and enforcement
        compliance = self.compliance.evaluate(resources)
        
        # Note: Depending on your EnforcementService implementation, 
        # you may need to pass resources here if it still internally uses project_id
        actions = self.enforcement.plan(project_id)

        compliant = sum(
            1 for item in compliance
            if item.compliant
        )

        return GovernanceReport(
            project=project_id,
            total_resources=len(resources),
            supported_resources=len(compliance),
            compliant_resources=compliant,
            non_compliant_resources=len(compliance) - compliant,
            enforcement_candidates=len(actions),
            compliance_percentage=(
                round(
                    compliant / len(compliance) * 100,
                    2,
                )
                if compliance
                else 100.0
            ),
        )

# from utils.logger import logger
# from models.report import GovernanceReport
# from services.discovery import DiscoveryService
# from services.compliance import ComplianceService
# from services.enforcement import EnforcementService

# class ReportService:

#     def __init__(self, repository, discovery):
#         self.repository = repository 
#         self.discovery = discovery
#         self.compliance = ComplianceService()
#         self.enforcement = EnforcementService(discovery)

#     def run(self, run_id: str):
#         """
#         Returns a complete summary for a remediation run.
#         """
#         return self.repository.remediation_run_summary(run_id)

#     def report(self, project_id: str):
#         logger.info("Generating governance report")

#         # Step 1: Discover resources first
#         resources = self.discovery.discover(project_id)
        
#         # Step 2: Pass resources to compliance and enforcement
#         compliance = self.compliance.evaluate(resources)
        
#         # Note: Depending on your EnforcementService implementation, 
#         # you may need to pass resources here if it still internally uses project_id
#         actions = self.enforcement.plan(project_id)

#         compliant = sum(
#             1 for item in compliance
#             if item.compliant
#         )

#         return GovernanceReport(
#             project=project_id,
#             total_resources=len(resources),
#             supported_resources=len(compliance),
#             compliant_resources=compliant,
#             non_compliant_resources=len(compliance) - compliant,
#             enforcement_candidates=len(actions),
#             compliance_percentage=(
#                 round(
#                     compliant / len(compliance) * 100,
#                     2,
#                 )
#                 if compliance
#                 else 100.0
#             ),
#         )