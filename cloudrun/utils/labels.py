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


def reconcile_labels(existing_labels: dict, schema_labels: dict) -> dict:
    """
    Merges schema_labels into existing_labels while preserving 
    customer-managed labels.
    """
    # Start with existing labels to ensure customer-managed keys are kept
    final_labels = existing_labels.copy() if existing_labels else {}
    
    # Update with schema_labels (this overwrites only schema-enforced keys)
    final_labels.update(schema_labels)
    
    return final_labels