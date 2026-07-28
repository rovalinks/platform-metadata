# Enterprise Metadata Governance Platform

# Manual Deployment Guide

**Version:** 1.0

**Audience**

- Cloud Platform Engineers
- Platform Administrators
- DevOps Engineers
- Google Cloud Administrators
- Operations Teams

---

# Purpose

This guide describes how to deploy the Enterprise Metadata Governance Platform manually into Google Cloud without using Terraform.

The document is intended for organizations that want to understand the platform deployment process or perform a manual installation for demonstration, testing, or production environments.

Unlike the Terraform deployment, this guide walks through every Google Cloud component that must be created and configured.

The deployment is fully parameterized and can be used in any Google Cloud organization, project, or supported region.

---

# Platform Overview

The Enterprise Metadata Governance Platform provides continuous metadata governance across Google Cloud.

It consists of four major capabilities.

- Brownfield Governance
- Greenfield Governance
- Metadata Registry
- Executive Reporting

Brownfield discovers existing resources and evaluates compliance.

Greenfield automatically evaluates newly created resources using Google Cloud Audit Logs.

The Governance Registry defines the expected metadata for every application.

BigQuery stores governance information for reporting and executive dashboards.

---

# High-Level Architecture

```
                           +--------------------------------+
                           | Governance Registry            |
                           | Application Metadata           |
                           +---------------+----------------+
                                           |
                                           |
                                           v
                          +-------------------------------+
                          | Cloud Run                     |
                          | Metadata Governance Platform  |
                          +---------------+---------------+
                                          |
          +-------------------------------+-------------------------------+
          |                               |                               |
          v                               v                               v

 Brownfield Discovery             Greenfield Events               Reporting Engine

          |                               |                               |
          +---------------+---------------+-------------------------------+
                          |
                          v

                    BigQuery Dataset

                          |

                          v

                 Executive Dashboard
```

---

# Supported Deployment Regions

The platform is region independent.

Any Google Cloud region supporting Cloud Run, Eventarc and BigQuery may be used.

Examples include:

| Region | Location |
|---------|----------|
| us-central1 | Iowa |
| us-east1 | South Carolina |
| us-east4 | Northern Virginia |
| europe-west1 | Belgium |
| europe-west2 | London |
| europe-west4 | Netherlands |
| australia-southeast1 | Sydney |
| asia-southeast1 | Singapore |

Choose the region closest to the workloads being governed.

---

# Deployment Variables

Before beginning deployment define the following variables.

| Variable | Description | Example |
|-----------|-------------|---------|
| PROJECT_ID | Google Cloud project hosting the platform | metadata-governance-prod |
| ORGANIZATION_ID | Google Cloud Organization ID | 123456789012 |
| REGION | Deployment region | europe-west2 |
| DATASET_NAME | BigQuery reporting dataset | metadata_governance_dataset |
| SERVICE_NAME | Cloud Run service | metadata-governance |
| REPOSITORY_NAME | Artifact Registry repository | metadata-governance |
| IMAGE_NAME | Cloud Run container image | metadata-governance |
| SERVICE_ACCOUNT_NAME | Runtime service account | metadata-governance |
| REGISTRY_PATH | Governance registry location | registry/ |

Example shell variables.

```bash
export PROJECT_ID=my-governance-project
export ORGANIZATION_ID=123456789012
export REGION=europe-west2
export DATASET_NAME=metadata_governance_dataset
export SERVICE_NAME=metadata-governance
export REPOSITORY_NAME=metadata-governance
export IMAGE_NAME=metadata-governance
export SERVICE_ACCOUNT_NAME=metadata-governance
```

---

# Prerequisites

Install the latest versions of the following tools.

| Software | Required |
|-----------|----------|
| Google Cloud SDK | Yes |
| Git | Yes |
| Docker | Yes |
| Python 3.12+ | Yes |

Verify installation.

```bash
gcloud version
```

```bash
git --version
```

```bash
docker --version
```

```bash
python --version
```

---

# Google Cloud Authentication

Authenticate with Google Cloud.

```bash
gcloud auth login
```

Configure Application Default Credentials.

```bash
gcloud auth application-default login
```

Verify authentication.

```bash
gcloud auth list
```

The active account should have sufficient permissions to deploy Google Cloud resources.

---

# Required IAM Permissions

The deploying identity requires permissions to create and configure Google Cloud services.

Typical deployment roles include:

| IAM Role | Purpose |
|-----------|---------|
| Project Owner | Create project resources |
| IAM Admin | Configure IAM |
| Service Usage Admin | Enable APIs |
| Cloud Run Admin | Deploy Cloud Run |
| Artifact Registry Admin | Create repositories |
| BigQuery Admin | Create datasets and tables |
| Eventarc Admin | Create Eventarc triggers |
| Pub/Sub Admin | Create topics and subscriptions |
| Logging Admin | Configure logging sinks |
| Service Account Admin | Create service accounts |

Runtime permissions are documented separately in:

```
docs/iam-permissions.md
```

---

# Enable Required Google Cloud APIs

Enable all required APIs.

```bash
gcloud services enable \
artifactregistry.googleapis.com \
bigquery.googleapis.com \
cloudasset.googleapis.com \
cloudbuild.googleapis.com \
cloudresourcemanager.googleapis.com \
eventarc.googleapis.com \
iam.googleapis.com \
logging.googleapis.com \
pubsub.googleapis.com \
run.googleapis.com \
secretmanager.googleapis.com \
serviceusage.googleapis.com \
sqladmin.googleapis.com \
storage.googleapis.com
```

Verify.

```bash
gcloud services list --enabled
```

Confirm all required services are enabled before continuing.

---

# Clone the Repository

Clone the platform repository.

```bash
git clone https://github.com/<organization>/platform-metadata-governance.git
```

Navigate into the project.

```bash
cd platform-metadata-governance
```

Expected repository structure.

```
cloudrun/
terraform/
registry/
docs/
validation/
```

---

# Create the Cloud Run Service Account

Create the runtime service account.

```bash
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
    --display-name="Metadata Governance Platform"
```

Verify.

```bash
gcloud iam service-accounts list
```

Expected output should include:

```
metadata-governance@PROJECT_ID.iam.gserviceaccount.com
```

---

# Configure Runtime IAM

Grant the required runtime permissions to the Cloud Run service account.

The recommended permissions are documented in:

```
docs/iam-permissions.md
```

Apply each required role using:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
--member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
--role="ROLE_NAME"
```

Repeat for every required runtime role.

---

# Create Artifact Registry

Create the Docker repository.

```bash
gcloud artifacts repositories create $REPOSITORY_NAME \
--repository-format=docker \
--location=$REGION \
--description="Enterprise Metadata Governance Platform Images"
```

Verify.

```bash
gcloud artifacts repositories list
```

Expected output.

```
metadata-governance
```

---

# Configure Docker Authentication

Configure Docker authentication.

```bash
gcloud auth configure-docker $REGION-docker.pkg.dev
```

Expected output.

```
Docker configuration updated.
```

---

# Build the Cloud Run Container

Submit the build.

```bash
gcloud builds submit \
--tag $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE_NAME:latest
```

Monitor the build.

```bash
gcloud builds list
```

If the build fails.

Retrieve logs.

```bash
gcloud builds log BUILD_ID
```

Correct any reported issues before continuing.

---

# Validate the Container Image

Verify the image exists.

```bash
gcloud artifacts docker images list \
$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME
```

Expected output.

```
IMAGE_NAME

latest
```


# Step 13 - Deploy Cloud Run

## Purpose

Cloud Run hosts the Metadata Governance Platform.

The service provides:

- Brownfield APIs
- Greenfield Event Processing
- Dashboard APIs
- Executive Dashboard

Deploy the container.

```bash
gcloud run deploy $SERVICE_NAME \
--image=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY_NAME/$IMAGE_NAME:latest \
--region=$REGION \
--service-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com \
--port=8080 \
--cpu=2 \
--memory=2Gi \
--min-instances=0 \
--max-instances=20 \
--timeout=900 \
--concurrency=80 \
--no-allow-unauthenticated
```

---

## Recommended Cloud Run Configuration

| Setting | Recommended Value |
|----------|------------------|
| CPU | 2 |
| Memory | 2 GiB |
| Timeout | 900 seconds |
| Port | 8080 |
| Min Instances | 0 |
| Max Instances | 20 |
| Concurrency | 80 |
| Authentication | IAM |

These values can be adjusted based on workload size.

---

## Verify Deployment

```bash
gcloud run services list
```

Expected output

```
SERVICE

metadata-governance

READY
```

Retrieve the service URL.

```bash
gcloud run services describe $SERVICE_NAME \
--region=$REGION \
--format="value(status.url)"
```

Save the URL.

Example

```
https://metadata-governance-xxxxxxxx.run.app
```

---

# Step 14 - Configure Environment Variables

Update the Cloud Run service.

```bash
gcloud run services update $SERVICE_NAME \
--region=$REGION \
--update-env-vars \
BIGQUERY_DATASET=$DATASET_NAME,\
REGISTRY_PATH=registry,\
LOG_LEVEL=INFO,\
PYTHONUNBUFFERED=1
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| BIGQUERY_DATASET | Yes | BigQuery reporting dataset |
| REGISTRY_PATH | Yes | Registry folder |
| LOG_LEVEL | No | Logging level |
| PYTHONUNBUFFERED | Yes | Flush Python logs immediately |

Verify.

```bash
gcloud run services describe $SERVICE_NAME \
--region=$REGION
```

---

# Step 15 - Verify Cloud Run

Health Check

```bash
TOKEN=$(gcloud auth print-identity-token)

curl \
-H "Authorization: Bearer $TOKEN" \
https://YOUR_CLOUD_RUN_URL/health
```

Expected

```json
{
    "status":"healthy"
}
```

Verify Dashboard

```bash
curl \
-H "Authorization: Bearer $TOKEN" \
https://YOUR_CLOUD_RUN_URL/
```

---

# Step 16 - Create BigQuery Dataset

## Purpose

The platform stores all governance information inside BigQuery.

Create the dataset.

```bash
bq mk \
--location=$REGION \
$DATASET_NAME
```

Verify

```bash
bq ls
```

---

# Step 17 - Create BigQuery Reporting Tables

The platform uses four reporting tables.

| Table | Purpose |
|---------|----------|
| resource_snapshot | Current cloud inventory |
| compliance_snapshot | Compliance evaluation results |
| remediation_plan | Planned remediation |
| remediation_execution | Execution history |

---

## resource_snapshot

Purpose

Stores the discovered inventory from every Brownfield execution.

| Column | Type | Description |
|---------|------|-------------|
| run_id | STRING | Brownfield execution identifier |
| snapshot_time | TIMESTAMP | Discovery timestamp |
| project_id | STRING | Google Cloud Project |
| asset_type | STRING | Cloud Asset type |
| resource_name | STRING | Full Cloud Asset name |
| location | STRING | Region or Zone |
| labels | JSON | Current labels |
| tags | JSON | Resource Manager Tags |

---

## compliance_snapshot

Stores compliance evaluation.

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

Stores planned remediation actions.

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

Stores execution history.

| Column | Type |
|----------|------|
| execution_id | STRING |
| run_id | STRING |
| project_id | STRING |
| asset_type | STRING |
| resource_name | STRING |
| status | STRING |
| error_message | STRING |
| executed_at | TIMESTAMP |

---

Verify

```bash
bq ls $DATASET_NAME
```

Expected

```
resource_snapshot

compliance_snapshot

remediation_plan

remediation_execution
```

---

# Step 18 - Create Pub/Sub

Create the topic.

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

# Step 19 - Configure Logging Sink

Create the Logging Sink.

Organization example

```bash
gcloud logging sinks create metadata-governance-sink \
pubsub.googleapis.com/projects/$PROJECT_ID/topics/metadata-governance-events \
--organization=$ORGANIZATION_ID \
--log-filter='logName:"cloudaudit.googleapis.com"'
```

Project example

```bash
gcloud logging sinks create metadata-governance-sink \
pubsub.googleapis.com/projects/$PROJECT_ID/topics/metadata-governance-events
```

Verify

```bash
gcloud logging sinks list
```

---

# Step 20 - Grant Pub/Sub Publisher

Retrieve the writer identity.

```bash
gcloud logging sinks describe metadata-governance-sink
```

Grant publisher permissions.

```bash
gcloud pubsub topics add-iam-policy-binding metadata-governance-events \
--member="serviceAccount:LOGGING_WRITER_IDENTITY" \
--role="roles/pubsub.publisher"
```

---

# Step 21 - Create Eventarc Trigger

Eventarc forwards Pub/Sub messages to Cloud Run.

```bash
gcloud eventarc triggers create metadata-governance-trigger \
--location=$REGION \
--destination-run-service=$SERVICE_NAME \
--destination-run-region=$REGION \
--transport-topic=metadata-governance-events
```

Verify.

```bash
gcloud eventarc triggers list
```

Describe.

```bash
gcloud eventarc triggers describe metadata-governance-trigger \
--location=$REGION
```

Expected

```
ACTIVE
```

---

# Step 22 - Configure Governance Registry

Each application requires one registry file.

Example

```yaml
schemaVersion: v1

product: payments

team: cloud-platform

owner: john.doe

budgetOwner: finance

organization: example

department: engineering

costCenter: CC100

bindings:

- cloud: gcp
  projectId: payments-dev
  region: europe-west2
  environment: dev
  businessCriticality: medium
```

---

## Registry Structure

```
registry/

    payments.yaml

    banking.yaml

    platform.yaml

    analytics.yaml
```

One YAML file represents one application.

One application can contain multiple project bindings.

---

# Step 23 - Validate Registry

```bash
python validation/validate_registry.py
```

Expected

```
Validation Passed
```

---

# Step 24 - Configure Resource Manager Tags

Create Tag Keys.

Example

```
environment
```

Create Tag Values.

```
dev

test

uat

prod
```

Verify.

```bash
gcloud resource-manager tags keys list
```

Verify values.

```bash
gcloud resource-manager tags values list \
--parent=TAG_KEY_ID
```

---

# Step 25 - Verify Infrastructure

Cloud Run

```bash
gcloud run services list
```

BigQuery

```bash
bq ls
```

Pub/Sub

```bash
gcloud pubsub topics list
```

Eventarc

```bash
gcloud eventarc triggers list
```

Logging

```bash
gcloud logging sinks list
```

Artifact Registry

```bash
gcloud artifacts repositories list
```


# Step 26 - Validate Brownfield Governance

## Purpose

Brownfield Governance discovers existing Google Cloud resources, evaluates metadata compliance, generates remediation plans, and applies remediation where required.

Execute a Brownfield scan.

```bash
TOKEN=$(gcloud auth print-identity-token)

curl \
-H "Authorization: Bearer $TOKEN" \
"https://YOUR_CLOUD_RUN_URL/brownfield?project=YOUR_PROJECT_ID"
```

Example response.

```json
{
  "project":"YOUR_PROJECT_ID",
  "run_id":"761c615e-e4bf-426a-ae3a-b4e4d60641be",
  "status":"COMPLETED",
  "discovered":79604,
  "evaluated":2567,
  "planned":520,
  "successful":420,
  "failed":0
}
```

Verify:

- Resources discovered
- Supported resources evaluated
- Compliance calculated
- Remediation planned
- Execution completed
- BigQuery updated

---

# Step 27 - Validate Greenfield Governance

## Purpose

Greenfield Governance automatically evaluates newly created resources.

Create a supported resource.

Example

```bash
gcloud compute instances create governance-test-vm \
--project=YOUR_PROJECT_ID \
--zone=YOUR_ZONE \
--machine-type=e2-medium \
--image-family=debian-12 \
--image-project=debian-cloud
```

Expected workflow.

```
Compute Engine

↓

Cloud Audit Logs

↓

Logging Sink

↓

Pub/Sub

↓

Eventarc

↓

Cloud Run

↓

Classification

↓

Compliance

↓

Automatic Remediation

↓

BigQuery
```

---

# Step 28 - Verify Cloud Run Processing

Monitor Cloud Run logs.

```bash
gcloud beta run services logs tail $SERVICE_NAME \
--region=$REGION
```

Expected sequence.

```
Audit Event Received

↓

Classification Completed

↓

Resource Retrieved

↓

Compliance Evaluated

↓

Remediation Executed

↓

Execution Persisted

↓

Dashboard Updated
```

---

# Step 29 - Validate BigQuery

Open BigQuery.

Verify the reporting dataset.

```bash
bq ls $DATASET_NAME
```

Verify table contents.

```sql
SELECT COUNT(*) FROM resource_snapshot;
```

```sql
SELECT COUNT(*) FROM compliance_snapshot;
```

```sql
SELECT COUNT(*) FROM remediation_plan;
```

```sql
SELECT COUNT(*) FROM remediation_execution;
```

All tables should contain records.

---

# Step 30 - Validate Dashboard

Open

```
https://YOUR_CLOUD_RUN_URL
```

Verify:

## Executive Summary

- Total Resources
- Supported Resources
- Compliance %
- Projects

---

## Brownfield

Verify:

- Planned
- Completed
- Remaining
- Failed
- Success Rate

---

## Greenfield

Verify:

- Total Events
- Remediated
- Compliant
- Failed
- Average Processing Time

---

## Projects

Verify:

- Organization view
- Project filtering
- Resource counts

---

## Resource Types

Verify:

- Total resources
- Compliance
- Progress bars

---

## Recent Runs

Verify:

- Run ID
- Planned
- Completed
- Failed
- Success Rate

---

## Top Non-Compliant Resources

Verify:

- Resource
- Type
- Missing Metadata
- Incorrect Metadata

---

# Step 31 - Verify Google Cloud Components

Run the following commands.

Cloud Run

```bash
gcloud run services list
```

Cloud Run Logs

```bash
gcloud beta run services logs tail $SERVICE_NAME \
--region=$REGION
```

Artifact Registry

```bash
gcloud artifacts repositories list
```

BigQuery

```bash
bq ls
```

Eventarc

```bash
gcloud eventarc triggers list
```

Pub/Sub

```bash
gcloud pubsub topics list
```

Logging

```bash
gcloud logging sinks list
```

IAM

```bash
gcloud projects get-iam-policy $PROJECT_ID
```

---

# Supported Resource Types

| Google Cloud Service | Brownfield | Greenfield | Remediation |
|----------------------|:----------:|:----------:|:-----------:|
| Compute Engine VM | ✅ | ✅ | ✅ |
| Compute Disk | ✅ | ✅ | ✅ |
| Static IP Address | ✅ | ✅ | ✅ |
| Forwarding Rule | ✅ | ✅ | ✅ |
| Cloud Storage Bucket | ✅ | ✅ | ✅ |
| BigQuery Dataset | ✅ | ❌ | ✅ |
| Pub/Sub Topic | ✅ | ✅ | ✅ |
| Cloud SQL Instance | ✅ | ✅ | ✅ |
| Secret Manager Secret | ✅ | ✅ | ✅ |
| Artifact Registry | ✅ | ✅ | ✅ |
| Cloud KMS CryptoKey | ✅ | ✅ | ✅ |
| GKE Cluster | ✅ | ❌ | Planned |
| GKE Node Pool | ✅ | ❌ | Planned |

---

# Platform APIs

| Endpoint | Purpose |
|-----------|---------|
| GET / | Dashboard UI |
| GET /health | Health Check |
| GET /reports/dashboard | Executive Dashboard API |
| POST /brownfield | Execute Brownfield Governance |
| POST /execute | Execute Remediation Plan |

---

# Rollback Procedure

If deployment fails:

1. Stop Cloud Run deployment.
2. Restore previous Cloud Run revision.
3. Verify Eventarc trigger.
4. Verify Pub/Sub.
5. Verify BigQuery.
6. Redeploy previous container image.

Restore previous revision.

```bash
gcloud run revisions list \
--service=$SERVICE_NAME \
--region=$REGION
```

Route traffic back.

```bash
gcloud run services update-traffic \
$SERVICE_NAME \
--to-revisions=REVISION_NAME=100 \
--region=$REGION
```

---

# Upgrade Procedure

1. Pull latest source code.
2. Validate Governance Registry.
3. Build container.
4. Deploy Cloud Run.
5. Verify Health Check.
6. Execute Brownfield validation.
7. Execute Greenfield validation.
8. Validate Dashboard.

---

# Operational Best Practices

- Keep Governance Registry current.
- Review failed remediations daily.
- Review Cloud Run logs.
- Monitor BigQuery growth.
- Review IAM permissions.
- Validate Eventarc triggers.
- Validate Pub/Sub subscriptions.
- Backup Governance Registry.
- Protect the main branch.
- Monitor deployment costs.

---

# Deployment Validation Checklist

| Validation | Status |
|------------|--------|
| APIs Enabled | ☐ |
| IAM Configured | ☐ |
| Artifact Registry Created | ☐ |
| Cloud Run Deployed | ☐ |
| Environment Variables Configured | ☐ |
| BigQuery Dataset Created | ☐ |
| Reporting Tables Created | ☐ |
| Pub/Sub Configured | ☐ |
| Logging Sink Configured | ☐ |
| Eventarc Trigger Active | ☐ |
| Governance Registry Loaded | ☐ |
| Brownfield Working | ☐ |
| Greenfield Working | ☐ |
| Dashboard Operational | ☐ |

---

# Deployment Complete

The Enterprise Metadata Governance Platform is now fully deployed.

The platform continuously:

- Discovers Google Cloud resources.
- Evaluates metadata compliance.
- Automatically remediates supported resources.
- Monitors newly created resources.
- Produces executive governance reporting.
- Supports organization-level and project-level governance.