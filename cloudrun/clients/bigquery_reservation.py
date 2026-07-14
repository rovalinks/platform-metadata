from clients.base import ResourceClient
from models.resource import Resource


class BigQueryReservationClient(ResourceClient):
    """Placeholder until Reservation implementation is added."""

    def supports(
        self,
        asset_type: str,
    ):

        return False

    def labels(
        self,
        resource,
    ):

        return {}

    def get(
        self,
        resource_name: str,
    ) -> Resource:

        raise NotImplementedError(
            "BigQuery Reservation not implemented yet."
        )

    def apply_labels(
        self,
        resource,
        labels: dict,
    ):

        raise NotImplementedError(
            "BigQuery Reservation not implemented yet."
        )