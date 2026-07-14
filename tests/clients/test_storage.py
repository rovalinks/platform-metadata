from unittest.mock import patch

from clients.storage import StorageClient


@patch("clients.storage.storage.Client")
def test_supports_bucket(
    mock_client,
):

    client = StorageClient()

    assert client.supports(
        "storage.googleapis.com/Bucket"
    )


@patch("clients.storage.storage.Client")
def test_supports_unknown(
    mock_client,
):

    client = StorageClient()

    assert client.supports(
        "foo"
    ) is False