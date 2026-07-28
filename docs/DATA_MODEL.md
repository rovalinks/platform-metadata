# Enterprise Metadata Governance Platform - Data Model

## 1. Purpose

This document defines the operational data model used by the Enterprise Metadata Governance Platform on Google Cloud.

BigQuery provides the durable governance evidence layer for:

- Brownfield discovery
- compliance evaluation
- remediation planning
- remediation execution
- Greenfield execution evidence
- dashboard reporting
- operational audit and troubleshooting

The platform uses dedicated governance projects:

```text
DEV  -> platform-metadata-dev
PROD -> platform-metadata-prod
```

DEV and PROD must maintain separate operational datasets and must not mix governance evidence.

---

## 2. Data Model Principles

The data model follows these principles:

```text
Operational evidence, not static repository snapshots
Run-correlated
Append-oriented where appropriate
Brownfield and Greenfield distinguishable
Project/application aware
Resource-type aware
Auditable
Dashboard consumable
Environment isolated
No hardcoded workload-project assumptions
```

BigQuery records what the platform observed and executed.

The Application Registry remains the source of desired application metadata.

---

## 3. Core Tables

The core governance model consists of:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

Their logical relationship is:

```text
                    run_id
                      |
        +-------------+-------------+
        |             |             |
        v             v             v
resource_snapshot -> compliance_snapshot
                          |
                          v
                    remediation_plan
                          |
                          v
                 remediation_execution
```

Not every row must have a corresponding row in every downstream table.

For example, a compliant resource does not require a remediation plan.

---

## 4. Table Responsibilities

| Table | Responsibility |
| --- | --- |
| `resource_snapshot` | What resources were discovered |
| `compliance_snapshot` | Whether discovered/evaluated resources met required metadata |
| `remediation_plan` | What metadata changes were planned |
| `remediation_execution` | What remediation was actually attempted and its outcome |

This separation is important for auditability.

---

## 5. Brownfield Data Flow

```text
Cloud Asset Inventory
        |
        v
resource_snapshot
        |
        v
Compliance Engine
        |
        v
compliance_snapshot
        |
        v
Remediation Planner
        |
        v
remediation_plan
        |
        v
Cloud Tasks / Worker
        |
        v
remediation_execution
```

Brownfield runs can therefore be reconstructed from discovery through execution.

---

## 6. Greenfield Data Flow

Greenfield does not require a full organisation discovery snapshot for every event.

Its operational flow is:

```text
Audit Event
    |
    v
Classifier
    |
    v
Registry / Compliance
    |
    v
Resource Adapter
    |
    v
remediation_execution
```

Where the implementation records additional Greenfield evaluation evidence, it should use the same canonical project/resource identifiers.

Greenfield execution is distinguished using:

```text
execution_mode = GREENFIELD
```

---

## 7. Run Identifier

Brownfield processing uses:

```text
run_id
```

as the primary correlation identifier.

A run ID should identify one logical governance execution.

It allows operators to correlate:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
Cloud Run logs
Cloud Tasks processing
dashboard run status
```

Run IDs should be generated rather than manually reused.

---

## 8. `resource_snapshot`

### Purpose

`resource_snapshot` records the resources observed during Brownfield discovery.

It represents the discovery state for a particular run.

Typical fields include:

```text
run_id
snapshot_time
project_id
asset_type
resource_name
location
labels
tags
```

The deployed schema remains authoritative.

---

## 9. `resource_snapshot.run_id`

Associates the discovered resource with the Brownfield run.

This field enables queries such as:

```text
How many resources were discovered in this run?
```

and:

```text
Which resource types were present in this run?
```

---

## 10. `resource_snapshot.snapshot_time`

Represents when the discovery snapshot was recorded.

This is not necessarily the resource creation time.

Do not interpret it as:

```text
resource created at
```

unless the source explicitly provides that separate information.

---

## 11. `resource_snapshot.project_id`

Identifies the workload project containing or owning the resource.

This field is central to Application Registry resolution.

The dashboard should not infer project ID from resource-name strings if a canonical project field exists.

---

## 12. `resource_snapshot.asset_type`

Stores the canonical/Cloud Asset Inventory resource type used by the platform.

Examples conceptually resemble:

```text
compute.googleapis.com/Instance
storage.googleapis.com/Bucket
bigquery.googleapis.com/Dataset
```

Exact values must match the application's supported-resource mapping.

---

## 13. `resource_snapshot.resource_name`

Stores the canonical resource identifier available to the platform.

This should be sufficiently precise to distinguish resources across projects and locations.

Resource adapters may derive service-specific identifiers from this field plus project/location metadata.

---

## 14. `resource_snapshot.location`

Stores resource location where relevant.

Depending on the service, a resource may be:

```text
global
regional
zonal
multi-regional
```

Do not assume every resource has a zone.

---

## 15. `resource_snapshot.labels`

Stores labels observed during discovery where available.

The exact BigQuery type may be:

- JSON
- RECORD
- serialised structure

depending on the deployed schema.

Code and SQL must follow the actual table definition rather than assume a representation.

---

## 16. `resource_snapshot.tags`

Where present, this stores tag-related discovery information.

Labels and Resource Manager tags are different Google Cloud metadata systems.

They must not be treated as interchangeable merely because both can represent governance metadata.

---

## 17. `compliance_snapshot`

### Purpose

`compliance_snapshot` records the result of comparing actual resource metadata with required registry-driven metadata.

Typical fields include:

```text
run_id
evaluated_time
project_id
asset_type
resource_name
compliant
missing_labels
incorrect_labels
```

The deployed schema remains authoritative.

---

## 18. Compliance State

The key question represented by this table is:

```text
At evaluation time, did the resource satisfy the managed metadata standard?
```

A resource can be non-compliant because:

- required managed label is missing
- managed label has the wrong value
- another supported metadata requirement is unmet

Unrelated user/application labels should not make a resource non-compliant unless policy explicitly governs them.

---

## 19. `compliant`

The compliance indicator should represent the evaluated result.

Conceptually:

```text
true  -> required managed metadata satisfied
false -> one or more managed requirements not satisfied
```

Unsupported resources and unbound projects should not be misleadingly represented as ordinary compliant resources.

Their handling should follow the implementation's explicit status/evidence model.

---

## 20. `missing_labels`

Records required managed labels that were absent during evaluation.

This field supports:

- remediation planning
- dashboard explanation
- audit evidence

It should contain only managed governance keys relevant to the evaluation.

---

## 21. `incorrect_labels`

Records managed labels that existed but contained values different from the required registry state.

This distinguishes:

```text
missing metadata
```

from:

```text
incorrect metadata
```

which is useful for governance reporting.

---

## 22. `remediation_plan`

### Purpose

`remediation_plan` records intended metadata changes before asynchronous execution.

Typical fields include:

```text
run_id
project_id
asset_type
resource_name
missing_labels
planned_labels
planned_tags
status
created_at
```

The deployed schema remains authoritative.

---

## 23. Why Planning Is Separate from Execution

Planning answers:

```text
What should the platform change?
```

Execution answers:

```text
What did the platform actually attempt and what happened?
```

These must not be collapsed into one status.

A planned action may:

- execute successfully
- fail
- remain queued
- become unnecessary because the resource changed
- be skipped due to later validation

---

## 24. `planned_labels`

Stores the managed label state intended for remediation.

This should represent governance-controlled metadata, not an instruction to delete every other existing resource label.

The adapter determines the safe final mutation using current resource state.

---

## 25. `planned_tags`

Where the platform supports Resource Manager tag planning, this field represents planned tag changes.

Tag support must remain capability-controlled.

Do not populate tag plans for services/resources that have not been validated for the platform's tag model.

---

## 26. Plan Status

Plan status should make it possible to determine whether an action is:

```text
planned
queued
processing
completed
failed
skipped
```

The exact status values are implementation-defined.

Dashboard logic must use actual deployed values rather than invent additional status strings client-side.

---

## 27. `remediation_execution`

### Purpose

`remediation_execution` is the primary evidence table for actual remediation attempts.

Typical fields include:

```text
execution_id
run_id
project_id
asset_type
resource_name
managed_labels
status
error_message
executed_at
execution_mode
service_name
method_name
duration_ms
```

The deployed schema remains authoritative.

---

## 28. `execution_id`

Uniquely identifies an execution record.

This is separate from `run_id`.

One Brownfield run can produce many execution records.

Greenfield events can also create independent execution records.

---

## 29. `execution_mode`

Distinguishes the governance path.

Expected logical values include:

```text
BROWNFIELD
GREENFIELD
```

This field is important for:

- dashboard segmentation
- operational analysis
- failure analysis
- throughput reporting
- client evidence

Do not infer execution mode from timestamps or resource names.

---

## 30. `managed_labels`

Records the governance metadata associated with the execution.

This should represent managed metadata relevant to the remediation.

It must not be treated as proof that unrelated pre-existing labels were absent.

---

## 31. `status`

Records the outcome of the remediation attempt.

The exact allowed values are implementation-defined.

Typical logical outcomes include:

```text
SUCCESS
FAILED
SKIPPED
NO_CHANGE
```

Only use values supported by the deployed application/schema.

---

## 32. `error_message`

Contains diagnostic information for failed execution where available.

Error content should be useful enough to identify:

- IAM denial
- resource lookup problem
- API failure
- unsupported behaviour
- update conflict

Do not persist secrets, tokens or confidential payload data in error messages.

---

## 33. `executed_at`

Records when the remediation attempt occurred.

This enables:

- recent activity
- daily/weekly reporting
- execution timelines
- operational troubleshooting

All time comparisons should use a consistent timezone strategy, preferably UTC at storage level.

---

## 34. `service_name`

For Greenfield, this can preserve the source Audit Log service context.

For example, it can help answer:

```text
Which Google Cloud service generated the event that led to remediation?
```

For Brownfield, this field may be populated according to implementation requirements.

Do not fabricate a service name when the processing path does not supply one.

---

## 35. `method_name`

For Greenfield, this can preserve the validated Audit Log method that caused event classification.

This is useful for:

- validating Greenfield routing
- troubleshooting event filters
- identifying unexpected methods

The value should come from the observed event.

---

## 36. `duration_ms`

Records execution duration where implemented.

This supports:

- performance analysis
- adapter comparison
- scale planning
- Cloud Run tuning

Duration alone must not be interpreted as total end-to-end Greenfield latency unless the measurement explicitly covers the entire event path.

---

## 37. Logical Table Relationships

A Brownfield resource can follow:

```text
resource_snapshot
       |
       | run_id + project_id + asset_type + resource_name
       v
compliance_snapshot
       |
       | non-compliant
       v
remediation_plan
       |
       | queued/executed
       v
remediation_execution
```

The combination used for joins must match the deployed schema and canonical resource identity.

Avoid joining only on `resource_name` if names can collide across projects or locations.

---

## 38. Greenfield Correlation

Greenfield does not necessarily originate from a Brownfield `run_id`.

Where the application creates a correlation/run identifier for Greenfield, it should remain unique and traceable.

Useful correlation context includes:

```text
execution_id
run_id/correlation_id where implemented
project_id
asset_type
resource_name
service_name
method_name
executed_at
```

---

## 39. Application Registry Relationship

The Application Registry is not replaced by BigQuery.

```text
Application Registry
      |
      | desired state
      v
Governance Engine
      |
      | observed/evaluated/executed state
      v
BigQuery
```

BigQuery may contain project/application information for reporting, but the registry remains authoritative for current required ownership metadata.

---

## 40. Application Dimension

For dashboard efficiency, reporting can associate operational rows with application information.

This can be performed through:

- backend registry enrichment
- controlled denormalisation
- a reporting view
- another approved data model

Do not create a second independently maintained application ownership source that can drift from the registry.

---

## 41. Dashboard Data Sources

The dashboard should use BigQuery operational evidence.

Examples:

```text
Executive Summary
    -> compliance_snapshot + remediation_execution

Brownfield Run Status
    -> all four core tables

Recent Activity
    -> remediation_execution

Resource Distribution
    -> resource_snapshot

Compliance by Resource Type
    -> compliance_snapshot

Remediation Failures
    -> remediation_execution

Greenfield Activity
    -> remediation_execution
       WHERE execution_mode = 'GREENFIELD'
```

Exact queries must match the deployed schema.

---

## 42. Repository Snapshot vs Operational Data

Repository/configuration files can describe:

- supported resources
- capability flags
- platform configuration

They must not be used as the source of live values such as:

```text
current resource count
current compliance percentage
current remediation success count
recent Greenfield activity
```

Those values must come from operational evidence.

---

## 43. Executive Summary

A correct executive summary should derive metrics dynamically.

Conceptually:

```text
Total resources
Evaluated resources
Compliant resources
Non-compliant resources
Planned remediation
Successful remediation
Faile