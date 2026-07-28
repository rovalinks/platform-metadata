# Deployment Guide

# Purpose

This document describes how to deploy the Enterprise Metadata Governance Platform into a Google Cloud environment using Terraform.

The deployment provisions all required Google Cloud services, IAM permissions, Cloud Run services, Eventarc triggers, Pub/Sub resources, BigQuery datasets, and supporting infrastructure.

---

# Prerequisites

Before deployment ensure the following prerequisites are met.

## Google Cloud

- Organization Administrator (or delegated permissions)
- Billing enabled
- Organization ID
- Folder or Project
- Terraform installed
- Google Cloud SDK installed
- Python 3.12+

---

# Required Google Cloud APIs

Enable the following APIs.

- Cloud Resource Manager API
- Cloud Asset API
- Cloud Run API
- Cloud Build API
- Artifact Registry API
- Eventarc API
- Pub/Sub API
- BigQuery API
- Cloud Logging API
- Secret Manager API
- IAM API
- Service Usage API

---

# Infrastructure Components

Terraform deploys the following components.

## Core

- Cloud Run
- Artifact Registry
- BigQuery
- Pub/Sub
- Eventarc
- Logging
- IAM

---

## Governance

- Governance Registry
- Reporting Dataset
- Brownfield Services
- Greenfield Services

---

# Repository Structure

```
terraform/
cloudrun/
registry/
docs/
```

---

# Terraform Modules

Current Terraform modules include:

- project-services
- iam
- cloud-run
- artifact-registry
- eventarc
- pubsub
- bigquery
- organization-logging
- scheduler
- monitoring

Each module is independently deployable.

---

# Deployment Steps

## Step 1

Clone the repository.

```bash
git clone <repository>
cd platform-metadata-governance
```

---

## Step 2

Authenticate.

```bash
gcloud auth login

gcloud auth application-default login
```

---

## Step 3

Select the target project.

```bash
gcloud config set project PROJECT_ID
```

---

## Step 4

Initialize Terraform.

```bash
terraform init
```

---

## Step 5

Validate.

```bash
terraform validate
```

---

## Step 6

Review deployment.

```bash
terraform plan
```

---

## Step 7

Deploy infrastructure.

```bash
terraform apply
```

---

# Cloud Run Deployment

Cloud Run hosts the governance platform.

Deployment includes:

- Container build
- Artifact Registry image
- Cloud Run service
- Service account
- IAM bindings

Cloud Run remains stateless.

---

# Event Processing

Greenfield governance uses:

Cloud Audit Logs

↓

Logging Sink

↓

Pub/Sub

↓

Eventarc

↓

Cloud Run

---

# Brownfield Processing

Brownfield processing is executed on demand.

Workflow:

Discovery

↓

Compliance

↓

Planning

↓

Execution

↓

Reporting

---

# Governance Registry

The registry must be populated before remediation.

Each application requires:

- Product
- Team
- Owner
- Budget Owner
- Organization
- Department
- Cost Center
- Environment
- Business Criticality

---

# BigQuery

Deployment creates reporting tables including:

- resource_snapshot
- compliance_snapshot
- remediation_plan
- remediation_execution

These tables support reporting and dashboard functionality.

---

# Verification

Verify the deployment.

## Infrastructure

- Terraform Apply completed
- Cloud Run deployed
- Artifact Registry created
- BigQuery dataset created
- Eventarc trigger created
- Pub/Sub topic created

---

## Brownfield

Execute a brownfield scan.

Verify:

- Discovery
- Compliance
- Planning
- Execution
- Reporting

---

## Greenfield

Create a supported Google Cloud resource.

Verify:

- Audit Log generated
- Event received
- Classification completed
- Compliance evaluated
- Metadata applied
- Dashboard updated

---

## Dashboard

Verify:

- Organization scope
- Project scope
- Executive Summary
- Brownfield metrics
- Greenfield metrics
- Compliance reporting
- Recent remediation runs

---

# Troubleshooting

Common validation steps:

- Check Cloud Run logs.
- Verify Eventarc trigger status.
- Verify Pub/Sub message delivery.
- Verify BigQuery tables contain data.
- Confirm Governance Registry entries exist.
- Verify IAM permissions.
- Confirm supported resource types.

---

# Upgrade Strategy

The platform supports incremental updates.

Recommended process:

1. Pull latest source.
2. Review Terraform plan.
3. Apply infrastructure changes.
4. Deploy Cloud Run image.
5. Validate dashboard.
6. Execute brownfield validation.
7. Execute greenfield validation.

---

# Summary

Deployment is fully automated through Terraform and follows Infrastructure as Code principles. Once deployed, the platform continuously governs supported Google Cloud resources using both scheduled brownfield workflows and event-driven greenfield automation.