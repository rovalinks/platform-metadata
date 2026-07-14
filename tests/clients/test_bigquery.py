from unittest.mock import patch

from clients.bigquery import BigQueryClient


@patch("clients.bigquery.bigquery.Client")
def test_supports_dataset(
    mock_client,
):

    client = BigQueryClient()

    assert client.supports(
        "bigquery.googleapis.com/Dataset"
    )


@patch("clients.bigquery.bigquery.Client")
def test_supports_table(
    mock_client,
):

    client = BigQueryClient()

    assert client.supports(
        "bigquery.googleapis.com/Table"
    )


@patch("clients.bigquery.bigquery.Client")
def test_supports_unknown(
    mock_client,
):

    client = BigQueryClient()

    assert client.supports(
        "foo"
    ) is False