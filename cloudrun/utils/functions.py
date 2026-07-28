def parse_function_name(resource_name: str):
    """
    Converts Cloud Asset Inventory resource name into the
    Cloud Functions API resource name.
    """

    name = resource_name.lstrip("/")

    if name.split("/")[0] == "cloudfunctions.googleapis.com":
        name = name.replace(
            "cloudfunctions.googleapis.com/",
            "",
            1,
        )

    return name