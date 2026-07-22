from flask import request, jsonify
from services.brownfield import BrownfieldService
from utils.org_helper import get_all_active_projects

def brownfield():
    scope = request.args.get("scope", "project")
    project_id = request.args.get("project")

    projects_to_scan = []

    if scope == "organization":
        # THE NUKE BUTTON: Fetch all projects!
        projects_to_scan = get_all_active_projects()
    elif project_id:
        # Single project scan
        projects_to_scan = [project_id]
    else:
        return jsonify({"error": "Must provide either ?scope=organization or ?project=project-id"}), 400

    if not projects_to_scan:
        return jsonify({"error": "No valid projects found to scan."}), 400

    service = BrownfieldService()
    result = service.execute(project_ids=projects_to_scan)

    return jsonify(result)