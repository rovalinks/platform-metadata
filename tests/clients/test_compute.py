from clients.compute import ComputeClient


def test_supports_instance():

    client = ComputeClient()

    assert client.supports(
        "compute.googleapis.com/Instance"
    )


def test_supports_disk():

    client = ComputeClient()

    assert client.supports(
        "compute.googleapis.com/Disk"
    )


def test_supports_unknown():

    client = ComputeClient()

    assert (
        client.supports(
            "foo.googleapis.com/Test"
        )
        is False
    )