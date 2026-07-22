from handlers.health import health
from handlers.discovery import discover
from handlers.compliance import compliance
from handlers.verify import verify
from handlers.report import report, get_projects
from handlers.execute import execute
from handlers.enforce import enforce
from handlers.plan import plan
from handlers.runs import runs
from handlers.worker import worker
from handlers.history import history
from handlers.dashboard import dashboard
from handlers.metrics import metrics
from handlers.greenfield import greenfield
from handlers.brownfield import brownfield
from handlers.run_status import run_status
from handlers.compliance_report import compliance_report
from handlers.resources import resources
from handlers.non_compliant import non_compliant

class Dispatcher:

    @staticmethod
    def dispatch(
        route: str,
        payload=None,
        **kwargs,
    ):

        if route == "health":
            return health()

        if route == "discover":
            return discover()

        if route == "compliance":
            return compliance()

        if route == "compliance_report":
            return compliance_report()  

        if route == "verify":
            return verify()

        if route == "report":
            return report()

        if route == "projects_list":
            return get_projects()

        if route == "runs":
            return runs()

        if route == "plan":
            return plan()

        if route == "execute":
            return execute()

        if route == "worker":
            return worker()
            
        if route == "enforce":
            return enforce()

        if route == "history":
            return history()

        if route == "dashboard":
            return dashboard()

        if route == "metrics":
            return metrics()

        if route == "greenfield":
            return greenfield(payload)

        if route == "brownfield":
            return brownfield()

        if route == "run_status":
            return run_status(
                kwargs["run_id"]
            )

        if route == "run":
            return run(kwargs["run_id"])

        if route == "resources":
            return resources()
        
        if route == "non_compliant":
            return non_compliant()

        return {
            "error": "Endpoint not found"
        }, 404

# from handlers.health import health
# from handlers.discovery import discover
# from handlers.compliance import compliance
# from handlers.verify import verify
# from handlers.report import report
# from handlers.execute import execute
# from handlers.enforce import enforce
# from handlers.plan import plan
# from handlers.runs import runs
# from handlers.worker import worker
# from handlers.history import history
# from handlers.dashboard import dashboard
# from handlers.metrics import metrics
# from handlers.greenfield import greenfield
# from handlers.brownfield import brownfield
# from handlers.run_status import run_status
# from handlers.compliance_report import compliance_report
# from handlers.resources import resources
# from handlers.non_compliant import non_compliant

# class Dispatcher:

#     @staticmethod
#     def dispatch(
#         route: str,
#         payload=None,
#         **kwargs,
#     ):

#         if route == "health":
#             return health()

#         if route == "discover":
#             return discover()

#         if route == "compliance":
#             return compliance()

#         if route == "compliance_report":
#             return compliance_report()  

#         if route == "verify":
#             return verify()

#         if route == "report":
#             return report()

#         if route == "runs":
#             return runs()

#         if route == "plan":
#             return plan()

#         if route == "execute":
#             return execute()

#         if route == "worker":
#             return worker()
            
#         if route == "enforce":
#             return enforce()

#         if route == "history":
#             return history()

#         if route == "dashboard":
#             return dashboard()

#         if route == "metrics":
#             return metrics()

#         if route == "greenfield":
#             return greenfield(payload)

#         if route == "brownfield":
#             return brownfield()

#         if route == "run_status":
#             return run_status(
#                 kwargs["run_id"]
#             )

#         if route == "run":
#             return run(kwargs["run_id"])

#         if route == "resources":
#             return resources()
        
#         if route == "non_compliant":
#             return non_compliant()

#         return {
#             "error": "Endpoint not found"
#         }, 404