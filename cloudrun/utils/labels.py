import re


def normalize_label_value(value: str) -> str:
    """
    Convert registry values into valid Google Cloud label values.

    Google Cloud labels only allow lowercase letters, numbers,
    hyphens and underscores.
    """

    value = value.lower()

    if "@" in value:
        value = value.split("@")[0]

    value = value.replace(" ", "-")

    value = re.sub(r"[^a-z0-9_-]", "-", value)

    value = re.sub(r"-+", "-", value)

    return value.strip("-")