def to_full_resource_name(
    resource_name: str,
) -> str:
    """
    Converts a resource name into a Cloud Asset
    full resource name if required.
    """

    if resource_name.startswith("//"):
        return resource_name

    #
    # Pub/Sub
    #
    if resource_name.startswith("projects/") and "/topics/" in resource_name:
        return f"//pubsub.googleapis.com/{resource_name}"

    #
    # Unknown.
    #
    return f"//{resource_name.lstrip('/')}"