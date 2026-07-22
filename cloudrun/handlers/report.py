from flask import jsonify, request

from services.context import RequestContext
from services.governance import GovernanceService
from services.report import ReportService
from utils.org_helper import get_all_active_projects

def report():
    """
    Generates compliance reports.

    GET /report
        Report every registered project.

    GET /report?project=<project-id>
        Report a single project.
    """

    context = RequestContext()
    governance = GovernanceService()
    
    # FIX: Pass both required arguments to the ReportService constructor
    service = ReportService(context.repository, context.discovery)

    project_id = request.args.get("project")
    reports = []

    if project_id:
        # Assuming service.report(project_id) returns a single report object
        reports.append(service.report(project_id))

    else:
        for project in governance.projects():
            # Collecting individual report objects
            reports.append(
                service.report(
                    project["projectId"]
                )
            )

    return jsonify(
        [
            report.to_dict()
            for report in reports
        ]
    )

def get_projects():
    """
    GET /reports/projects
    Returns a list of all active projects in the Organization for the UI dropdown.
    """
    try:
        projects = get_all_active_projects()
        return jsonify({"projects": projects, "count": len(projects)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500