# Platform Metadata Governance

# Deployment Guide

---

# Overview

This document describes how to deploy the Platform Metadata Governance solution into a Google Cloud project.

The deployment provisions:

- Artifact Registry
- IAM
- Service Accounts
- Workload Identity Federation
- Cloud Run
- GitHub Actions CI/CD

The platform uses GitHub Actions together with Google Cloud Workload Identity Federation.

No service account keys are required.

---

# Deployment Architecture

```
Developer

    │

    ▼

GitHub Repository

    │

    ▼

GitHub Actions

    │

    ▼

Workload Identity Federation

    │

    ▼

Docker Build

    │

    ▼

Artifact Registry

    │

    ▼

Cloud Run

    │

    ▼

Platform Metadata Governance
```

---

# Prerequisites

Install the following software.

## Git

Verify

```bash
git --version
```

---

## Terraform

Verify

```bash
terraform version
```

Recommended version

Terraform 1.8+

---

## Google Cloud SDK

Verify

```bash
gcloud version
```

---

## Docker

Verify (Not Mandatory)

```bash
docker version
```

---

# Create Google Cloud Project

Create a project.

```bash
gcloud projects create PROJECT_ID
```

Example

```bash
gcloud projects create platform-metadata-demo
```

Set the active project.

```bash
gcloud config set project platform-metadata-demo
```

Attach a billing account.

---

# Enable Required APIs

Enable the following services.

```bash
gcloud services enable \
artifactregistry.googleapis.com \
cloudasset.googleapis.com \
run.googleapis.com \
iam.googleapis.com \
iamcredentials.googleapis.com \
cloudresourcemanager.googleapis.com \
serviceusage.googleapis.com
```

Verify

```bash
gcloud services list --enabled
```

---

# Clone Repository

Clone the repository.

```bash
git clone <repository>

cd platform-metadata-governance
```

---

# Configure Terraform

Copy

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Open

```
terraform.tfvars
```

Update

- project_id
- region
- repository
- github owner
- github repository

Example

```hcl
project_id = "platform-metadata-demo"

region = "europe-west2"

artifact_registry_repository = "platform-images"

deploy_cloud_run = true
```

---

# Deploy Infrastructure

Move into Terraform.

```bash
cd terraform
```

Initialise.

```bash
terraform init
```

Validate.

```bash
terraform validate
```

Review.

```bash
terraform plan
```

Deploy.

```bash
terraform apply
```

Terraform provisions

- Service Accounts
- IAM Roles
- Artifact Registry
- Workload Identity Federation
- Cloud Run

Wait for deployment to complete successfully before continuing.

# Configure GitHub

Open your GitHub repository.

Navigate to:

```text
Settings
↓
Secrets and variables
↓
Actions
```

Create the following repository secrets.

| Secret                | Description                                   | Example                                                                                           |
| --------------------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| `WIF_PROVIDER`        | Full Workload Identity Provider resource name | `projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `WIF_SERVICE_ACCOUNT` | GitHub Actions service account email          | `github-actions-sa@my-project.iam.gserviceaccount.com`                                            |

## How to obtain the values

### `WIF_PROVIDER`

Retrieve the full Workload Identity Provider resource name:

```bash
gcloud iam workload-identity-pools providers describe github-provider \
    --location=global \
    --workload-identity-pool=github-pool \
    --format="value(name)"
```

Example output:

```text
projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider
```

Copy this value into the `WIF_PROVIDER` GitHub secret.

If you don't know the provider name, list the available providers first:

```bash
gcloud iam workload-identity-pools providers list \
    --location=global \
    --workload-identity-pool=github-pool
```

### `WIF_SERVICE_ACCOUNT`

Retrieve the service account email:

```bash
gcloud iam service-accounts list
```

Example output:

```text
NAME                  EMAIL
GitHub Actions SA     github-actions-sa@my-project.iam.gserviceaccount.com
```

Copy the **EMAIL** value into the `WIF_SERVICE_ACCOUNT` GitHub secret.

If you already know the service account name, you can retrieve just its email:

```bash
gcloud iam service-accounts describe \
    github-actions-sa@my-project.iam.gserviceaccount.com \
    --format="value(email)"
```
---

# Configure Branch Protection

Protect the **main** branch.

Navigate to

```
Settings

↓

Branches

↓

Add Rule
```

Configure

- Require a pull request before merging
- Require approvals
- Dismiss stale approvals
- Require status checks
- Require conversation resolution
- Restrict direct pushes to main

This ensures that registry changes cannot be merged without validation and approval.

---

# Configure GitHub Actions

The deployment workflow is located at

```
.github/workflows/deploy.yml
```

Deployment is triggered automatically when code is merged into the **main** branch.

Pipeline

```
Git Push

↓

GitHub Actions

↓

Authenticate using Workload Identity Federation

↓

Build Docker Image

↓

Push Image to Artifact Registry

↓

Deploy Cloud Run
```

No service account keys are required.

---

# Verify Workload Identity Federation

Verify authentication by checking the GitHub Actions logs.

Successful authentication should show

```
Authenticated with Workload Identity Federation
```

No JSON service account keys should exist in the repository.

---

# Verify Infrastructure

After Terraform completes, verify each component.

## Service Accounts

```bash
gcloud iam service-accounts list
```

Expected

- terraform-sa
- github-actions-sa
- governance-engine-sa
- cloud-build-sa

---

## Artifact Registry

```bash
gcloud artifacts repositories list
```

Expected

```
platform-images
```

---

## Cloud Run

```bash
gcloud run services list
```

Expected

```
metadata-governance
```

---

## Workload Identity Pool

```bash
gcloud iam workload-identity-pools list \
--location=global
```

Expected

```
github-pool
```

---

## Workload Identity Provider

```bash
gcloud iam workload-identity-pools providers list \
--workload-identity-pool=github-pool \
--location=global
```

Expected

```
github-provider
```

---

# Deploy the Application

Create a feature branch.

```bash
git checkout -b feature/my-change
```

Make the required changes.

Commit.

```bash
git add .

git commit -m "Describe change"
```

Push.

```bash
git push origin feature/my-change
```

Open a Pull Request.

After approval, merge into **main**.

GitHub Actions automatically

- Builds the Docker image
- Pushes the image to Artifact Registry
- Deploys Cloud Run

No manual deployment is required.

---

# Verify Cloud Run

Retrieve the service URL.

```bash
gcloud run services describe metadata-governance \
--region=europe-west2 \
--format="value(status.url)"
```

Example

```
https://metadata-governance-xxxxx-ew.a.run.app
```

---

# Verify Platform APIs

Verify each endpoint.

## Health

```
GET /health
```

Expected

```
200 OK
```

---

## Discovery

```
GET /discover
```

Returns all discovered Google Cloud resources.

---

## Compliance

```
GET /compliance
```

Returns

- compliant resources
- missing labels
- incorrect labels
- compliance summary

---

## Verification

```
GET /verify
```

Verifies that expected metadata exists after enforcement.

---

## Enforcement

```
GET /enforce
```

Applies missing labels to supported resources.

Current supported resources

- Compute Engine
- BigQuery Dataset

---

## Report

```
GET /report
```

Returns

- Total resources
- Supported resources
- Compliant resources
- Non-compliant resources
- Enforcement candidates
- Compliance percentage

---

# Registry Workflow

Every application is represented by an individual registry file.

Example

```
registry/applications/

APP000001.yaml

APP000002.yaml

APP000003.yaml
```

To onboard a new application

1. Create a feature branch.

2. Create a new YAML file.

3. Commit the file.

4. Push the branch.

5. Open a Pull Request.

6. Registry validation executes automatically.

7. Obtain approval.

8. Merge into **main**.

9. GitHub Actions automatically deploys the latest platform.

No Python code changes are required.

---

# Validate Registry

Registry validation runs automatically during every Pull Request.

Validation includes

- YAML syntax
- JSON Schema
- Required fields
- Project bindings
- Metadata structure

Pull Requests cannot be merged until validation succeeds.

---

# Platform Validation

Verify the following workflow.

```
Create Registry File

↓

Pull Request

↓

Registry Validation

↓

Approval

↓

Merge

↓

GitHub Actions

↓

Cloud Run Deployment

↓

Platform Ready
```

---

# Operational Flow

```
Application Registry

↓

Governance Service

↓

Cloud Asset Inventory

↓

Discovery Service

↓

Compliance Service

↓

Enforcement Planner

↓

Executor

↓

Resource Adapter

↓

Google Cloud APIs
```

---

# Monitoring

Application logs are automatically written to Cloud Logging.

View logs.

```bash
gcloud logging read \
"resource.type=cloud_run_revision"
```

Logs include

- Discovery
- Compliance
- Enforcement
- Verification
- Reporting

---

# Updating the Platform

Create a feature branch.

```bash
git checkout -b feature/update
```

Commit changes.

```bash
git add .

git commit -m "Platform enhancement"
```

Push.

```bash
git push origin feature/update
```

Create a Pull Request.

After approval, merge into **main**.

Deployment occurs automatically.

---

# Destroy Infrastructure

Destroy the environment.

```bash
cd terraform

terraform destroy
```

---

# Known Google Cloud Behaviour

Google Cloud Workload Identity Pools use a soft-delete lifecycle.

If a pool is deleted, Google reserves the pool identifier for a retention period.

Attempting to recreate a pool immediately after deletion may result in

```
409 Requested entity already exists
```

If this occurs

- Restore the existing pool

or

- Create a new Workload Identity Pool ID

This is expected Google Cloud behaviour.

---

# Troubleshooting

## GitHub Authentication

Verify

- WIF_PROVIDER
- WIF_SERVICE_ACCOUNT

Check GitHub Actions logs.

---

## Cloud Run Deployment

Verify

```bash
gcloud run services list
```

---

## Artifact Registry

Verify

```bash
gcloud artifacts repositories list
```

---

## Registry Validation Failure

Run locally

```bash
python validation/validate_registry.py
```

---

## Unit Tests

Run

```bash
pytest
```

All tests should pass before merging into **main**.

---

# Next Steps

After successful deployment you can

- Onboard new applications
- Discover resources
- Evaluate compliance
- Apply metadata
- Verify remediation
- Generate governance reports

The platform is now ready for operational use.
