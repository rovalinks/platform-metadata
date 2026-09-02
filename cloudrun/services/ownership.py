from utils.logger import logger
class OwnershipService:
    def build(self, existing: dict, desired: dict, allowed: list) -> dict:
        merged = dict(existing) if existing else {}
        
        for key, value in desired.items():
            # PRESERVE: Never overwrite an existing label value set by a user
            if key not in merged:
                merged[key] = value
                
        return merged