import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

#
# Only load .env for local development.
# Cloud Run receives configuration from environment variables.
#
dotenv_file = BASE_DIR / ".env"

if dotenv_file.exists():
    load_dotenv(dotenv_file)

def get_env_or_raise(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(f"Missing mandatory environment variable: {key}")
    return value

# Mandatory Configuration (Fail fast if missing)
TAG_PARENT = get_env_or_raise("TAG_PARENT")
PROJECT_ID = get_env_or_raise("PROJECT_ID")
REGION = get_env_or_raise("REGION")
TASK_QUEUE = get_env_or_raise("TASK_QUEUE")
CLOUD_RUN_URL = get_env_or_raise("CLOUD_RUN_URL")
SERVICE_ACCOUNT_EMAIL = get_env_or_raise("SERVICE_ACCOUNT_EMAIL")
REGISTRY_BUCKET = get_env_or_raise("REGISTRY_BUCKET")

# Optional Configuration (With defaults)
BIGQUERY_DATASET = os.getenv("BIGQUERY_DATASET", "metadata_governance_dataset")
REGISTRY_CACHE_TTL = int(os.getenv("REGISTRY_CACHE_TTL", "300"))
DISCOVERY_RETENTION_DAYS = int(os.getenv("DISCOVERY_RETENTION_DAYS", "10"))
MAX_PARALLEL_WORKERS = int(os.getenv("MAX_PARALLEL_WORKERS", "10"))
REMEDIATION_BATCH_SIZE = int(os.getenv("REMEDIATION_BATCH_SIZE", "500"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Booleans
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"
PRESERVE_EXISTING_LABELS = os.getenv("PRESERVE_EXISTING_LABELS", "true").lower() == "true"

# Lists
EXCLUDED_BUCKETS = [
    b.strip() for b in os.getenv("EXCLUDED_BUCKETS", "").split(",") if b.strip()
]

# Constants
REGISTRY_PREFIX = "applications"
SNAPSHOT_PREFIX = "snapshots"
RESOURCE_SNAPSHOT_PREFIX = f"{SNAPSHOT_PREFIX}/inventory"
COMPLIANCE_SNAPSHOT_PREFIX = f"{SNAPSHOT_PREFIX}/compliance"
