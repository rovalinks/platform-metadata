# Troubleshooting Guide

# Purpose

This document provides troubleshooting guidance for common issues encountered when deploying and operating the Enterprise Metadata Governance Platform.

It covers Brownfield governance, Greenfield governance, reporting, dashboard, Cloud Run, Eventarc, Pub/Sub, BigQuery, IAM, and the Governance Registry.

---

# Deployment Issues

## Terraform Apply Fails

### Symptoms

- Resources fail to deploy
- Terraform exits with an error

### Checks

- Verify APIs are enabled
- Verify IAM permissions
- Verify billing is enabled
- Verify project ID
- Verify Terraform variables

---

## Cloud Run Deployment Fails

### Symptoms

Deployment fails.

### Checks

```bash
gcloud run services list
```

```bash
gcloud builds list
```

```bash
gcloud builds log BUILD_ID
```

Verify:

- Artifact Registry exists
- Image was built
- IAM permissions
- Service Account

---

# Cloud Run

## 403 Forbidden

### Symptoms

```
403 Forbidden
```

### Cause

Cloud Run requires authentication.

### Resolution

```bash
curl \
-H "Authorization: Bearer $(gcloud auth print-identity-token)" \
https://<cloud-run-url>/
```

or grant public access if appropriate.

---

## Cloud Run Returns 500

### Checks

```bash
gcloud beta run services logs tail metadata-governance \
--region=europe-west2
```

Look for:

- Python exceptions
- Missing environment variables
- BigQuery errors
- IAM errors

---

## Slow Dashboard

### Cause

Dashboard executes multiple BigQuery queries.

### Resolution

- Verify Cloud Run is warm
- Cache dashboard responses
- Execute queries in parallel
- Avoid unnecessary refreshes

---

# IAM

## Permission Denied

### Symptoms

```
PERMISSION_DENIED
```

### Checks

Verify:

- Cloud Run Service Account
- IAM bindings
- Organization permissions
- Project permissions

Refer to:

```
docs/iam-permissions.md
```

---

# Cloud Asset Inventory

## No Resources Found

### Symptoms

Brownfield returns zero resources.

### Checks

Verify:

- Cloud Asset API enabled
- Cloud Asset Viewer role
- Correct project
- Billing enabled

---

# Brownfield

## Resources Discovered But Few Evaluated

### Symptoms

```
Discovered: 90,000

Evaluated: 2,500
```

### Explanation

Discovery inventories all resources.

Compliance only evaluates supported resource types.

This is expected behavior.

---

## No Remediation Planned

### Symptoms

```
planned = 0
```

### Explanation

Resources are already compliant.

No remediation is required.

---

## Run Already Executed

### Symptoms

```
Run already executed
```

### Explanation

Execution is idempotent.

The platform prevents duplicate execution of the same remediation plan.

---

# Greenfield

## Event Not Received

### Checks

Verify:

```bash
gcloud eventarc triggers list
```

Verify:

```bash
gcloud pubsub topics list
```

Verify:

```bash
gcloud pubsub subscriptions list
```

Verify:

Cloud Run logs.

---

## Resource Not Remediated

Possible causes:

- Unsupported resource
- Registry missing
- IAM failure
- Resource deleted
- API failure

Check Cloud Run logs.

---

## Unsupported Event

### Symptoms

```
Unsupported audit event
```

### Explanation

The event is not mapped by the Classification Service.

The platform ignores unsupported events.

---

# Registry

## Project Not Found

### Symptoms

```
No registry entry found
```

### Resolution

Verify the registry contains:

- Product
- Project ID
- Environment
- Team
- Owner

---

## Incorrect Metadata Applied

Verify:

- Registry values
- Project binding
- Expected labels
- Expected Resource Manager Tags

---

# Dashboard

## Projects Missing

### Cause

Organization reporting queries only return projects present in reporting tables.

### Resolution

Run Brownfield against the project.

Verify reporting tables.

---

## Project Filter Empty

Verify:

- Registry
- Reporting data
- Project exists
- Dashboard API response

---

## Tables Render Incorrectly

### Cause

Duplicate HTML element IDs or malformed table markup.

### Resolution

Verify:

- Unique container IDs
- Valid HTML
- Browser developer console

---

## Dashboard Does Not Refresh

Verify:

- Browser cache
- JavaScript console
- Dashboard API
- Cloud Run logs

---

# BigQuery

## Reporting Tables Empty

Verify Brownfield execution.

Verify Greenfield execution.

Verify BigQuery dataset.

---

## BigQuery Permission Error

Verify:

- BigQuery Job User
- BigQuery Data Viewer
- BigQuery Data Editor

---

# Pub/Sub

## No Messages

Verify:

- Topic exists
- Subscription exists
- IAM
- Logging Sink

---

# Eventarc

## Trigger Not Firing

Verify:

```bash
gcloud eventarc triggers describe TRIGGER_NAME
```

Verify:

- Event filters
- Region
- Pub/Sub
- Logging Sink

---

# Logging

## No Audit Logs

Verify:

Cloud Logging

↓

Logging Sink

↓

Pub/Sub

↓

Eventarc

↓

Cloud Run

Any break in this chain prevents Greenfield processing.

---

# Resource Manager Tags

## TagBinding Failed

Possible causes:

- TagKey missing
- TagValue missing
- IAM
- Unsupported resource

Verify TagBindings using:

```bash
gcloud resource-manager tags bindings list
```

---

# Performance

## Slow Brownfield

Expected when:

- Large estates
- First discovery
- Cold Cloud Run instance

Mitigation:

- Execute per project
- Use parallel processing
- Increase Cloud Run resources

---

# Common Validation Commands

Cloud Run

```bash
gcloud run services list
```

Cloud Run Logs

```bash
gcloud beta run services logs tail metadata-governance \
--region=europe-west2
```

Eventarc

```bash
gcloud eventarc triggers list
```

Pub/Sub

```bash
gcloud pubsub topics list
```

BigQuery

```bash
bq ls
```

IAM

```bash
gcloud projects get-iam-policy PROJECT_ID
```

---

# Support Checklist

Before raising an issue verify:

- APIs enabled
- Billing enabled
- IAM configured
- Registry configured
- Cloud Run healthy
- Eventarc healthy
- Pub/Sub healthy
- BigQuery healthy
- Brownfield working
- Greenfield working
- Dashboard working

---

# Summary

Most deployment and runtime issues can be resolved by validating IAM permissions, Google Cloud service configuration, reporting data, and the Governance Registry. Following the troubleshooting steps in this guide should resolve the majority of operational issues without requiring code changes.