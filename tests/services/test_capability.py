from services.capability import CapabilityService


def test_compute_instance_supported():

    assert CapabilityService.supports_labels(
        "compute.googleapis.com/Instance"
    )


def test_bigquery_supported():

    assert CapabilityService.supports_labels(
        "bigquery.googleapis.com/Dataset"
    )


def test_storage_supported():

    assert CapabilityService.supports_labels(
        "storage.googleapis.com/Bucket"
    )