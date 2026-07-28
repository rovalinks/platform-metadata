# Greenfield Governance

# Purpose

This document describes how the Enterprise Metadata Governance Platform automatically governs newly created Google Cloud resources using an event-driven architecture.

Unlike Brownfield governance, which evaluates existing resources, Greenfield governance provides near real-time metadata enforcement immediately after supported resources are created.

---

# Overview

Greenfield governance continuously monitors Google Cloud Audit Logs for supported resource creation events.

When a supported resource is created, the platform automatically:

1. Receives the event
2. Classifies the resource
3. Retrieves the resource metadata
4. Evaluates compliance
5. Applies required metadata
6. Records execution results
7. Updates reporting data

No user interaction is required.

---

# Greenfield Workflow

```
Google Cloud Resource Created
            │
            ▼
Cloud Audit Logs
            │
            ▼
Logging Sink
            │
            ▼
Pub/Sub Topic
            │
            ▼
Eventarc Trigger
            │
            ▼
Cloud Run
            │
            ▼
Audit Log Parser
            │
            ▼
Classification Service
            │
            ▼
Resource Adapter
            │
            ▼
Compliance Engine
            │
            ▼
Governance Engine
            │
            ▼
Automatic Remediation
            │
            ▼
Execution Repository
            │
            ▼
Executive Dashboard
```

---

# Event Sources

The platform consumes Cloud Audit Log events published through Eventarc.

Typical supported events include:

- Compute Engine Instance creation
- Compute Engine Disk creation
- Cloud Storage Bucket creation
- BigQuery Dataset creation
- Pub/Sub Topic creation
- Cloud SQL Instance creation
- Artifact Registry Repository creation
- Secret Manager Secret creation
- Cloud KMS Key creation

Unsupported events are ignored.

---

# Audit Log Processing

Cloud Audit Log events are delivered to Cloud Run through Eventarc and Pub/Sub.

Responsibilities include:

- Decode Audit Log payload
- Validate event structure
- Extract project information
- Extract resource information
- Normalize method names

Unsupported or malformed events are safely ignored.

---

# Classification

The Classification Service determines which supported resource type generated the event.

Responsibilities:

- Identify Google Cloud service
- Normalize Audit Log method names
- Select appropriate classifier
- Produce a Resource Event

If no classifier matches, processing stops without error.

---

# Resource Resolution

After classification, the appropriate resource adapter retrieves the latest resource state.

Responsibilities:

- Resolve full resource name
- Read labels
- Read Resource Manager Tags
- Build normalized resource model

If the resource no longer exists, processing ends gracefully.

---

# Compliance Evaluation

The Compliance Engine compares the resource metadata against the Governance Registry.

Checks include:

- Missing labels
- Incorrect labels
- Missing Resource Manager Tags
- Incorrect Resource Manager Tags

Compliant resources require no further action.

---

# Governance

The Governance Service loads the expected metadata for the project.

Metadata includes:

- Product
- Team
- Owner
- Budget Owner
- Organization
- Department
- Cost Center
- Environment
- Business Criticality

The Governance Registry remains the single source of truth.

---

# Automatic Remediation

If the resource is not compliant, the Execution Service automatically applies the required metadata.

Depending on the resource capabilities, remediation may include:

- Labels
- Resource Manager Tags

Customer-managed metadata is preserved.

---

# Execution Reporting

Every remediation is recorded.

Execution history includes:

- Resource
- Project
- Asset Type
- Status
- Error Message
- Execution Timestamp

These records support auditing and dashboard reporting.

---

# Error Handling

The platform safely handles common scenarios including:

- Unsupported resource types
- Missing resources
- Deleted resources
- Permission failures
- API failures
- Temporary service errors

Processing continues without affecting unrelated events.

---

# Performance

Greenfield processing is designed for low-latency operation.

Characteristics include:

- Stateless Cloud Run execution
- Event-driven processing
- No polling
- Automatic scaling
- Independent event processing

---

# Scalability

The Greenfield architecture supports:

- Multiple Google Cloud projects
- Organization-wide governance
- High event throughput
- Independent Cloud Run scaling
- Parallel event processing

---

# Security

The platform follows Google Cloud security best practices.

Principles include:

- Least privilege IAM
- Dedicated service accounts
- Cloud Audit Logs
- Workload Identity
- No embedded credentials

---

# Relationship to Brownfield

Brownfield and Greenfield governance are complementary.

Brownfield:

- Evaluates existing resources
- Performs bulk remediation
- Produces estate-wide compliance reports

Greenfield:

- Evaluates newly created resources
- Automatically remediates non-compliant resources
- Prevents governance drift

Together they provide continuous governance across the cloud estate.

---

# Summary

Greenfield governance enables near real-time metadata enforcement using Google Cloud's native event-driven services. By integrating Cloud Audit Logs, Eventarc, Pub/Sub, Cloud Run, and the Governance Registry, the platform automatically maintains metadata compliance for supported resources as they are created.