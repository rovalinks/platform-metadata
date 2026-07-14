def parse_crypto_key_name(resource_name: str):

    parts = resource_name.split("/")

    return {
        "project": parts[4],
        "location": parts[6],
        "key_ring": parts[8],
        "crypto_key": parts[10],
    }