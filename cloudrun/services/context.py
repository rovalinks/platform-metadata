from services.discovery import DiscoveryService
from repositories.report_repository import ReportRepository


class RequestContext:
    """Shared services for a single request."""

    def __init__(self):

        self.discovery = DiscoveryService()
        self.repository = ReportRepository()