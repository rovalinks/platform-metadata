from clients.kms import KmsClient


def test_supports_crypto_key():

    client = KmsClient()

    assert client.supports(
        "cloudkms.googleapis.com/CryptoKey"
    )


def test_unknown():

    client = KmsClient()

    assert not client.supports(
        "foo"
    )
