def parse_dataset_name(
    resource_name: str,
):
    """Parses a BigQuery dataset resource name."""

    #
    # Brownfield:
    # //bigquery.googleapis.com/projects/<project>/datasets/<dataset>
    #
    if resource_name.startswith("//"):

        parts = resource_name.split("/")

        return {
            "project": parts[4],
            "dataset": parts[6],
        }

    #
    # Greenfield:
    # projects/<project>/datasets/<dataset>
    #
    parts = resource_name.split("/")

    return {
        "project": parts[1],
        "dataset": parts[3],
    }


def parse_table_name(
    resource_name: str,
):
    """
    Parses a BigQuery table resource name.

    Brownfield:
    //bigquery.googleapis.com/projects/<project>/datasets/<dataset>/tables/<table>
    """

    parts = resource_name.split("/")

    return {
        "project": parts[4],
        "dataset": parts[6],
        "table": parts[8],
    }