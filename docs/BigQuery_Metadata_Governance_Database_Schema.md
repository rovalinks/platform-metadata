# BigQuery Database Schema - Metadata Governance Platform

## Executive Summary

The **metadata_governance** BigQuery dataset is the analytical backbone
of the Metadata Governance Platform. It centralizes operational
telemetry, compliance evaluation, remediation planning, and remediation
execution history for enterprise Google Cloud environments. It enables
governance reporting, FinOps visibility, compliance auditing, and
operational analytics across the complete lifecycle of every managed
cloud resource.

## Database Schema Overview

### Dataset: `metadata_governance`

The dataset is the platform's reporting repository. It stores discovery
results, compliance assessments, remediation plans, and execution
history for dashboards, APIs, audit reporting, and trend analysis.

### Table: `resource_snapshot`

**Purpose:** Stores the inventory discovered during each governance
run. - Records discovered resources - Captures labels and tags -
Represents the baseline state - Logical key: `run_id`, `project_id`,
`resource_name`

### Table: `compliance_snapshot`

**Purpose:** Stores compliance evaluation results. - Indicates whether
resources comply with metadata policies - Records missing and incorrect
labels - Generated from `resource_snapshot`

### Table: `remediation_plan`

**Purpose:** Stores planned remediation before execution. - Planned
labels - Planned tags - Missing labels - Planning status - Created
timestamp

### Table: `remediation_execution`

**Purpose:** Stores execution history. - Success/failure status - Error
details - API/service invoked - Execution duration - Complete audit
trail

## End-to-End Lifecycle

1.  Discover resources → `resource_snapshot`
2.  Evaluate compliance → `compliance_snapshot`
3.  Generate remediation → `remediation_plan`
4.  Execute remediation → `remediation_execution`

## Mermaid ERD

``` mermaid
erDiagram

RESOURCE_SNAPSHOT {
STRING run_id
TIMESTAMP snapshot_time
STRING project_id
STRING asset_type
STRING resource_name
STRING location
STRING labels
STRING tags
}

COMPLIANCE_SNAPSHOT {
STRING run_id
TIMESTAMP evaluated_time
STRING project_id
STRING asset_type
STRING resource_name
BOOL compliant
STRING missing_labels
STRING incorrect_labels
}

REMEDIATION_PLAN {
STRING run_id
STRING project_id
STRING asset_type
STRING resource_name
JSON missing_labels
JSON planned_labels
STRING planned_tags
STRING status
TIMESTAMP created_at
}

REMEDIATION_EXECUTION {
STRING execution_id
STRING run_id
STRING project_id
STRING asset_type
STRING resource_name
STRING managed_labels
STRING status
STRING error_message
TIMESTAMP executed_at
STRING execution_mode
STRING service_name
STRING method_name
INT duration_ms
}

RESOURCE_SNAPSHOT ||--o{ COMPLIANCE_SNAPSHOT : evaluates
COMPLIANCE_SNAPSHOT ||--o{ REMEDIATION_PLAN : generates
REMEDIATION_PLAN ||--o{ REMEDIATION_EXECUTION : executes
RESOURCE_SNAPSHOT ||--o{ REMEDIATION_EXECUTION : tracked_by
```

## Relationship Summary

  Shared Key      Purpose
  --------------- --------------------------------------------------
  run_id          Correlates records belonging to a governance run
  project_id      Enables project-level reporting
  resource_name   Tracks the same resource across the lifecycle
  asset_type      Supports resource-type analytics
