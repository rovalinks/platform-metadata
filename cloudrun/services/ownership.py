from utils.logger import logger
class OwnershipService:
    def build(self, existing: dict, desired: dict, allowed: list[str]) -> dict:
        existing = existing or {}
        desired = desired or {}
        allowed = set(allowed or [])
        final = existing.copy()
        for key in allowed:
            if key in desired:
                final[key] = desired[key]
            elif key in final:
                final.pop(key, None)
        logger.debug("Existing=%s Allowed=%s Desired=%s Final=%s", existing, sorted(allowed), desired, final)
        return final