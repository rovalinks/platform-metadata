from unittest.mock import patch

from clients.project import ProjectClient


@patch("clients.project.ProjectsClient")
def test_supports_project(
    mock_client,
):

    client = ProjectClient()

    assert client.supports(
        "cloudresourcemanager.googleapis.com/Project"
    )


@patch("clients.project.ProjectsClient")
def test_supports_unknown(
    mock_client,
):

    client = ProjectClient()

    assert client.supports(
        "foo"
    ) is False