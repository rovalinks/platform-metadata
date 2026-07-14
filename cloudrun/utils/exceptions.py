from google.api_core import exceptions as gcp_exceptions


class MetadataGovernanceError(Exception):
    """Base exception for the metadata governance platform."""


def format_gcp_exception(error: Exception) -> str:

    if isinstance(error, gcp_exceptions.GoogleAPICallError):

        return (
            f"{error.__class__.__name__}: {error}"
        )

    return str(error)