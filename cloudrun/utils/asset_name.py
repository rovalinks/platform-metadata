import re

def asset_display_name(asset_type: str) -> str:
    """
    Converts Cloud Asset Inventory asset types into human-readable names
    without any hardcoded mappings.
    """

    try:
        service, resource = asset_type.split("/")
    except ValueError:
        return asset_type

    # compute.googleapis.com -> compute
    service = service.split(".")[0]

    # Compute
    service = re.sub(r"(?<!^)(?=[A-Z])", " ", service)
    service = service.replace("_", " ").replace("-", " ")
    service = service.title()

    # InstanceTemplate -> Instance Template
    resource = re.sub(r"(?<!^)(?=[A-Z])", " ", resource)

    # Avoid "Project Project"
    if resource.lower() == service.lower():
        return resource

    return f"{service} {resource}"