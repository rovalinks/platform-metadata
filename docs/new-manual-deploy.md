Here is the complete, single-file documentation for setting up and deploying the Enterprise Metadata Governance engine. It covers the manual infrastructure bootstrapping required before handing over the continuous deployment to GitHub Actions.

You can save this as `docs/deployment-guide.md` or `README.md` in your repository.

---

# 🚀 Enterprise Metadata Governance - Deployment Guide

This guide details the end-to-end process for deploying the real-time (Greenfield) and batch (Brownfield) GCP Metadata Governance Engine.

The infrastructure routing (Pub/Sub, BigQuery, Log Sinks) requires a one-time manual bootstrap by a GCP Administrator. Once the environment is bootstrapped, the application lifecycle is fully managed via **GitHub Actions**.

---

## 📋 Prerequisites

1. **GCP Project**: A dedicated host project (e.g., `platform-metadata`).
2. **Permissions**: You must have `Owner` or `Editor + IAM Admin` rights on the host project, and `Organization Policy Admin` or `Logging Admin` at the Organization level for the Log Sink.
3. **Tools Required**: `gcloud` CLI authenticated to your GCP account.

Set your environment variables in your terminal before starting:

```bash
export PROJECT_ID="platform-metadata"
export REGION="europe-west2"
export ORG_ID="YOUR_ORGANIZATION_ID"
export SA_NAME="metadata-governance"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project $PROJECT_ID

```

---

## 🛠 Phase 1: Infrastructure Bootstrap (Manual)

Run these commands to provision the required stateful components.

### 1.1 Enable APIs

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    eventarc.googleapis.com \
    pubsub.googleapis.com \
    cloudtasks.googleapis.com \
    cloudasset.googleapis.com \
    bigquery.googleapis.com \
    iamcredentials.googleapis.com

```

### 1.2 Create BigQuery Dataset & Tables

```bash
bq mk --location=$REGION -d $PROJECT_ID:metadata_governance_dataset

```

*(Note: The application will automatically create the tables (e.g., `remediation_plan`, `compliance_snapshot`) on its first run if they do not exist).*

### 1.3 Create Cloud Storage Registry

```bash
gcloud storage buckets create gs://${PROJECT_ID}-registry --location=$REGION

```

### 1.4 Create Rate-Limited Cloud Tasks Queue

```bash
gcloud tasks queues create metadata-remediation --location=$REGION

# Apply strict rate limits to prevent API Quota exhaustion during Brownfield scans
gcloud tasks queues update metadata-remediation \
  --location=$REGION \
  --max-dispatches-per-second=5 \
  --max-concurrent-dispatches=10

```

### 1.5 Create Real-Time Pub/Sub Topic

```bash
gcloud pubsub topics create metadata-governance-events

```

---

## 🔐 Phase 2: Service Account & IAM Setup

The Cloud Run service needs a dedicated identity with the principle of least privilege.

### 2.1 Create the Service Account

```bash
gcloud iam service-accounts create $SA_NAME \
    --display-name="Metadata Governance Engine Runtime"

```

### 2.2 Grant Standard Operational Roles

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/bigquery.dataEditor"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudtasks.enqueuer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/storage.objectViewer"

```

### 2.3 Grant Organization-Level Read/Write Roles

To allow the engine to read Cloud Asset Inventory and write labels across the organization:

```bash
# Allow discovery
gcloud organizations add-iam-policy-binding $ORG_ID \
    --member="serviceAccount:$SA_EMAIL" \
    --role="roles/cloudasset.viewer"

# Note: You must also create a Custom Role containing permissions like 
# `compute.instances.setLabels`, `bigquery.datasets.update`, etc., 
# and bind it to this Service Account at the Org level.

```

---

## 🐙 Phase 3: GitHub Actions Setup (CI/CD)

The application code is deployed automatically via GitHub Actions. We use Workload Identity Federation (WIF) to securely authenticate GitHub to GCP without long-lived JSON keys.

### 3.1 Create Workload Identity Pool

```bash
gcloud iam workload-identity-pools create "github-actions-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool"

```

### 3.2 Create OIDC Provider

```bash
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-actions-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

```

### 3.3 Allow GitHub to impersonate the Service Account

```bash
export REPO="rovalinks/platform-metadata" # Update to your exact repo name
export POOL_ID=$(gcloud iam workload-identity-pools describe "github-actions-pool" --location="global" --format="value(name)")

gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${REPO}"

```

### 3.4 GitHub Repository Secrets

Go to your GitHub Repository -> Settings -> Secrets and Variables -> Actions. Add the following:

* `WIF_PROVIDER`: The full path to the provider created in 3.2 (e.g., `projects/123456789/locations/global/workloadIdentityPools/github-actions-pool/providers/github-provider`)
* `SA_EMAIL`: Your service account email.
* `GCP_PROJECT`: `platform-metadata`
* `GCP_REGION`: `europe-west2`

*(Pushing to the `main` branch will now automatically build the Docker container and deploy it to Cloud Run).*

---

## 📡 Phase 4: Event Routing (Greenfield)

Once GitHub Actions has deployed the Cloud Run service, you must configure GCP to route real-time audit logs to it.

### 4.1 Create the Eventarc Trigger

```bash
gcloud eventarc triggers create metadata-governance-trigger \
  --location=$REGION \
  --destination-run-service=metadata-governance \
  --destination-run-region=$REGION \
  --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" \
  --transport-topic=projects/$PROJECT_ID/topics/metadata-governance-events \
  --service-account=$SA_EMAIL

# Grant Eventarc permission to invoke Cloud Run
gcloud run services add-iam-policy-binding metadata-governance \
  --region=$REGION \
  --member="serviceAccount:eventarc-trigger@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

```

### 4.2 Create the Organization Log Sink

Capture all resource creation events at the Org level and route them to Pub/Sub. **Crucial:** We exclude the host project to prevent an infinite feedback loop.

```bash
gcloud logging sinks create metadata-governance-sink \
  pubsub.googleapis.com/projects/$PROJECT_ID/topics/metadata-governance-events \
  --organization=$ORG_ID \
  --include-children \
  --log-filter='log_id("cloudaudit.googleapis.com/activity") AND protoPayload.serviceName=~"^(compute|bigquery|storage|secretmanager|sqladmin|pubsub|cloudfunctions|artifactregistry|aiplatform|redis|alloydb|cloudkms|container)\.googleapis\.com$" AND protoPayload.methodName=~"(?i)(create|insert)" AND NOT logName:"projects/platform-metadata"'

```

### 4.3 Grant Sink Permissions

GCP creates a unique writer identity for Org sinks. Find it and grant it Pub/Sub Publisher rights:

```bash
# Get the Writer Identity
SINK_SA=$(gcloud logging sinks describe metadata-governance-sink --organization=$ORG_ID --format='value(writerIdentity)')

# Grant access
gcloud pubsub topics add-iam-policy-binding metadata-governance-events \
  --member="$SINK_SA" \
  --role="roles/pubsub.publisher"

```

---

## ✅ Phase 5: Verification

### 5.1 Test Greenfield (Real-time)

1. Open Cloud Shell and tail the engine logs:
`gcloud beta run services logs tail metadata-governance --region=europe-west2`
2. Create a test Compute Engine VM in any project *except* `platform-metadata`.
3. Verify the logs show the event being intercepted, the Extractor parsing the implicit disks, and the labels being successfully patched.

### 5.2 Test Brownfield (Batch)

Trigger a full estate scan to update your dashboard compliance.

```bash
export TOKEN=$(gcloud auth print-identity-token)
export CLOUD_RUN_URL=$(gcloud run services describe metadata-governance --region=$REGION --format='value(status.url)')

curl -H "Authorization: Bearer $TOKEN" -X POST "${CLOUD_RUN_URL}/brownfield?scope=organization"

```

Monitor the Cloud Tasks queue to watch the remediation batches safely execute within your API limits.