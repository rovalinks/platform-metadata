from utils.logger import logger


class OwnershipService:
    """
    Determines which labels are managed by the platform.

    Customer-managed labels are never modified.

    Platform-managed labels always follow the registry.
    """

    def build(
        self,
        existing: dict,
        desired: dict,
        managed: list[str],
    ) -> dict:
        """
        Build the final label set to apply.

        existing:
            Current labels on the resource.

        desired:
            Labels from the governance registry.

        managed:
            Labels previously created by this platform.
        """

        existing = existing or {}
        desired = desired or {}
        managed = set(managed or [])

        final = existing.copy()

        #
        # Remove labels that we previously created
        # but have since removed from the registry.
        #
        for key in managed:
            if key not in desired:
                final.pop(key, None)

        #
        # Update only labels owned by this platform.
        #
        for key in managed:
            if key in desired:
                final[key] = desired[key]

        #
        # Add new registry labels that don't already
        # exist on the resource.
        #
        for key, value in desired.items():
            if key not in existing:
                final[key] = value

        logger.debug(
            "Existing=%s Managed=%s Desired=%s Final=%s",
            existing,
            sorted(managed),
            desired,
            final,
        )

        return final

    def managed_keys(
        self,
        existing: dict,
        desired: dict,
        managed: list[str],
    ) -> list[str]:
        """
        Returns the new list of platform-managed labels
        after remediation completes successfully.
        """

        existing = existing or {}
        desired = desired or {}
        keys = set(managed or [])

        #
        # Any label we create becomes platform-managed.
        #
        for key in desired:
            if key not in existing:
                keys.add(key)

        #
        # Labels removed from the registry are no
        # longer platform-managed.
        #
        keys.intersection_update(desired.keys())

        return sorted(keys)

    def is_platform_managed(
        self,
        label: str,
        managed: list[str],
    ) -> bool:
        """
        Returns True if the platform owns the label.
        """

        return label in set(managed or [])

    def customer_labels(
        self,
        existing: dict,
        managed: list[str],
    ) -> dict:
        """
        Returns customer-managed labels only.
        """

        managed = set(managed or [])

        return {
            key: value
            for key, value in (existing or {}).items()
            if key not in managed
        }

    def platform_labels(
        self,
        existing: dict,
        managed: list[str],
    ) -> dict:
        """
        Returns platform-managed labels only.
        """

        managed = set(managed or [])

        return {
            key: value
            for key, value in (existing or {}).items()
            if key in managed
        }