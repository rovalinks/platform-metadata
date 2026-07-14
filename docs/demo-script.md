# Enterprise Metadata Governance Platform

# Demonstration Guide

## Purpose

This document provides a step-by-step demonstration of the Enterprise Metadata Governance Platform.

The demonstration showcases:

- Brownfield Governance
- Greenfield Governance
- Executive Dashboard

Estimated duration:

**10-15 minutes**

---

# Demonstration Objectives

By the end of the demonstration the audience should understand:

- The business problem
- The platform architecture
- Brownfield governance
- Greenfield governance
- Executive reporting
- Enterprise scalability

---

# Agenda

| Time | Topic |
|------|-------|
| 2 min | Business Problem |
| 2 min | Architecture |
| 3 min | Brownfield Governance |
| 3 min | Greenfield Governance |
| 3 min | Executive Dashboard |
| 2 min | Questions |

---

# Step 1 - Business Problem

Explain:

Large enterprises typically have thousands of cloud resources.

Without governance they experience:

- Missing ownership
- Missing cost allocation
- Inconsistent metadata
- Governance drift
- Difficult FinOps reporting
- Difficult operational support

The platform automates metadata governance across the cloud estate.

---

# Step 2 - Architecture

Show:

Architecture Diagram

Explain:

Registry

↓

Brownfield

↓

Greenfield

↓

Reporting

↓

Dashboard

Highlight:

- Cloud Run
- Eventarc
- Pub/Sub
- BigQuery
- Governance Registry

---

# Step 3 - Brownfield Governance

Call:

```
/brownfield?project=platform-metadata-demo
```

Example:

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
"https://<cloud-run-url>/brownfield?project=platform-metadata-demo"
```

Explain:

The platform:

- Discovers resources
- Evaluates compliance
- Generates a remediation plan
- Executes remediation
- Records execution history

Discuss the response fields:

- Discovered
- Evaluated
- Planned
- Successful
- Failed
- Run ID

---

# Step 4 - Greenfield Governance

Create a supported resource.

Example:

```bash
gcloud compute instances create demo-vm \
    --project=platform-metadata-demo \
    --zone=europe-west2-a \
    --machine-type=e2-medium \
    --image-family=debian-12 \
    --image-project=debian-cloud
```

Explain:

The platform automatically:

- Receives the Audit Log
- Classifies the resource
- Evaluates compliance
- Applies labels or Resource Manager Tags
- Updates reporting

Show Cloud Run logs:

```bash
gcloud beta run services logs tail metadata-governance \
    --region=europe-west2
```

Highlight:

- Event received
- Classification
- Compliance evaluation
- Automatic remediation

---

# Step 5 - Executive Dashboard

Open:

```
https://<cloud-run-url>/
```

Walk through:

## Executive Summary

Explain:

- Total resources
- Supported resources
- Compliance percentage
- Brownfield metrics
- Greenfield metrics

---

## Projects

Show:

- Organization view
- Project view

Explain:

Leadership can understand governance across the cloud estate or focus on an individual project.

---

## Resource Types

Explain:

Compliance grouped by service.

Highlight:

- Compute
- Storage
- BigQuery
- Pub/Sub
- Cloud SQL

---

## Recent Remediation Runs

Explain:

Every remediation execution is fully auditable.

---

## Top Non-Compliant Resources

Explain:

Shows resources requiring governance attention.

---

# Questions You May Be Asked

## Why both Brownfield and Greenfield?

Brownfield governs existing resources.

Greenfield prevents future governance drift.

Together they provide continuous governance.

---

## Does it scale?

Yes.

The platform is stateless and designed for enterprise environments with tens of thousands of resources across multiple projects.

---

## Does it support additional resource types?

Yes.

The adapter architecture allows new Google Cloud services to be added with minimal changes.

---

## Does it overwrite customer metadata?

No.

The platform preserves customer-managed labels and Resource Manager Tags.

Only governance-managed metadata is updated.

---

## Can it operate across multiple projects?

Yes.

The dashboard supports both organization-level and project-level reporting.

---

# Troubleshooting During the Demo

If Brownfield returns no resources:

- Verify Cloud Asset API
- Verify IAM permissions
- Verify project configuration

---

If Greenfield events are not received:

- Verify Eventarc trigger
- Verify Pub/Sub topic
- Verify Logging Sink
- Check Cloud Run logs

---

If the dashboard is empty:

- Verify BigQuery tables
- Execute a Brownfield scan
- Refresh the dashboard

---

# Key Messages

Emphasize:

- Cloud-native architecture
- Automated governance
- Enterprise scalability
- Modular design
- Infrastructure as Code
- Executive reporting
- Continuous compliance

---

# Summary

The Enterprise Metadata Governance Platform provides a scalable, cloud-native solution for metadata governance across Google Cloud. By combining Brownfield discovery, Greenfield event-driven remediation, centralized reporting, and an executive dashboard, the platform enables organizations to maintain consistent metadata standards while reducing manual effort and improving operational visibility.