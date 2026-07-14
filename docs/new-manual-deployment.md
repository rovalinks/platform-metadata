# Enterprise Metadata Governance Platform

# Infrastructure Deployment Guide

Version 1.0

---

# Purpose

This document provisions the Google Cloud infrastructure required to host the Enterprise Metadata Governance Platform.

At the end of this guide the following components will exist.

- Google Cloud Project
- Billing
- Required APIs
- Service Accounts
- IAM
- Workload Identity Federation
- Artifact Registry

No application code is deployed in this document.

---

# Deployment Architecture

```
Developer

        │

        ▼

GitHub Repository

        │

        ▼

Workload Identity Federation

        │

        ▼

Google Cloud

        │

        ▼

Artifact Registry

        │

        ▼

Cloud Run
```

---

# Prerequisites

Install

- Google Cloud SDK
- Git
- GitHub CLI (optional)

Authenticate

```bash
gcloud auth login

gcloud auth application-default login
```

---

# Required Variables

```bash
export PROJECT_ID=platform-metadata

export REGION=europe-west2

export SERVICE_ACCOUNT=metadata-governance

export REPOSITORY_NAME=metadata-governance
```

---

# Step 1

Select Project

```bash
gcloud config set project $PROJECT_ID
```

Verify

```bash
gcloud config get-value project
```

---

# Step 2

Verify Billing

```bash
gcloud beta billing projects describe $PROJECT_ID
```

Expected

```
billingEnabled: true
```

---

# Step 3

Enable Required APIs

```bash
gcloud services enable \
artifactregistry.googleapis.com \
bigquery.googleapis.com \
cloudasset.googleapis.com \
cloudbuild.googleapis.com \
cloudresourcemanager.googleapis.com \
eventarc.googleapis.com \
iam.googleapis.com \
iamcredentials.googleapis.com \
logging.googleapis.com \
pubsub.googleapis.com \
run.googleapis.com \
secretmanager.googleapis.com \
serviceusage.googleapis.com \
sqladmin.googleapis.com \
storage.googleapis.com
```

Verify

```bash
gcloud services list --enabled
```

---


# Step 4 & 5

Grant Runtime IAM Roles

Grant the runtime service account the required roles.

| Role | Purpose |
|-------|----------|
| Cloud Asset Viewer | Discovery |
| BigQuery Data Editor | Reporting |
| BigQuery Job User | Queries |
| Logging Viewer | Read Audit Logs |
| Pub/Sub Subscriber | Greenfield Processing |
| Storage Admin | Bucket Remediation |
| Compute Admin | VM/Disk Remediation |
| Cloud SQL Admin | Cloud SQL Remediation |
| Secret Manager Admin | Secret Remediation |
| Artifact Registry Admin | Repository Remediation |
| Cloud KMS Admin | Key Remediation |
| Resource Manager Tag User | Apply Tags |
| Resource Manager Tag Viewer | Read Tags |

Apply using:
apply-iam-permissions.sh
chmod +x apply-iam-permissions.sh
./apply-iam-permissions.sh

#!/usr/bin/env bash

# Exit immediately if any command fails
set -e

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ID="platform-metadata"

# Service Account Names
RUN_SA_NAME="metadata-governance"
EVENTARC_SA_NAME="eventarc-trigger"
CLOUDBUILD_SA_NAME="cloudbuild"

# Full Service Account Emails
RUN_SA="${RUN_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
EVENTARC_SA="${EVENTARC_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
CLOUDBUILD_SA="${CLOUDBUILD_SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "Using project: ${PROJECT_ID}"

# ==========================================
# HELPER FUNCTION: CREATE SA IF NOT EXISTS
# ==========================================
create_sa_if_not_exists() {
  local sa_name=$1
  local display_name=$2
  local email="${sa_name}@${PROJECT_ID}.iam.gserviceaccount.com"

  echo "Checking service account: ${email}..."
  if ! gcloud iam service-accounts describe "${email}" --project="${PROJECT_ID}" >/dev/null 2>&1; then
    echo "Creating service account: ${sa_name}..."
    gcloud iam service-accounts create "${sa_name}" \
      --project="${PROJECT_ID}" \
      --display-name="${display_name}" \
      --quiet
  else
    echo "Service account '${sa_name}' already exists. Skipping creation."
  fi
}

# ==========================================
# 1. CREATE SERVICE ACCOUNTS
# ==========================================
echo "Ensuring service accounts exist..."
create_sa_if_not_exists "${RUN_SA_NAME}" "Metadata Governance Cloud Run SA"
create_sa_if_not_exists "${EVENTARC_SA_NAME}" "Eventarc Trigger SA"
create_sa_if_not_exists "${CLOUDBUILD_SA_NAME}" "Cloud Build SA"

# ==========================================
# 2. CLOUD RUN RUNTIME PERMISSIONS
# ==========================================
echo "Applying Cloud Run runtime roles..."

RUNTIME_ROLES=(
  "roles/cloudasset.viewer"
  "roles/bigquery.jobUser"
  "roles/bigquery.dataEditor"
  "roles/bigquery.dataViewer"
  "roles/resourcemanager.tagUser"
  "roles/resourcemanager.tagViewer"
  "roles/logging.viewer"
  "roles/pubsub.subscriber"
  "roles/pubsub.viewer"
  "roles/storage.admin"
  "roles/compute.admin"
  "roles/cloudsql.admin"
  "roles/artifactregistry.admin"
  "roles/secretmanager.admin"
  "roles/cloudkms.admin"
)

for role in "${RUNTIME_ROLES[@]}"; do
  echo "Granting ${role} to ${RUN_SA}..."
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${RUN_SA}" \
    --role="${role}" \
    --quiet > /dev/null
done

# ==========================================
# 3. EVENTARC SERVICE ACCOUNT PERMISSIONS
# ==========================================
echo "Applying Eventarc receiver role..."
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${EVENTARC_SA}" \
  --role="roles/eventarc.eventReceiver" \
  --quiet > /dev/null

# ==========================================
# 4. CLOUD BUILD SERVICE ACCOUNT PERMISSIONS
# ==========================================
echo "Applying Cloud Build roles..."
CLOUDBUILD_ROLES=(
  "roles/cloudbuild.builds.editor"
  "roles/artifactregistry.writer"
)

for role in "${CLOUDBUILD_ROLES[@]}"; do
  echo "Granting ${role} to ${CLOUDBUILD_SA}..."
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${CLOUDBUILD_SA}" \
    --role="${role}" \
    --quiet > /dev/null
done

echo "Service accounts and IAM policy configurations completed successfully!"



---

# Step 6

Configure GitHub Workload Identity Federation

Create Workload Identity Pool

```bash
gcloud iam workload-identity-pools create github \
--location=global \
--display-name="GitHub Actions"
```

Retrieve Project Number

```bash
gcloud projects describe $PROJECT_ID \
--format="value(projectNumber)"
```

Create OIDC Provider

```bash
gcloud iam workload-identity-pools providers create-oidc github \
--location=global \
--workload-identity-pool=github \
--issuer-uri=https://token.actions.githubusercontent.com \
--attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
--attribute-condition="assertion.repository=='YOUR_GITHUB_ORG/YOUR_REPOSITORY'"
```

Allow GitHub to impersonate the runtime service account.

```bash
gcloud iam service-accounts add-iam-policy-binding \
metadata-governance@$PROJECT_ID.iam.gserviceaccount.com \
--role=roles/iam.workloadIdentityUser \
--member="principalSet://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/github/attribute.repository/YOUR_GITHUB_ORG/YOUR_REPOSITORY"
```

---

# Step 7

Configure GitHub Secrets

Repository Settings

Secrets and Variables

Actions

Create

| Secret | Value |
|----------|-------|
| WIF_PROVIDER | Workload Identity Provider Resource Name |
| WIF_SERVICE_ACCOUNT | metadata-governance@$PROJECT_ID.iam.gserviceaccount.com |

---

# Step 8

Create Artifact Registry

```bash
gcloud artifacts repositories create metadata-governance \
--repository-format=docker \
--location=$REGION \
--description="Enterprise Metadata Governance Images"
```

Verify

```bash
gcloud artifacts repositories list
```

Expected

```
metadata-governance
```

---

# Infrastructure Validation

Verify

✓ Project configured

✓ Billing enabled

✓ APIs enabled

✓ Runtime Service Account exists

✓ IAM configured

✓ GitHub OIDC configured

✓ Artifact Registry created

Infrastructure deployment is now complete.

Continue with:

Application Deployment Guide

# Enterprise Metadata Governance Platform

# Application Deployment Guide

Version 1.0

---

# Purpose

This document deploys the Enterprise Metadata Governance Platform application into an existing Google Cloud infrastructure.

This guide assumes the infrastructure described in **Infrastructure.md** has already been deployed successfully.

This document does **not** create Google Cloud infrastructure.

It deploys the application using GitHub Actions and Workload Identity Federation.

At the end of this guide the following components will exist.

- Cloud Run Service
- Cloud Run Revision
- Artifact Registry Image
- GitHub Actions Deployment Pipeline
- Health Endpoint
- Dashboard UI
- REST APIs

---

# Deployment Architecture

```
                  Developer

                      │

                      ▼

             GitHub Repository

                      │

                Git Push

                      │

                      ▼

             GitHub Actions

                      │

        Workload Identity Federation

                      │

                      ▼

              Cloud Build

                      │

                      ▼

           Artifact Registry Image

                      │

                      ▼

                Cloud Run

                      │

                      ▼

          Metadata Governance APIs
```

---

# Prerequisites

Before continuing verify the following.

| Component | Status |
|------------|--------|
| Infrastructure Deployment Completed | ✓ |
| Artifact Registry Exists | ✓ |
| Runtime Service Account Exists | ✓ |
| GitHub OIDC Configured | ✓ |
| GitHub Secrets Configured | ✓ |

---

# Step 1 - Clone the Repository

Clone the Metadata Governance Platform repository.

```bash
git clone https://github.com/<ORGANIZATION>/platform-metadata-governance.git
```

Navigate into the repository.

```bash
cd platform-metadata-governance
```

---

# Step 2 - Verify Repository Structure

Verify the repository contains the following folders.

```
.github/

cloudrun/

registry/

terraform/

validation/

docs/
```

The GitHub workflow should exist.

```
.github/workflows/

deploy.yml
```

If the workflow is missing the deployment cannot continue.

---

# Step 3 - Verify GitHub Secrets

Open

Repository

↓

Settings

↓

Secrets and Variables

↓

Actions

Verify the following secrets exist.

| Secret | Description |
|----------|-------------|
| WIF_PROVIDER | Workload Identity Provider Resource Name |
| WIF_SERVICE_ACCOUNT | Runtime Service Account |

Example

```
projects/123456789/locations/global/workloadIdentityPools/github/providers/github
```

```
metadata-governance@platform-metadata.iam.gserviceaccount.com
```

---

# Step 4 - Review GitHub Workflow

The deployment workflow should perform the following operations.

```
Checkout Repository

↓

Authenticate to Google Cloud

↓

Configure Docker Authentication

↓

Build Container

↓

Push Image

↓

Deploy Cloud Run

↓

Verify Deployment
```

No manual Docker build should occur.

No manual Cloud Run deployment should occur.

GitHub Actions is the only deployment mechanism.

---

# Step 5 - Deploy the Application

Commit the latest changes.

```bash
git add .
```

```bash
git commit -m "Deploy Metadata Governance Platform"
```

Push the changes.

```bash
git push origin main
```

---

# Step 6 - Monitor GitHub Actions

Open

```
GitHub

↓

Actions
```

Monitor the deployment.

Expected stages.

```
Checkout

↓

Authenticate

↓

Build

↓

Push Image

↓

Deploy Cloud Run

↓

Complete
```

If any stage fails stop and resolve the error before continuing.

---

# Step 7 - Verify Artifact Registry

Verify the image has been pushed.

```bash
gcloud artifacts docker images list \
$REGION-docker.pkg.dev/$PROJECT_ID/metadata-governance
```

Expected

```
latest

IMAGE DIGEST

CREATE TIME
```

---

# Step 8 - Verify Cloud Run

List services.

```bash
gcloud run services list \
--region=$REGION
```

Expected

```
metadata-governance

READY
```

Describe the service.

```bash
gcloud run services describe metadata-governance \
--region=$REGION
```

Verify.

- Ready
- URL assigned
- Revision deployed
- Runtime Service Account configured

---

# Step 9 - Retrieve the Cloud Run URL

Retrieve the URL.

```bash
gcloud run services describe metadata-governance \
--region=$REGION \
--format="value(status.url)"
```

Example

```
https://metadata-governance-xxxxxxxx.europe-west2.run.app
```

Store this URL.

It will be used throughout the remaining deployment.

---

# Step 10 - Health Check

Retrieve an Identity Token.

```bash
TOKEN=$(gcloud auth print-identity-token)
```

Call the Health endpoint.

```bash
curl \
-H "Authorization: Bearer $TOKEN" \
https://YOUR_CLOUD_RUN_URL/health
```

Expected Response

```json
{
    "status":"healthy"
}
```

---

# Step 11 - Verify Dashboard

Open

```
https://YOUR_CLOUD_RUN_URL/
```

The Metadata Governance Dashboard should load successfully.

Initially no reporting data will be displayed because the reporting platform has not yet been configured.

This is expected.

---

# Step 12 - Verify REST APIs

Dashboard API

```bash
curl \
-H "Authorization: Bearer $TOKEN" \
https://YOUR_CLOUD_RUN_URL/reports/dashboard
```

Expected

HTTP 200

Health API

```bash
curl \
-H "Authorization: Bearer $TOKEN" \
https://YOUR_CLOUD_RUN_URL/health
```

Expected

HTTP 200

Brownfield API

```bash
curl \
-H "Authorization: Bearer $TOKEN" \
https://YOUR_CLOUD_RUN_URL/brownfield
```

At this stage the request may fail because the reporting platform has not yet been configured.

This is expected.

---

# Step 13 - Verify Cloud Run Logs

Monitor the application logs.

```bash
gcloud beta run services logs tail metadata-governance \
--region=$REGION
```

Verify.

- Application Started
- Flask Started
- Dispatcher Loaded
- No Python Exceptions
- No Import Errors

---

# Troubleshooting

## GitHub Authentication Failed

Verify

- WIF_PROVIDER
- WIF_SERVICE_ACCOUNT

Verify the Workload Identity Provider.

---

## Artifact Registry Permission Denied

Verify

Artifact Registry IAM.

Verify the runtime service account has the required permissions.

---

## Cloud Run Deployment Failed

Verify.

- Container build completed.
- Image exists in Artifact Registry.
- Cloud Run API enabled.
- Runtime Service Account exists.

---

## Health Endpoint Returns 403

Cloud Run is configured to require authentication.

Always use an Identity Token.

Example.

```bash
TOKEN=$(gcloud auth print-identity-token)
```

---

## Health Endpoint Returns 500

Review Cloud Run logs.

```bash
gcloud beta run services logs tail metadata-governance \
--region=$REGION
```

Resolve all startup exceptions before continuing.

---

# Application Deployment Validation

Verify.

✓ GitHub Actions Completed

✓ Container Built

✓ Image Stored in Artifact Registry

✓ Cloud Run Ready

✓ Health Endpoint Responding

✓ Dashboard Accessible

✓ REST APIs Available

Application deployment is complete.

Continue with

Platform Configuration & Validation Guide


# Enterprise Metadata Governance Platform

# Platform Configuration & Validation Guide

Version 1.0

---

# Purpose

This guide configures the Metadata Governance Platform after the application has been successfully deployed.

At the end of this guide the platform will support:

- BigQuery Reporting
- Brownfield Governance
- Greenfield Governance
- Executive Dashboard
- Organization-level Reporting
- Project-level Reporting

---

# Deployment Order

The platform components must be configured in the following order.

```
Cloud Run

↓

BigQuery Dataset

↓

BigQuery Tables

↓

Governance Registry

↓

Pub/Sub

↓

Logging Sink

↓

Logging Publisher Permissions

↓

Eventarc

↓

Brownfield

↓

Greenfield

↓

Dashboard Validation
```

Do not change this order.

---

# Step 1 - Create BigQuery Dataset

The Metadata Governance Platform stores all reporting information in BigQuery.

Create the dataset.

```bash
bq mk \
--location=$REGION \
metadata_governance_dataset
```

Verify.

```bash
bq ls
```

Expected.

```
metadata_governance_dataset
```

---

# Step 2 - Create Bigquery Tables

The platform requires four reporting tables.

| Table | Purpose |
|---------|----------|
| resource_snapshot | Resource inventory |
| compliance_snapshot | Compliance results |
| remediation_plan | Planned remediation |
| remediation_execution | Execution history |


Copy-pasteable script to set up your BigQuery dataset in London (`europe-west2`) and create the four requested governance tables: `resource_snapshot`, `compliance_snapshot`, `remediation_plan`, and `remediation_execution`[cite: 3, 5, 6, 7].

The script is specifically designed to stream the schemas safely using standard input, preventing any unexpected script terminations when running under `set -e`.

---

## 1. The Script

Save the following code block to a file named `create-bq-tables.sh`.

```bash
#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -e

# =====================================================================
# CONFIGURATION
# =====================================================================
PROJECT_ID="platform-metadata"   # Your GCP Project ID
DATASET_ID="metadata_governance" # Your BigQuery Dataset ID
LOCATION="europe-west2"          # London region

echo "Using Project: ${PROJECT_ID}"
echo "Using Dataset: ${DATASET_ID}"
echo "Location:      ${LOCATION}"

# Create the dataset if it does not exist
echo "Ensuring BigQuery dataset '${DATASET_ID}' exists..."
bq show --project_id="${PROJECT_ID}" "${DATASET_ID}" > /dev/null 2>&1 || \
bq --project_id="${PROJECT_ID}" mk --dataset --location="${LOCATION}" "${DATASET_ID}"

# Helper function to read schema from stdin and create the clustered table
create_table() {
  local table_name=$1
  local clustering_fields=$2

  echo "Creating table: ${table_name} (Clustered by: ${clustering_fields})..."
  
  # Read schema from stdin and write to a temporary file
  cat > "/tmp/${table_name}_schema.json"
  
  # Create the table using the schema file and clustering configuration
  bq --project_id="${PROJECT_ID}" mk \
    --table \
    --clustering_fields="${clustering_fields}" \
    "${DATASET_ID}.${table_name}" \
    "/tmp/${table_name}_schema.json"

  # Clean up the temp file
  rm "/tmp/${table_name}_schema.json"
}

# =====================================================================
# TABLE 1: resource_snapshot
# =====================================================================
create_table "resource_snapshot" "project_id,asset_type,run_id" <<'EOF'
[
  {
    "name": "run_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "snapshot_time",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "project_id",
    "type": "STRING"
  },
  {
    "name": "asset_type",
    "type": "STRING"
  },
  {
    "name": "resource_name",
    "type": "STRING"
  },
  {
    "name": "location",
    "type": "STRING"
  },
  {
    "name": "labels",
    "type": "STRING"
  },
  {
    "name": "tags",
    "type": "STRING"
  }
]
EOF

# =====================================================================
# TABLE 2: compliance_snapshot
# =====================================================================
create_table "compliance_snapshot" "project_id,asset_type,run_id" <<'EOF'
[
  {
    "name": "run_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "evaluated_time",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "project_id",
    "type": "STRING"
  },
  {
    "name": "asset_type",
    "type": "STRING"
  },
  {
    "name": "resource_name",
    "type": "STRING"
  },
  {
    "name": "compliant",
    "type": "BOOL"
  },
  {
    "name": "missing_labels",
    "type": "STRING"
  },
  {
    "name": "incorrect_labels",
    "type": "STRING"
  }
]
EOF

# =====================================================================
# TABLE 3: remediation_plan
# =====================================================================
create_table "remediation_plan" "project_id,asset_type,run_id" <<'EOF'
[
  {
    "name": "run_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "project_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "asset_type",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "resource_name",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "missing_labels",
    "type": "JSON",
    "mode": "REQUIRED"
  },
  {
    "name": "planned_labels",
    "type": "JSON",
    "mode": "REQUIRED"
  },
  {
    "name": "planned_tags",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "status",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "created_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  }
]
EOF

# =====================================================================
# TABLE 4: remediation_execution
# =====================================================================
create_table "remediation_execution" "project_id,asset_type,run_id" <<'EOF'
[
  {
    "name": "execution_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "run_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "project_id",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "asset_type",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "resource_name",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "managed_labels",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "status",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "error_message",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "executed_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  },
  {
    "name": "execution_mode",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "service_name",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "method_name",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "duration_ms",
    "type": "INT64",
    "mode": "NULLABLE"
  }
]
EOF

# =====================================================================
# TABLE 5: label_ownership
# =====================================================================
create_table "label_ownership" "resource_name" <<'EOF'
[
  {
    "name": "resource_name",
    "type": "STRING",
    "mode": "REQUIRED"
  },
  {
    "name": "managed_labels",
    "type": "JSON",
    "mode": "NULLABLE"
  },
  {
    "name": "managed_tags",
    "type": "STRING",
    "mode": "NULLABLE"
  },
  {
    "name": "updated_at",
    "type": "TIMESTAMP",
    "mode": "REQUIRED"
  }
]
EOF

echo "All BigQuery tables created and clustered successfully in region ${LOCATION}!"


chmod +x create-bq-tables.sh

./create-bq-tables.sh

```Verify.

```bash
bq ls metadata_governance_dataset
```

Expected.

```
resource_snapshot

compliance_snapshot

remediation_plan

remediation_execution
```

---

# BigQuery Table Definitions

## resource_snapshot

| Column | Type |
|----------|------|
| run_id | STRING |
| snapshot_time | TIMESTAMP |
| project_id | STRING |
| asset_type | STRING |
| resource_name | STRING |
| location | STRING |
| labels | JSON |
| tags | JSON |

---

## compliance_snapshot

| Column | Type |
|----------|------|
| run_id | STRING |
| evaluated_time | TIMESTAMP |
| project_id | STRING |
| asset_type | STRING |
| resource_name | STRING |
| compliant | BOOLEAN |
| missing_labels | JSON |
| incorrect_labels | JSON |

---

## remediation_plan

| Column | Type |
|----------|------|
| remediation_id | STRING |
| run_id | STRING |
| project_id | STRING |
| asset_type | STRING |
| resource_name | STRING |
| status | STRING |
| planned_time | TIMESTAMP |

---

## remediation_execution

| Column | Type |
|----------|------|
| execution_id | STRING |
| run_id | STRING |
| project_id | STRING |
| asset_type | STRING |
| resource_name | STRING |
| status | STRING |
| executed_at | TIMESTAMP |
| error_message | STRING |

---

# Step 3 - Configure Governance Registry

The Governance Registry defines the expected metadata for each application.

Repository structure.

```
registry/

    payments.yaml

    platform.yaml

    analytics.yaml

    customer360.yaml
```

Each file represents one application.

Example.

```yaml
schemaVersion: v1

product: payments

team: cloud-platform

owner: john.doe

budgetOwner: finance

organization: example

department: engineering

costCenter: FIN001

bindings:

- cloud: gcp
  projectId: payments-prod
  region: europe-west2
  environment: prod
  businessCriticality: high
```

Validate.

```bash
python validation/validate_registry.py
```

Expected.

```
Validation Passed
```

---

# Step 4 - Create Pub/Sub

Create the event topic.

```bash
gcloud pubsub topics create metadata-governance-events
```

Create the subscription.

```bash
gcloud pubsub subscriptions create metadata-governance-sub \
--topic=metadata-governance-events
```

Verify.

```bash
gcloud pubsub topics list
```

```bash
gcloud pubsub subscriptions list
```

---

# Step 5 - Configure Logging Sink

Create the Logging Sink.

```bash
gcloud logging sinks create metadata-governance-sink \
pubsub.googleapis.com/projects/$PROJECT_ID/topics/metadata-governance-events \
--log-filter='logName:"cloudaudit.googleapis.com"'
```

Verify.

```bash
gcloud logging sinks list
```

---

# Step 6 - Grant Logging Publisher Permissions

Retrieve the writer identity.

```bash
gcloud logging sinks describe metadata-governance-sink
```

Grant Pub/Sub Publisher.

```bash
gcloud pubsub topics add-iam-policy-binding metadata-governance-events \
--member="serviceAccount:LOGGING_WRITER_IDENTITY" \
--role="roles/pubsub.publisher"
```

---

# Step 7 - Create Eventarc Trigger

Cloud Run must already exist before creating the trigger.

```bash
gcloud eventarc triggers create metadata-governance-trigger \
--location=$REGION \
--destination-run-service=metadata-governance \
--destination-run-region=$REGION \
--transport-topic=metadata-governance-events
```

Verify.

```bash
gcloud eventarc triggers list
```

Expected.

```
ACTIVE
```

---

# Step 8 - Execute First Brownfield Scan

Retrieve an Identity Token.

```bash
TOKEN=$(gcloud auth print-identity-token)
```

Execute Brownfield.

```bash
curl \
-H "Authorization: Bearer $TOKEN" \
"https://YOUR_CLOUD_RUN_URL/brownfield?project=$PROJECT_ID"
```

Expected.

- Resources discovered
- Compliance evaluated
- Remediation plan generated
- Reporting tables populated

---

# Step 9 - Verify BigQuery Reporting

Verify inventory.

```sql
SELECT COUNT(*) FROM metadata_governance_dataset.resource_snapshot;
```

Verify compliance.

```sql
SELECT COUNT(*) FROM metadata_governance_dataset.compliance_snapshot;
```

Verify remediation plan.

```sql
SELECT COUNT(*) FROM metadata_governance_dataset.remediation_plan;
```

Verify execution history.

```sql
SELECT COUNT(*) FROM metadata_governance_dataset.remediation_execution;
```

Each table should contain records.

---

# Step 10 - Validate Greenfield Governance

Create a supported resource.

Example.

```bash
gcloud compute instances create governance-test-vm \
--project=$PROJECT_ID \
--zone=europe-west2-a \
--machine-type=e2-micro \
--image-family=debian-12 \
--image-project=debian-cloud
```

Monitor Cloud Run logs.

```bash
gcloud beta run services logs tail metadata-governance \
--region=$REGION
```

Expected processing flow.

```
Audit Event Received

↓

Classification Completed

↓

Registry Match

↓

Compliance Evaluated

↓

Remediation Executed

↓

Reporting Updated
```

---

# Step 11 - Validate Dashboard

Open.

```
https://YOUR_CLOUD_RUN_URL
```

Verify.

## Executive Summary

- Total Resources
- Supported Resources
- Compliance Percentage
- Projects

## Brownfield

- Planned
- Completed
- Remaining
- Failed
- Success Rate

## Greenfield

- Events
- Remediated
- Failed
- Average Processing Time

## Projects

- Organization View
- Project Filter

## Resource Types

- Compliance
- Progress Bars

## Recent Runs

- Latest Brownfield Executions

## Top Non-Compliant Resources

- Missing Labels
- Incorrect Labels

---

# Platform Validation Checklist

| Validation | Status |
|------------|--------|
| BigQuery Dataset Created | ☐ |
| Reporting Tables Created | ☐ |
| Registry Validated | ☐ |
| Pub/Sub Created | ☐ |
| Logging Sink Created | ☐ |
| Logging Publisher Granted | ☐ |
| Eventarc Trigger Active | ☐ |
| Brownfield Successful | ☐ |
| Greenfield Successful | ☐ |
| Dashboard Operational | ☐ |

---

# Deployment Complete

The Enterprise Metadata Governance Platform is now fully operational.

The platform continuously:

- Discovers Google Cloud resources.
- Evaluates metadata compliance.
- Automatically remediates supported resources.
- Processes newly created resources in real time.
- Stores governance history in BigQuery.
- Provides executive dashboards for organization and project governance.
