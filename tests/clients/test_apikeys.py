from clients.apikeys import ApiKeysClient


def test_supports_apikey():

    client = ApiKeysClient()

    assert client.supports(
        "apikeys.googleapis.com/Key"
    )


def test_unknown():

    client = ApiKeysClient()

    assert not client.supports(
        "foo"
    )
