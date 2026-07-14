# Enterprise Metadata Governance Platform Architecture

# Purpose

This document describes the architecture of the Enterprise Metadata Governance Platform, including its core services, processing flows, governance model, and Google Cloud integration.

The platform is designed to provide automated metadata governance for Google Cloud resources at enterprise scale.

---

# Architecture Principles

The platform is designed around the following principles:

- Cloud-native architecture
- Infrastructure as Code
- Event-driven processing
- Stateless services
- Modular adapters
- Enterprise scalability
- Policy-driven governance
- No resource-specific hardcoding
- Centralized governance registry
- Organization-wide visibility

---

# High-Level Architecture

The platform consists of four major domains:

- Governance Registry
- Brownfield Governance
- Greenfield Governance
- Reporting & Dashboard

Each domain is independently scalable while sharing common governance services.

---

# Core Components

## Governance Registry

The Governance Registry acts as the single source of truth for metadata.

Each application defines:

- Product
- Team
- Owner
- Budget Owner
- Organization
- Department
- Cost Center
- Environment
- Business Criticality

During compliance evaluation the registry determines the expected metadata for each project.

---

## Brownfield Governance

Brownfield governance evaluates existing cloud resources.

Processing pipeline:

1. Resource Discovery
2. Compliance Evaluation
3. Remediation Planning
4. Execution
5. Reporting

Brownfield processing is executed on demand and is designed to support large enterprise estates.

---

## Greenfield Governance

Greenfield governance automatically evaluates newly created resources.

Processing pipeline:

Cloud Audit Logs

↓

Logging Sink

↓

Pub/Sub

↓

Cloud Run

↓

Classification

↓

Compliance Evaluation

↓

Automatic Remediation

↓

Reporting

Only supported resource creation events are processed.

---

# Discovery Layer

Discovery is responsible for collecting supported resources.

Responsibilities:

- Enumerate supported services
- Normalize resources
- Capture labels
- Capture Resource Manager Tags
- Produce a unified resource model

The discovery layer is independent of remediation.

---

# Classification Layer

Incoming Audit Log events are classified into supported resource types.

Responsibilities:

- Parse Audit Logs
- Identify resource type
- Resolve resource name
- Select correct adapter

Unsupported events are ignored.

---

# Compliance Engine

The Compliance Engine compares discovered metadata against the Governance Registry.

Responsibilities:

- Evaluate labels
- Evaluate Resource Manager Tags
- Detect missing metadata
- Detect incorrect metadata
- Produce compliance results

No metadata changes occur during evaluation.

---

# Governance Engine

The Governance Engine generates the desired governance state.

Responsibilities:

- Load registry
- Resolve application
- Produce expected labels
- Produce expected tags

This component contains no Google Cloud API logic.

---

# Adapter Layer

Each supported resource has an adapter.

Examples:

- Compute
- Storage
- BigQuery
- Pub/Sub
- Cloud SQL
- Artifact Registry
- Secret Manager
- Cloud KMS

Responsibilities:

- Read metadata
- Update metadata
- Normalize API differences

This allows new resource types to be added without changing governance logic.

---

# Remediation Engine

The Remediation Engine applies governance changes.

Responsibilities:

- Apply labels
- Apply Resource Manager Tags
- Preserve customer-managed metadata
- Update execution status

Execution is fully auditable.

---

# Reporting Layer

Reporting reads immutable BigQuery data.

Provides:

- Executive summary
- Compliance reporting
- Resource inventory
- Brownfield statistics
- Greenfield statistics
- Remediation history

No reporting component modifies governance data.

---

# Executive Dashboard

The Executive Dashboard provides two reporting scopes.

## Organization

Provides:

- Enterprise compliance
- Cross-project reporting
- Executive KPIs

## Project

Provides:

- Project compliance
- Resource compliance
- Resource inventory
- Execution history

---

# BigQuery Data Model

Primary reporting tables:

- resource_snapshot
- compliance_snapshot
- remediation_plan
- remediation_execution

These tables provide a complete audit history for governance activities.

---

# Scalability

The platform is designed for enterprise environments supporting:

- Multiple organizations
- Multiple projects
- Tens of thousands of resources
- Parallel discovery
- Parallel remediation
- Event-driven governance
- Stateless Cloud Run services

---

# Security

The platform follows Google Cloud IAM best practices.

Key principles:

- Least privilege
- Service accounts
- Workload Identity
- No embedded credentials
- Audit logging enabled

---

# Extensibility

New Google Cloud services can be added by implementing:

- Discovery adapter
- Resource adapter
- Optional classifier
- Capability definition

No changes are required to the governance engine.

---

# Technology Stack

Infrastructure

- Terraform

Compute

- Cloud Run

Messaging

- Pub/Sub

Events

- Eventarc

Logging

- Cloud Logging

Data

- BigQuery

Programming Language

- Python

Framework

- Flask

---

# Summary

The Enterprise Metadata Governance Platform provides a modular, cloud-native architecture for enforcing metadata governance across Google Cloud environments.

The separation between discovery, compliance, governance, remediation, and reporting enables the platform to scale while remaining extensible for future Google Cloud services.