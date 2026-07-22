import os

# Resilient getter that NEVER crashes Gunicorn
def get_env(key: str, default: str = "") -> str:
    value = os.getenv(key)
    return value if value else default

# Core Configuration
PROJECT_ID = get_env("PROJECT_ID", "platform-metadata")
REGION = get_env("REGION", "europe-west2")
TAG_PARENT = get_env("TAG_PARENT", "")
TASK_QUEUE = get_env("TASK_QUEUE", "metadata-remediation")
CLOUD_RUN_URL = get_env("CLOUD_RUN_URL", "PENDING_FIRST_DEPLOY")
SERVICE_ACCOUNT_EMAIL = get_env("SERVICE_ACCOUNT_EMAIL", "")
REGISTRY_BUCKET = get_env("REGISTRY_BUCKET", "platform-metadata-registry")
REGISTRY_PREFIX = get_env("REGISTRY_PREFIX", "applications")
BIGQUERY_DATASET = get_env("BIGQUERY_DATASET", "metadata_governance")

# Tuning Configuration
REGISTRY_CACHE_TTL = int(get_env("REGISTRY_CACHE_TTL", "60"))
DISCOVERY_RETENTION_DAYS = int(get_env("DISCOVERY_RETENTION_DAYS", "10"))
MAX_PARALLEL_WORKERS = int(get_env("MAX_PARALLEL_WORKERS", "10"))
REMEDIATION_BATCH_SIZE = int(get_env("REMEDIATION_BATCH_SIZE", "500"))
LOG_LEVEL = get_env("LOG_LEVEL", "WARNING")

# Booleans (Strict parsing)
DRY_RUN = get_env("DRY_RUN", "false").lower() in ("true", "1", "yes")
PRESERVE_EXISTING_LABELS = get_env("PRESERVE_EXISTING_LABELS", "true").lower() in ("true", "1", "yes")

# Lists
EXCLUDED_BUCKETS = [
    b.strip() for b in os.getenv("EXCLUDED_BUCKETS", "").split(",") if b.strip()
]

# Constants
REGISTRY_PREFIX = "applications"
SNAPSHOT_PREFIX = "snapshots"
RESOURCE_SNAPSHOT_PREFIX = f"{SNAPSHOT_PREFIX}/inventory"
COMPLIANCE_SNAPSHOT_PREFIX = f"{SNAPSHOT_PREFIX}/compliance"



# import os

# def get_env_or_raise(key: str) -> str:
#     value = os.getenv(key)
#     if not value:
#         raise RuntimeError(f"Missing mandatory environment variable: {key}")
#     return value

# # Mandatory Configuration (Fail fast if missing)
# TAG_PARENT = get_env_or_raise("TAG_PARENT")
# PROJECT_ID = get_env_or_raise("PROJECT_ID")
# REGION = get_env_or_raise("REGION")
# TASK_QUEUE = get_env_or_raise("TASK_QUEUE")
# CLOUD_RUN_URL = os.getenv("CLOUD_RUN_URL", "PENDING_FIRST_DEPLOY")
# SERVICE_ACCOUNT_EMAIL = get_env_or_raise("SERVICE_ACCOUNT_EMAIL")
# REGISTRY_BUCKET = get_env_or_raise("REGISTRY_BUCKET")
# BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET")

# # Optional Configuration (With defaults)
# REGISTRY_CACHE_TTL = int(os.getenv("REGISTRY_CACHE_TTL", "60"))
# DISCOVERY_RETENTION_DAYS = int(os.getenv("DISCOVERY_RETENTION_DAYS", "10"))
# MAX_PARALLEL_WORKERS = int(os.getenv("MAX_PARALLEL_WORKERS", "10"))
# REMEDIATION_BATCH_SIZE = int(os.getenv("REMEDIATION_BATCH_SIZE", "500"))
# LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")

# # Booleans
# DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
# PRESERVE_EXISTING_LABELS = os.getenv("PRESERVE_EXISTING_LABELS", "true").lower() == "true"

# # Lists
# EXCLUDED_BUCKETS = [
#     b.strip() for b in os.getenv("EXCLUDED_BUCKETS", "").split(",") if b.strip()
# ]

# # Constants
# REGISTRY_PREFIX = "applications"
# SNAPSHOT_PREFIX = "snapshots"
# RESOURCE_SNAPSHOT_PREFIX = f"{SNAPSHOT_PREFIX}/inventory"
# COMPLIANCE_SNAPSHOT_PREFIX = f"{SNAPSHOT_PREFIX}/compliance"
