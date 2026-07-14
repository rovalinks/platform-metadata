from unittest.mock import MagicMock
from unittest.mock import patch

from services.adapter import AdapterService


@patch("services.adapter.ProjectClient")
@patch("services.adapter.SecretManagerClient")
@patch("services.adapter.GkeClient")
@patch("services.adapter.PubSubClient")
@patch("services.adapter.ArtifactRegistryClient")
@patch("services.adapter.CloudSqlClient")
@patch("services.adapter.StorageClient")
@patch("services.adapter.BigQueryReservationClient")
@patch("services.adapter.BigQueryClient")
@patch("services.adapter.ComputeClient")
def test_adapter(
    mock_compute,
    mock_bigquery,
    mock_reservation,
    mock_storage,
    mock_sql,
    mock_artifact,
    mock_pubsub,
    mock_gke,
    mock_secret,
    mock_project,
):

    clients = [
        mock_compute,
        mock_bigquery,
        mock_reservation,
        mock_storage,
        mock_sql,
        mock_artifact,
        mock_pubsub,
        mock_gke,
        mock_secret,
        mock_project,
    ]

    for client in clients:

        instance = MagicMock()

        instance.supports.return_value = False

        client.return_value = instance

    compute = mock_compute.return_value

    compute.supports.side_effect = (
        lambda asset: asset
        == "compute.googleapis.com/Instance"
    )

    adapter = AdapterService()

    assert (
        adapter.client_for(
            "compute.googleapis.com/Instance"
        )
        == compute
    )

    assert adapter.client_for("foo") is None