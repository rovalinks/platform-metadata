import os

# -------------------------------------------------------------------------
# Inject dummy environment variables for local testing
# This must happen BEFORE any cloudrun modules are imported so config.py 
# doesn't crash during Pytest's collection phase.
# -------------------------------------------------------------------------

os.environ["TAG_PARENT"] = "organizations/321880981428"
os.environ["PROJECT_ID"] = "platform-metadata"
os.environ["REGION"] = "us-central1"
os.environ["TASK_QUEUE"] = "test-queue"
os.environ["CLOUD_RUN_URL"] = "https://test-governance-engine-url.run.app"
os.environ["SERVICE_ACCOUNT_EMAIL"] = "metadata-governance@platform-metadata.iam.gserviceaccount.com"
os.environ["REGISTRY_BUCKET"] = "test-registry-bucket"

# Optional variables you can set just to be safe
os.environ["BIGQUERY_DATASET"] = "test_governance_dataset"
os.environ["DRY_RUN"] = "true"  # Good practice for tests