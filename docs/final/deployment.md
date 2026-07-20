Here is the complete, finalized **Enterprise Deployment Guide**.

This document serves as your single source of truth. It incorporates every fix, permission, and architectural decision we made to support a secure, multi-environment (Dev & Prod) deployment using GitHub Actions and Workload Identity Federation.

You can save this directly to your repository as `docs/DEPLOYMENT_GUIDE.md` or `README.md`.

---

# 🚀 Enterprise Metadata Governance - Multi-Environment Deployment Guide

This guide details the end-to-end setup for the real-time (Greenfield) and batch (Brownfield) GCP Metadata Governance Engine across two isolated environments:

1. **Development (`platform-metadata-dev`)**: Triggered automatically on merges to the `main` branch. Scoped to a sandbox/dev folder.
2. **Production (`platform-metadata`)**: Triggered securely via GitHub Releases. Scoped to the entire GCP Organization.

---

## 📋 Phase 1: Environment Preparation (Run Locally)

You must run the infrastructure bootstrap **twice**—once for the Dev project, and once for the Prod project.

Open your local terminal (or GCP Cloud Shell) and set up your variables.

### 1.1 Define Variables

Set these variables. When setting up Dev, use the `dev` project ID. When setting up Prod, use the `prod` project ID.

```bash
# CHANGE THIS TO "platform-metadata" WHEN SETTING UP PROD
export PROJECT_ID="platform-metadata-dev" 

export REGION="europe-west2"
export GITHUB_REPO="rovalinks/platform-metadata" # Your exact, case-sensitive GitHub Repo
export SA_NAME="metadata-governance"
export SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
export WIF_POOL="github-pool"
export WIF_PROVIDER="github-provider"

gcloud config set project $PROJECT_ID

```

### 1.2 Enable Required APIs

```bash
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    eventarc.googleapis.com \
    pubsub.googleapis.com \
    cloudtasks.googleapis.com \
    cloudasset.googleapis.com \
    bigquery.googleapis.com \
    artifactregistry.googleapis.com

```

### 1.3 Provision Core Infrastructure (The "Furniture")

```bash
# 1. BigQuery Dataset
bq mk --location=$REGION -d ${PROJECT_ID}:metadata_governance_dataset

# 2. Cloud Storage Registry (Where your YAMLs go)
gcloud storage buckets create gs://${PROJECT_ID}-registry --location=$REGION

# 3. Cloud Tasks Queue (Rate Limited)
gcloud tasks queues create metadata-remediation --location=$REGION
gcloud tasks queues update metadata-remediation --location=$REGION --max-dispatches-per-second=5 --max-concurrent-dispatches=10

# 4. Pub/Sub Topic for Greenfield
gcloud pubsub topics create metadata-governance-events

# 5. Artifact Registry for Docker Images
gcloud artifacts repositories create metadata-governance \
  --repository-format=docker \
  --location=$REGION \
  --description="Docker repository for Metadata Governance Engine" \
  --project=$PROJECT_ID

```

---

## 🔐 Phase 2: IAM & Security (The "Keys")

We will create a single Service Account that acts as both the deployment identity (for GitHub) and the runtime identity (for Cloud Run).

### 2.1 Create the Service Account

```bash
gcloud iam service-accounts create $SA_NAME \
  --display-name="Metadata Governance Runtime & Deployer"

```

### 2.2 Grant Operational Permissions

```bash
# BigQuery, Cloud Tasks, Storage
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/bigquery.dataEditor"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/cloudtasks.enqueuer"
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/storage.objectViewer"

# Artifact Registry (To push Docker images)
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/artifactregistry.writer"

# Cloud Run Deployment & Execution (actAs)
gcloud projects add-iam-policy-binding $PROJECT_ID --member="serviceAccount:$SA_EMAIL" --role="roles/run.admin"
gcloud iam service-accounts add-iam-policy-binding $SA_EMAIL --member="serviceAccount:$SA_EMAIL" --role="roles/iam.serviceAccountUser"

```

*⚠️ **Important Governance Scoping:** You must also grant this Service Account `roles/cloudasset.viewer` and your custom label-editing role. For Dev, attach this to a Sandbox Folder/Project. For Prod, attach this at the Organization level.*

### 2.3 Setup Workload Identity Federation (GitHub Bridge)

```bash
# 1. Create Pool & Provider
gcloud iam workload-identity-pools create $WIF_POOL --location="global" --display-name="GitHub Actions Pool"
gcloud iam workload-identity-pools providers create-oidc $WIF_PROVIDER \
  --location="global" \
  --workload-identity-pool=$WIF_POOL \
  --display-name="GitHub Repo Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# 2. Extract Pool ID
export POOL_ID=$(gcloud iam workload-identity-pools describe $WIF_POOL --location="global" --format="value(name)")

# 3. Bind the exact GitHub Repository to the Service Account
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${GITHUB_REPO}"

```

### 2.4 Extract Secrets for GitHub

Run these commands and save the output. You will paste these into GitHub.

```bash
# 1. The WIF_PROVIDER string
gcloud iam workload-identity-pools providers describe $WIF_PROVIDER --location="global" --workload-identity-pool=$WIF_POOL --format="value(name)"

# 2. The SERVICE_ACCOUNT string
echo $SA_EMAIL

```

*(🛑 **STOP**: Once finished with Dev, scroll back up to Step 1.1, change the `PROJECT_ID` to `platform-metadata`, and repeat the process to build Prod).*

---

## 🐙 Phase 3: GitHub Repository Configuration

### 3.1 Setup GitHub Environments

1. Go to your GitHub Repository **Settings > Environments**.
2. Create an environment named `dev`.
3. Create an environment named `prod`. (Check "Required reviewers" and add yourself so prod requires manual approval).

### 3.2 Add Secrets and Variables to Environments

Inside **each** environment (`dev` and `prod`), configure the following:

**Environment Secrets:**

* `WIF_PROVIDER`: Paste the long string from Step 2.4 (ensure you use the Dev one for Dev, and Prod for Prod).
* `WIF_SERVICE_ACCOUNT`: Paste the Service Account Email.
* `SERVICE_ACCOUNT_EMAIL`: Paste the Service Account Email again.

**Environment Variables:**

* `PROJECT_ID`: `platform-metadata-dev` (for dev) or `platform-metadata` (for prod)
* `REGION`: `europe-west2`
* `CLOUD_RUN_SERVICE`: `metadata-governance`
* `IMAGE_NAME`: `governance-engine`
* `ARTIFACT_REPOSITORY`: `metadata-governance`
* `TAG_PARENT`: `organizations/YOUR_ORG_ID`
* `REGISTRY_BUCKET`: `platform-metadata-dev-registry` (adjust for prod)
* `BIGQUERY_DATASET`: `metadata_governance_dataset`
* `TASK_QUEUE`: `metadata-remediation`
* `DRY_RUN`: `"true"` (Keep true until you are ready to actually mutate resources)

---

## 🔄 Phase 4: CI/CD Pipeline

Save this file as `.github/workflows/deploy.yml`.

* Commits to `main` -> Triggers Security Scans -> Deploys to `dev`.
* GitHub Releases -> Triggers Security Scans -> Deploys to `prod`.

```yaml
name: Deploy Metadata Governance

on:
  push:
    branches:
      - main
    paths:
      - "cloudrun/**"
      - "Dockerfile"
      - ".github/workflows/deploy.yml"
  release:
    types: [published]

permissions:
  contents: read
  id-token: write
  security-events: write

jobs:
  security-checks:
    name: Security Scans
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4.2.0
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - name: Install & Run Bandit
        run: |
          pip install bandit
          bandit -r cloudrun/ -ll -ii
      - name: Run Trivy Vulnerability Scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'table'
          exit-code: '1'
          ignore-unfixed: true
          severity: 'CRITICAL,HIGH'

  deploy-dev:
    name: Deploy to Dev
    needs: security-checks
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: dev 
    steps:
      - uses: actions/checkout@v4.2.0
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker ${{ vars.REGION }}-docker.pkg.dev --quiet
      - name: Build & Push Image
        run: |
          IMAGE_PATH="${{ vars.REGION }}-docker.pkg.dev/${{ vars.PROJECT_ID }}/${{ vars.ARTIFACT_REPOSITORY }}/${{ vars.IMAGE_NAME }}"
          docker build -f Dockerfile -t "$IMAGE_PATH:${{ github.sha }}" -t "$IMAGE_PATH:latest" .
          docker push "$IMAGE_PATH:${{ github.sha }}"
          docker push "$IMAGE_PATH:latest"
      - name: Get Cloud Run URL
        id: service_url
        run: |
          URL=$(gcloud run services describe ${{ vars.CLOUD_RUN_SERVICE }} \
            --project=${{ vars.PROJECT_ID }} --region=${{ vars.REGION }} \
            --format="value(status.url)" 2>/dev/null || echo "PENDING_FIRST_DEPLOY")
          echo "SERVICE_URL=$URL" >> $GITHUB_ENV
      - name: Prepare env.yaml
        env:
          PROJECT_ID: ${{ vars.PROJECT_ID }}
          REGION: ${{ vars.REGION }}
          TAG_PARENT: ${{ vars.TAG_PARENT }}
          REGISTRY_BUCKET: ${{ vars.REGISTRY_BUCKET }}
          BIGQUERY_DATASET: ${{ vars.BIGQUERY_DATASET }}
          TASK_QUEUE: ${{ vars.TASK_QUEUE }}
          SERVICE_ACCOUNT_EMAIL: ${{ secrets.SERVICE_ACCOUNT_EMAIL }}
          CLOUD_RUN_URL: ${{ env.SERVICE_URL }}
          DRY_RUN: ${{ vars.DRY_RUN }} 
        run: |
          python3 -c '
          import os
          content = ""
          if os.path.exists("cloudrun/env.yaml"):
              with open("cloudrun/env.yaml", "r") as f: content = f.read().rstrip() + "\n"
          for key in ["PROJECT_ID", "REGION", "TAG_PARENT", "REGISTRY_BUCKET", "BIGQUERY_DATASET", "TASK_QUEUE", "SERVICE_ACCOUNT_EMAIL", "CLOUD_RUN_URL", "DRY_RUN"]:
              if os.environ.get(key): content += f"{key}: \"{os.environ.get(key)}\"\n"
          os.makedirs("cloudrun", exist_ok=True)
          with open("cloudrun/env.yaml", "w") as f: f.write(content)
          '
      - name: Deploy Cloud Run
        run: |
          gcloud run deploy ${{ vars.CLOUD_RUN_SERVICE }} \
            --project=${{ vars.PROJECT_ID }} \
            --region=${{ vars.REGION }} \
            --image="${{ vars.REGION }}-docker.pkg.dev/${{ vars.PROJECT_ID }}/${{ vars.ARTIFACT_REPOSITORY }}/${{ vars.IMAGE_NAME }}:latest" \
            --service-account=${{ secrets.SERVICE_ACCOUNT_EMAIL }} \
            --env-vars-file=cloudrun/env.yaml \
            --memory=1Gi --cpu=2 --timeout=900 --concurrency=80 --allow-unauthenticated

  deploy-prod:
    name: Deploy to Prod
    needs: security-checks
    if: github.event_name == 'release' && github.event.action == 'published'
    runs-on: ubuntu-latest
    environment: prod 
    steps:
      # [IDENTICAL STEPS TO DEV - Replace environment: prod and run the same checkout, auth, build, and deploy steps]
      - uses: actions/checkout@v4.2.0
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      - uses: google-github-actions/setup-gcloud@v2
      - run: gcloud auth configure-docker ${{ vars.REGION }}-docker.pkg.dev --quiet
      - name: Build & Push Image
        run: |
          IMAGE_PATH="${{ vars.REGION }}-docker.pkg.dev/${{ vars.PROJECT_ID }}/${{ vars.ARTIFACT_REPOSITORY }}/${{ vars.IMAGE_NAME }}"
          docker build -f Dockerfile -t "$IMAGE_PATH:${{ github.ref_name }}" -t "$IMAGE_PATH:latest" .
          docker push "$IMAGE_PATH:${{ github.ref_name }}"
          docker push "$IMAGE_PATH:latest"
      - name: Get Cloud Run URL
        id: service_url
        run: |
          URL=$(gcloud run services describe ${{ vars.CLOUD_RUN_SERVICE }} --project=${{ vars.PROJECT_ID }} --region=${{ vars.REGION }} --format="value(status.url)" 2>/dev/null || echo "PENDING_FIRST_DEPLOY")
          echo "SERVICE_URL=$URL" >> $GITHUB_ENV
      - name: Prepare env.yaml
        env:
          PROJECT_ID: ${{ vars.PROJECT_ID }}
          REGION: ${{ vars.REGION }}
          TAG_PARENT: ${{ vars.TAG_PARENT }}
          REGISTRY_BUCKET: ${{ vars.REGISTRY_BUCKET }}
          BIGQUERY_DATASET: ${{ vars.BIGQUERY_DATASET }}
          TASK_QUEUE: ${{ vars.TASK_QUEUE }}
          SERVICE_ACCOUNT_EMAIL: ${{ secrets.SERVICE_ACCOUNT_EMAIL }}
          CLOUD_RUN_URL: ${{ env.SERVICE_URL }}
          DRY_RUN: ${{ vars.DRY_RUN }} 
        run: |
          python3 -c '
          import os
          content = ""
          if os.path.exists("cloudrun/env.yaml"):
              with open("cloudrun/env.yaml", "r") as f: content = f.read().rstrip() + "\n"
          for key in ["PROJECT_ID", "REGION", "TAG_PARENT", "REGISTRY_BUCKET", "BIGQUERY_DATASET", "TASK_QUEUE", "SERVICE_ACCOUNT_EMAIL", "CLOUD_RUN_URL", "DRY_RUN"]:
              if os.environ.get(key): content += f"{key}: \"{os.environ.get(key)}\"\n"
          os.makedirs("cloudrun", exist_ok=True)
          with open("cloudrun/env.yaml", "w") as f: f.write(content)
          '
      - name: Deploy Cloud Run
        run: |
          gcloud run deploy ${{ vars.CLOUD_RUN_SERVICE }} \
            --project=${{ vars.PROJECT_ID }} \
            --region=${{ vars.REGION }} \
            --image="${{ vars.REGION }}-docker.pkg.dev/${{ vars.PROJECT_ID }}/${{ vars.ARTIFACT_REPOSITORY }}/${{ vars.IMAGE_NAME }}:latest" \
            --service-account=${{ secrets.SERVICE_ACCOUNT_EMAIL }} \
            --env-vars-file=cloudrun/env.yaml \
            --memory=1Gi --cpu=2 --timeout=900 --concurrency=80 --allow-unauthenticated

```

*(Remember to add `# nosec B104` to `host="0.0.0.0"` in your `app.py` to pass the Bandit scan!)*

---

## 📡 Phase 5: Post-Deployment Wiring (Eventarc & Sinks)

Once GitHub Actions successfully deploys Cloud Run, you must connect the Pub/Sub plumbing. Run this for both Dev and Prod (substituting the `$PROJECT_ID`).

### 5.1 Connect Eventarc to Cloud Run

```bash
gcloud eventarc triggers create metadata-governance-trigger \
  --project=$PROJECT_ID \
  --location=$REGION \
  --destination-run-service=metadata-governance \
  --destination-run-region=$REGION \
  --event-filters="type=google.cloud.pubsub.topic.v1.messagePublished" \
  --transport-topic=projects/$PROJECT_ID/topics/metadata-governance-events \
  --service-account=$SA_EMAIL

# Allow Eventarc to invoke Cloud Run
gcloud run services add-iam-policy-binding metadata-governance \
  --project=$PROJECT_ID \
  --region=$REGION \
  --member="serviceAccount:eventarc-trigger@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

```

### 5.2 Create the Greenfield Log Sink

**For Dev:** Scope this to a specific sandbox folder or project to test safely.

```bash
gcloud logging sinks create metadata-governance-sink \
  pubsub.googleapis.com/projects/platform-metadata-dev/topics/metadata-governance-events \
  --folder=YOUR_SANDBOX_FOLDER_ID \
  --include-children \
  --log-filter='log_id("cloudaudit.googleapis.com/activity") AND protoPayload.serviceName=~"^(compute|bigquery|storage|secretmanager|sqladmin|pubsub|cloudfunctions|artifactregistry|aiplatform|redis|alloydb|cloudkms|container)\.googleapis\.com$" AND protoPayload.methodName=~"(?i)(create|insert)" AND NOT logName:"projects/platform-metadata-dev"'

```

**For Prod:** Scope to the entire Organization.

```bash
gcloud logging sinks create metadata-governance-sink \
  pubsub.googleapis.com/projects/platform-metadata/topics/metadata-governance-events \
  --organization=YOUR_ORG_ID \
  --include-children \
  --log-filter='log_id("cloudaudit.googleapis.com/activity") AND protoPayload.serviceName=~"^(compute|bigquery|storage|secretmanager|sqladmin|pubsub|cloudfunctions|artifactregistry|aiplatform|redis|alloydb|cloudkms|container)\.googleapis\.com$" AND protoPayload.methodName=~"(?i)(create|insert)" AND NOT logName:"projects/platform-metadata"'

```

### 5.3 Grant Sink Write Access

```bash
SINK_SA=$(gcloud logging sinks describe metadata-governance-sink --organization=YOUR_ORG_ID --format='value(writerIdentity)')

gcloud pubsub topics add-iam-policy-binding metadata-governance-events \
  --project=$PROJECT_ID \
  --member="$SINK_SA" \
  --role="roles/pubsub.publisher"

```

**You are now fully deployed in both environments.** 🚀