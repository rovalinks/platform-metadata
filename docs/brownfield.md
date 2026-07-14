# Brownfield Governance

# Purpose

This document describes how the Enterprise Metadata Governance Platform discovers, evaluates, remediates, and reports on existing Google Cloud resources.

Brownfield governance is responsible for bringing an existing cloud estate into compliance with the organization's metadata standards.

---

# Overview

Brownfield governance processes existing Google Cloud resources that were created before the platform was deployed or resources that have drifted from the expected governance state.

The workflow consists of five stages:

1. Discovery
2. Compliance Evaluation
3. Remediation Planning
4. Remediation Execution
5. Reporting

Each stage is independent and produces auditable outputs.

---

# Brownfield Workflow

```
Brownfield Request
        │
        ▼
Resource Discovery
        │
        ▼
Compliance Evaluation
        │
        ▼
Remediation Planning
        │
        ▼
Remediation Execution
        │
        ▼
BigQuery Reporting
        │
        ▼
Executive Dashboard
```

---

# Discovery

The Discovery Service inventories supported Google Cloud resources within the target project.

Responsibilities:

- Enumerate supported resources
- Normalize resource metadata
- Read existing labels
- Read existing Resource Manager Tags
- Produce a common resource model

Discovery never modifies resources.

---

# Supported Resource Types

Current supported resources include:

- Compute Engine Instances
- Compute Engine Disks
- Cloud Storage Buckets
- BigQuery Datasets
- Pub/Sub Topics
- Artifact Registry Repositories
- Cloud SQL Instances
- Secret Manager Secrets
- Cloud KMS Keys

Additional resource types can be added through the adapter architecture.

---

# Compliance Evaluation

The Compliance Service compares discovered metadata against the Governance Registry.

Checks include:

- Missing labels
- Incorrect labels
- Missing Resource Manager Tags
- Incorrect Resource Manager Tags

Outputs include:

- Compliant
- Non-compliant
- Missing metadata
- Incorrect metadata

Evaluation is read-only.

---

# Governance Registry

The Governance Service loads the expected metadata for the project from the Governance Registry.

Expected metadata includes:

- Product
- Team
- Owner
- Budget Owner
- Organization
- Department
- Cost Center
- Environment
- Business Criticality

The registry is the single source of truth.

---

# Remediation Planning

The Planner Service generates a remediation plan without modifying resources.

Each planned action includes:

- Resource
- Project
- Asset Type
- Current Metadata
- Expected Metadata
- Planned Action

Plans are stored in BigQuery.

---

# Remediation Execution

The Execution Service applies the remediation plan.

Responsibilities:

- Apply labels
- Apply Resource Manager Tags
- Preserve customer-managed metadata
- Update execution status

Execution is idempotent.

Previously completed remediation actions are not executed again.

---

# Label Ownership

The platform only manages metadata owned by the Governance Registry.

Customer-managed metadata is preserved.

This prevents accidental removal of application-specific labels or tags.

---

# BigQuery Reporting

Brownfield processing writes results to BigQuery.

Primary reporting tables:

- resource_snapshot
- compliance_snapshot
- remediation_plan
- remediation_execution

These tables provide a complete audit history.

---

# Reporting

The Reporting Service provides:

- Executive summary
- Compliance metrics
- Project reporting
- Resource reporting
- Remediation history
- Execution history

The reporting layer is read-only.

---

# Error Handling

Common failure scenarios include:

- Resource deleted during execution
- Permission denied
- Unsupported resource type
- Invalid registry configuration
- API rate limiting

Failures are recorded in the remediation execution history.

---

# Scalability

The brownfield workflow is designed for enterprise environments.

Key characteristics:

- Stateless execution
- Parallel processing
- Modular adapters
- Incremental remediation
- Idempotent execution
- Project-level execution
- Organization-level reporting

---

# Summary

Brownfield governance provides automated remediation of existing Google Cloud resources by combining discovery, compliance evaluation, governance policy, remediation execution, and centralized reporting into a scalable enterprise workflow.