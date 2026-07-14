from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_labels():

    return {
        "environment": "dev",
        "owner": "platform",
    }


@pytest.fixture
def mock_resource():

    resource = MagicMock()

    resource.name = (
        "projects/test-project/zones/europe-west2-a/instances/test-instance"
    )

    resource.asset_type = (
        "compute.googleapis.com/Instance"
    )

    resource.project = "test-project"

    resource.location = "europe-west2-a"

    resource.labels = {}

    return resource