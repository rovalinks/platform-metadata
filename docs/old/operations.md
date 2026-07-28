# Operations Guide

# Purpose

This document describes the day-to-day operational activities required to monitor, maintain, and support the Enterprise Metadata Governance Platform.

The guide is intended for:

- Cloud Platform Engineers
- Operations Teams
- Support Engineers
- Site Reliability Engineers (SRE)

---

# Daily Health Checks

Verify:

- Cloud Run service is healthy
- Eventarc triggers are active
- Pub/Sub subscriptions are healthy
- BigQuery reporting is updating
- Dashboard is accessible

---

# Cloud Run

Verify service status.

```bash
gcloud run services list
```

Describe service.

```bash
gcloud run services describe metadata-governance \
--region=europe-west2
```

View logs.

```bash
gcloud beta run services logs tail metadata-governance \
--region=europe-west2
```

---

# Brownfield Operations

Execute Brownfield.

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
"https://<cloud-run-url>/brownfield?project=<project-id>"
```

Verify:

- Resources discovered
- Compliance evaluated
- Remediation planned
- Execution completed

---

# Greenfield Operations

Create a supported resource.

Verify:

- Audit Log generated
- Eventarc trigger fired
- Cloud Run received event
- Resource remediated

---

# Dashboard

Verify:

- Organization view
- Project view
- Resource Types
- Recent Runs
- Executive Summary

---

# BigQuery

Monitor reporting tables.

```sql
SELECT COUNT(*)
FROM resource_snapshot;
```

```sql
SELECT COUNT(*)
FROM compliance_snapshot;
```

```sql
SELECT COUNT(*)
FROM remediation_execution;
```

---

# Pub/Sub

Verify topics.

```bash
gcloud pubsub topics list
```

Verify subscriptions.

```bash
gcloud pubsub subscriptions list
```

---

# Eventarc

List triggers.

```bash
gcloud eventarc triggers list
```

Describe trigger.

```bash
gcloud eventarc triggers describe <trigger>
```

---

# Governance Registry

Validate registry before deployment.

Check:

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

# Resource Manager Tags

Verify:

- Tag Keys
- Tag Values
- Tag Bindings

---

# Backup

Backup:

- Registry
- BigQuery Dataset
- Terraform State
- Documentation

---

# Monitoring

Monitor:

- Cloud Run errors
- Eventarc failures
- Pub/Sub backlog
- BigQuery failures
- IAM changes

---

# Incident Response

If governance stops working:

1. Check Cloud Run.
2. Check Eventarc.
3. Check Pub/Sub.
4. Check BigQuery.
5. Check IAM.
6. Check Registry.

---

# Upgrade Process

1. Pull latest source.
2. Review release notes.
3. Terraform plan.
4. Terraform apply.
5. Deploy Cloud Run.
6. Execute Brownfield validation.
7. Execute Greenfield validation.
8. Validate dashboard.

---

# Operational Best Practices

- Monitor Cloud Run logs daily.
- Execute Brownfield after onboarding a new project.
- Keep the Governance Registry up to date.
- Review failed remediations regularly.
- Apply least-privilege IAM.
- Review dashboard KPIs weekly.

---

# Summary

The platform is designed for continuous operation using managed Google Cloud services. Regular monitoring, registry maintenance, and validation of Brownfield and Greenfield workflows help ensure consistent metadata governance across the cloud estate.