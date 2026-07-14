from google.cloud import kms_v1
from google.protobuf.field_mask_pb2 import FieldMask

import config

from clients.base import ResourceClient
from models.resource import Resource
from utils.kms import parse_crypto_key_name


class KmsClient(ResourceClient):
    """Cloud KMS CryptoKey resource adapter."""

    def __init__(self):
        self.client = kms_v1.KeyManagementServiceClient()

    def supports(
        self,
        asset_type: str,
    ):
        return (
            asset_type
            == "cloudkms.googleapis.com/CryptoKey"
        )

    def labels(
        self,
        resource,
    ):
        crypto_key = self.client.get_crypto_key(
            request={
                "name": resource.name.replace(
                    "//cloudkms.googleapis.com/",
                    "",
                    1,
                )
            }
        )

        return dict(
            crypto_key.labels or {}
        )

    def get(
        self,
        resource_name: str,
    ) -> Resource:
        crypto_key = self.client.get_crypto_key(
            request={
                "name": resource_name.replace(
                    "//cloudkms.googleapis.com/",
                    "",
                    1,
                )
            }
        )

        info = parse_crypto_key_name(
            resource_name
        )

        return Resource(
            asset_type="cloudkms.googleapis.com/CryptoKey",
            name=resource_name,
            project=info["project"],
            location=info["location"],
            labels=dict(
                crypto_key.labels or {}
            ),
            tags={},
        )

    def apply_labels(
        self,
        resource,
        labels: dict,
    ):
        crypto_key = self.client.get_crypto_key(
            request={
                "name": resource.name.replace(
                    "//cloudkms.googleapis.com/",
                    "",
                    1,
                )
            }
        )

        existing = dict(
            crypto_key.labels or {}
        )

        if config.PRESERVE_EXISTING_LABELS:
            merged = existing.copy()

            for key, value in labels.items():
                if key not in merged:
                    merged[key] = value
        else:
            merged = existing.copy()
            merged.update(labels)

        if merged == existing:
            return True

        crypto_key.labels = merged

        operation = self.client.update_crypto_key(
            request={
                "crypto_key": crypto_key,
                "update_mask": FieldMask(
                    paths=["labels"],
                ),
            }
        )

        return operation