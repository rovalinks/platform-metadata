from utils.supported_resources import SUPPORTED_LABEL_RESOURCES, SUPPORTED_TAG_RESOURCES


class CapabilityService:
    """
    Determines which governance mechanism
    a resource supports.
    """

    @staticmethod
    def supports_labels(asset_type: str,) -> bool:
        return asset_type in SUPPORTED_LABEL_RESOURCES

    @staticmethod
    def supports_tags(asset_type: str,) -> bool:
        return asset_type in SUPPORTED_TAG_RESOURCES