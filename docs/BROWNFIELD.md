# Enterprise Metadata Governance Platform - Brownfield Governance

## 1. Purpose

This document defines the Brownfield governance architecture and operational model for the Enterprise Metadata Governance Platform on Google Cloud.

Brownfield governance is responsible for discovering existing GCP resources across the authorised estate, resolving application ownership and required metadata, evaluating compliance, generating remediation plans and applying approved metadata changes through a controlled asynchronous execution model.

The design is:

- organisation-aware
- centralised
- registry-driven
- capability-controlled
- asynchronous
- serverless
- auditable
- designed for enterprise-scale estates

Development and validation are performed through:

```text
platform-metadata-dev
```

Production organisation-wide governance is performed through:

```text
platform-metadata-prod
```

---

## 2. Brownfield Objective

Brownfield governance addresses resources that already exist before the metadata governance platform processes them.

Typical Brownfield conditions include:

- resources with no governance labels
- resources with partially populated labels
- resources with incorrect managed label values
- resources created before the governance standard existed
- resources belonging to applications that have subsequently been registered
- resources requiring metadata reconciliation after registry changes

Brownfield governance is not based on waiting for creation events.

Instead, the platform actively discovers the existing estate.

---

## 3. High-Level Brownfield Architecture

```text
                           GCP ORGANISATION
                                  |
                                  v
                     Governed Workload Projects
                                  |
                                  v
                      Cloud Asset Inventory
                                  |
                                  v
                         Discovery Engine
                                  |
                                  v
                     Resource Metadata Enrichment
                                  |
                                  v
                       Application Registry
                                  |
                                  v
                        Capability Validation
                                  |
                                  v
                       Compliance Evaluation
                                  |
                    +-------------+-------------+
                    |                           |
                    v                           v
                Compliant                 Non-Compliant
                    |                           |
                    v                           v
             Record Evidence             Remediation Plan
                                                |
                                                v
                                           Cloud Tasks
                                                |
                                                v
                                         Cloud Run /worker
                                                |
                                                v
                                        Resource Adapter
                                                |
                                                v
                                         Native GCP API
                                                |
                                                v
                                      BigQuery Execution
```

---

## 4. Brownfield and Greenfield Relationship

Brownfield and Greenfield use different ingestion paths but share the same governance model.

```text
Brownfield
Cloud Asset Inventory
        |
        +------------------+
                           |
                           v
                    Shared Governance
                           |
Greenfield                 |
Audit Event ---------------+
                           |
                           v
                 Application Registry
                           |
                           v
                    Capability Gate
                           |
                           v
                      Compliance
                           |
                           v
                  Resource Adapters
                           |
                           v
                  BigQuery Evidence
```

The metadata standard must not differ depending on whether a resource was discovered through Brownfield or Greenfield processing.

---

## 5. Organisation and Project Scope

Brownfield processing can operate against:

- a controlled individual project
- a selected set of projects
- the authorised organisation scope

Organisation-scale processing should obtain the target project estate dynamically through authorised project/resource discovery.

The platform must not rely on a hardcoded list of every client project in application code.

---

## 6. Governance Project Exclusion

The dedicated governance control-plane projects contain platform infrastructure and must be protected from unintended remediation where appropriate.

Examples include:

```text
platform-metadata-dev
platform-metadata-prod
```

Platform-specific resources such as the Application Registry bucket may also require explicit exclusion.

Exclusions must be configuration-driven.

Do not scatter fixed project names or bucket names through service adapters.

---

## 7. Brownfield Run

A Brownfield execution is treated as a governance run.

Each run should have a unique:

```text
run_id
```

The same run identifier is used to correlate:

- discovery
- resource snapshots
- compliance results
- remediation plans
- execution results
- dashboard/reporting

This provides traceability from estate discovery through final remediation.

---

## 8. Brownfield Processing Flow

The logical processing sequence is:

```text
Start Brownfield Run
        |
        v
Resolve Scope
        |
        v
Discover Resources
        |
        v
Persist Resource Snapshot
        |
        v
Resolve Application Registry
        |
        v
Capability Check
        |
        v
Read/Enrich Live Metadata
        |
        v
Evaluate Compliance
        |
        v
Persist Compliance Snapshot
        |
        +---------------------+
        |                     |
     Compliant           Non-Compliant
        |                     |
        v                     v
      Finish           Create Remediation Plan
                              |
                              v
                       Persist Plan Records
                              |
                              v
                         Create Batches
                              |
                              v
                          Cloud Tasks
                              |
                              v
                       Cloud Run /worker
                              |
                              v
                        Resource Adapter
                              |
                              v
                       Native GCP Update
                              |
                              v
                    Remediation Execution
```

---

## 9. Cloud Asset Inventory Discovery

Cloud Asset Inventory is the primary Brownfield discovery mechanism.

It provides a scalable inventory layer for resources visible to the governance runtime.

The discovery layer should identify information such as:

- project
- asset type
- resource name
- location
- available metadata
- resource ancestry/context where required

Cloud Asset Inventory is used for discovery, not as the universal mutation interface.

Actual metadata remediation is performed through the relevant service API.

---

## 10. Discovery Scope

The platform should determine discovery scope dynamically from the requested execution mode and authorised project estate.

Possible scope patterns include:

```text
Single project
Selected projects
Organisation scope
```

A controlled single-project run is the preferred initial validation method before large-scale organisation remediation.

---

## 11. Resource Snapshot

Discovered inventory is persisted in BigQuery.

The core table is:

```text
resource_snapshot
```

Important fields include:

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

The snapshot provides evidence of what the platform discovered during a specific run.

It also separates discovery evidence from later compliance and remediation results.

---

## 12. Live Metadata Enrichment

Cloud Asset Inventory may not always contain every service-specific value required for safe mutation.

Where necessary, the resource client retrieves the current resource directly from its native Google Cloud API.

This can provide values such as:

- current labels
- fingerprints
- ETags
- versions
- location details
- service-specific resource identifiers

Discovery and live enrichment therefore have separate responsibilities.

```text
Cloud Asset Inventory
    -> scalable discovery

Native service API
    -> current mutation-safe resource state
```

---

## 13. Application Registry Resolution

The platform resolves each workload project against the Application Registry.

The registry supplies required governance metadata without embedding application values in Brownfield code.

Typical governance values include:

- application/product
- team
- owner
- budget owner
- organisation
- department
- cost centre
- environment
- region
- business criticality

If a project has no valid registry binding, the platform must follow the defined unbound-project behaviour rather than inventing values.

---

## 14. Capability Gate

A discovered resource is not automatically eligible for remediation.

The platform first checks the supported-resource capability configuration.

This distinction is fundamental:

```text
Discovered resource
      !=
Supported resource
      !=
Remediation-enabled resource
```

The capability layer protects the platform from attempting updates against resources whose metadata semantics, IAM or adapter behaviour have not been validated.

---

## 15. Unsupported Resources

Unsupported asset types should be handled safely.

The platform should:

- identify them as unsupported
- avoid mutation
- retain sufficient operational evidence where required
- continue processing unrelated resources

One unsupported resource must not terminate an entire enterprise Brownfield run.

---

## 16. Compliance Evaluation

For supported resources, the platform compares actual metadata with required registry-derived metadata.

Conceptually:

```text
Required metadata
        +
Current resource metadata
        |
        v
Compliance Engine
        |
        +-- compliant
        |
        +-- missing managed metadata
        |
        +-- incorrect managed metadata
```

The platform should only plan changes required to reconcile managed governance metadata.

---

## 17. Compliance Snapshot

Compliance results are persisted in:

```text
compliance_snapshot
```

Important fields include:

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

This provides a point-in-time compliance record independently of whether remediation subsequently succeeds.

---

## 18. Already Compliant Resources

Resources already matching the required governance metadata should not generate unnecessary mutation requests.

This reduces:

- API calls
- runtime work
- risk
- audit noise
- remediation volume

The platform should record the compliance result and continue.

---

## 19. Remediation Planning

Non-compliant resources that are eligible for remediation are converted into remediation plans.

The plan separates:

```text
What should change?
```

from:

```text
Has the change actually been executed?
```

This is important for enterprise auditability.

---

## 20. Remediation Plan Table

Planned actions are persisted in:

```text
remediation_plan
```

Important fields include:

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

The plan provides an auditable record of intended changes before worker execution.

---

## 21. Asynchronous Remediation

Large Brownfield runs must not attempt to synchronously mutate an entire enterprise estate within the original HTTP request.

The platform uses Cloud Tasks to decouple orchestration from execution.

```text
Brownfield Orchestrator
       |
       | create batches
       v
Cloud Tasks
       |
       | authenticated requests
       v
Cloud Run /worker
```

This improves scalability and failure isolation.

---

## 22. Remediation Batch Size

The current application default is:

```text
REMEDIATION_BATCH_SIZE = 500
```

This means the platform groups remediation actions into batches rather than creating one Cloud Task for every resource.

For example:

```text
1,000,000 planned remediation actions
÷ 500 actions per batch
≈ 2,000 task batches
```

before retries or ancillary operations.

The exact batch size remains runtime configuration and must not be hardcoded into architecture assumptions outside the configured default.

---

## 23. Parallel Processing

The application includes a configurable parallelism control:

```text
MAX_PARALLEL_WORKERS
```

Parallelism should be tuned against:

- Cloud Run capacity
- service API quotas
- resource API latency
- Cloud Tasks delivery rate
- error rate
- target estate size

Increasing parallelism is not automatically better.

Production tuning must use measured behaviour from representative DEV testing.

---

## 24. Cloud Tasks Queue

The deployed remediation queue is:

```text
metadata-remediation
```

Cloud Tasks provides:

- asynchronous delivery
- retry support
- controlled execution
- decoupling from the original orchestration request

The queue must exist in the correct environment and region before Brownfield remediation can execute.

---

## 25. Worker Authentication

Cloud Tasks invokes the worker using authenticated service-to-service access.

The worker endpoint is:

```text
/worker
```

The task's OIDC identity must have permission to invoke the Cloud Run service.

Anonymous worker access must not be required.

---

## 26. Worker Responsibilities

The worker processes a remediation batch.

Its responsibilities include:

```text
Receive batch
    |
    v
Validate payload
    |
    v
Iterate remediation actions
    |
    v
Dispatch by asset type
    |
    v
Read current state where required
    |
    v
Apply managed metadata
    |
    v
Capture success/failure
    |
    v
Persist execution evidence
```

A failure affecting one resource should not unnecessarily prevent unrelated resources in the batch from being processed.

---

## 27. Resource Adapters

Resource adapters isolate Google Cloud service-specific behaviour.

Different services may require:

- `setLabels`
- update operations
- update masks
- fingerprints
- ETags
- regional endpoints
- zonal endpoints
- long-running operation polling

The Brownfield orchestrator and compliance engine should not implement these service-specific details directly.

---

## 28. Metadata Preservation

Where policy requires it, existing unrelated labels must be preserved.

The application configuration includes:

```text
PRESERVE_EXISTING_LABELS
```

The intended reconciliation pattern is:

```text
Existing labels
      +
Required managed labels
      |
      v
Safe merged target state
```

rather than replacing all labels indiscriminately.

This behaviour must be validated per service adapter.

---

## 29. Dry-Run Control

The application supports:

```text
DRY_RUN
```

Dry-run mode is useful during:

- initial client onboarding
- new capability validation
- production change review
- large-scope preflight testing

Dry-run behaviour should permit discovery/compliance/planning visibility without applying actual metadata mutations, according to the implementation.

The exact expected output must be validated in DEV before relying on it operationally.

---

## 30. IAM Model

Brownfield requires two broad IAM categories.

### Discovery

Organisation-level read visibility for:

- projects
- Cloud Asset Inventory
- resource metadata required for evaluation

### Remediation

Service-specific read/update permissions for enabled resource capabilities.

The production custom remediation role must contain only the permissions required by active, tested capabilities.

Do not use Owner or Editor as a shortcut.

See `IAM.md` for the detailed model.

---

## 31. BigQuery Execution Evidence

Completed remediation attempts are persisted in:

```text
remediation_execution
```

Important fields include:

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

Brownfield execution should be distinguishable through:

```text
execution_mode = BROWNFIELD
```

where the implementation writes execution mode.

---

## 32. Brownfield Dashboard Reporting

The dashboard should use operational BigQuery data for Brownfield status.

Useful metrics include:

- resources discovered
- resources evaluated
- supported resources
- compliant resources
- non-compliant resources
- remediation actions planned
- remediation actions completed
- remediation failures
- remaining remediation
- project compliance
- resource-type compliance
- recent runs

The dashboard must not use repository snapshots as a substitute for live operational execution data.

---

## 33. Failure Isolation

Enterprise Brownfield processing must tolerate individual resource failures.

A resource can fail because of:

- IAM denial
- API quota/rate limiting
- transient API error
- invalid resource state
- unsupported metadata behaviour
- resource deleted between discovery and execution
- fingerprint/ETag conflict
- registry problem
- adapter defect

The platform should capture the failure and continue processing unrelated resources wherever safe.

---

## 34. Retry Behaviour

Retries should target transient failures.

Examples may include:

- temporary resource lookup failure
- retryable API response
- temporary service availability problem

Retries must be bounded.

Permanent failures such as missing IAM should not create uncontrolled retry loops.

Cloud Tasks retry behaviour and application-level retry behaviour should be reviewed together to avoid retry amplification.

---

## 35. Resource Changes During a Run

Brownfield is operating against a live cloud estate.

Between discovery and worker execution:

- a resource may be deleted
- labels may be changed manually
- registry values may change
- a resource may become compliant
- fingerprints/ETags may change

Adapters should therefore obtain current state where required immediately before mutation.

The platform must not assume the discovery snapshot is always mutation-safe current state.

---

## 36. Idempotency

Brownfield remediation should be safe to retry.

The desired model is:

```text
Read current metadata
      |
      v
Compare managed metadata
      |
      +-- already correct -> no unnecessary mutation
      |
      +-- change required -> reconcile managed metadata
```

Repeated processing should converge on the same required metadata state.

---

## 37. Exclusions

The platform supports configuration-driven exclusions.

Relevant controls include:

```text
EXCLUDED_PROJECTS
EXCLUDED_BUCKETS
```

These controls are especially important for protecting:

- governance projects
- registry buckets
- platform-owned resources
- explicitly exempted workload resources

Exclusion logic should be centralised and testable.

---

## 38. Application Registry Changes

A registry change can alter the required metadata for resources already present in the estate.

Brownfield provides the mechanism to reconcile those existing resources during a subsequent run.

Therefore, registry promotion and Brownfield execution should be operationally coordinated.

A large registry change should be reviewed for expected remediation impact before organisation-wide execution.

---

## 39. Single-Project Validation

Before organisation-wide execution, validate a representative project.

Recommended sequence:

```text
1. Select registered DEV workload project
2. Confirm exclusions
3. Confirm supported resource types
4. Run discovery
5. Review resource_snapshot
6. Review compliance_snapshot
7. Review remediation_plan
8. Use dry-run where appropriate
9. Execute limited remediation
10. Verify target labels
11. Verify remediation_execution
12. Verify dashboard
```

This should be repeated when onboarding materially different resource families.

---

## 40. Organisation-Scale Execution

After controlled validation, the platform can process the authorised organisation scope.

Before doing so, confirm:

```text
[ ] Project discovery is correct
[ ] Governance projects are excluded where required
[ ] Registry bindings are valid
[ ] Unsupported resource types are gated
[ ] IAM is approved
[ ] API quotas are understood
[ ] Batch size is validated
[ ] Parallelism is validated
[ ] Cloud Tasks queue is healthy
[ ] BigQuery writes are healthy
[ ] Failure monitoring exists
[ ] Rollback/recovery process is documented
```

---

## 41. Brownfield Operational States

A run should expose enough state to determine where work currently stands.

Useful conceptual states include:

```text
DISCOVERY
EVALUATION
PLANNING
QUEUED
REMEDIATING
COMPLETED
PARTIALLY_COMPLETED
FAILED
```

The exact implementation status values may differ.

Operational reporting must distinguish orchestration completion from successful completion of all asynchronous worker batches.

---

## 42. Important Asynchronous Behaviour

A Brownfield orchestration request can successfully finish creating Cloud Tasks while worker execution is still in progress.

Therefore:

```text
Orchestrator completed
```

does not necessarily mean:

```text
All resource remediation completed
```

The authoritative completion view must include worker/execution evidence.

This distinction is important for dashboard status and client operational reporting.

---

## 43. Brownfield Run Validation Queries

Operational validation should check all four stages of evidence:

```text
resource_snapshot
        |
        v
compliance_snapshot
        |
        v
remediation_plan
        |
        v
remediation_execution
```

For a given `run_id`, operators should be able to determine:

- how many resources were discovered
- how many were evaluated
- how many were compliant
- how many remediation actions were planned
- how many were executed successfully
- how many failed
- what remains outstanding

---

## 44. Troubleshooting Sequence

When Brownfield does not behave as expected, troubleshoot in processing order.

```text
Scope
  |
  v
Project discovery
  |
  v
Cloud Asset Inventory
  |
  v
resource_snapshot
  |
  v
Registry binding
  |
  v
Capability
  |
  v
Compliance
  |
  v
remediation_plan
  |
  v
Cloud Tasks
  |
  v
/worker
  |
  v
Adapter
  |
  v
Target API
  |
  v
remediation_execution
```

Do not start by changing adapters if no remediation plan was created.

---

## 45. No Resources Discovered

Check:

- requested project/organisation scope
- runtime organisation/project visibility
- Cloud Asset Inventory permissions
- supported asset query/filter
- project status
- exclusions
- discovery logs

---

## 46. Resources Discovered but Not Evaluated

Check:

- registry project binding
- capability configuration
- asset-type mapping
- resource metadata parsing
- live enrichment errors
- compliance engine logs

---

## 47. Plans Created but No Tasks Execute

Check:

- `metadata-remediation` queue exists
- queue region/configuration
- Cloud Tasks enqueue IAM
- task creation logs
- Cloud Run URL configuration
- OIDC service-account configuration
- Cloud Run Invoker permission
- `/worker` logs

---

## 48. Worker Executes but Resource Is Not Updated

Check:

- asset type dispatch
- adapter selection
- current resource lookup
- exact denied IAM permission
- fingerprint/ETag
- update API response
- preserve-existing-label behaviour
- exclusion logic
- operation polling where required

---

## 49. Resource Updated but Dashboard Is Wrong

Check:

- `remediation_execution`
- `execution_mode`
- run correlation
- dashboard API query
- BigQuery query filters
- stale/static repository snapshot logic
- dashboard refresh/caching

The dashboard should reflect operational BigQuery evidence.

---

## 50. Scale and Quota Management

Brownfield processing can generate substantial API activity.

Scale controls include:

```text
REMEDIATION_BATCH_SIZE
MAX_PARALLEL_WORKERS
Cloud Tasks queue behaviour
Cloud Run maximum instances
service-specific API quotas
```

Production tuning should use measured execution characteristics rather than theoretical maximum concurrency.

The platform should optimise for safe sustained throughput, not maximum instantaneous request volume.

---

## 51. Cost Characteristics

Brownfield is consumption-based.

Primary variable-cost components include:

- Cloud Asset Inventory operations where chargeable under the applicable pricing model
- Cloud Run execution
- Cloud Tasks operations
- BigQuery storage and queries
- Cloud Logging
- target service API usage where applicable

Because remediation is batched, task count is not necessarily equal to resource count.

Any client cost estimate must use the deployed batch model and current official Google Cloud pricing rather than assuming one task per resource.

---

## 52. Brownfield Security Controls

Production Brownfield must maintain:

```text
[ ] Dedicated PROD governance project
[ ] Dedicated PROD runtime identity
[ ] Organisation discovery access approved
[ ] Least-privilege remediation custom role
[ ] Authenticated Cloud Tasks worker invocation
[ ] Registry access controlled
[ ] Governance projects/resources excluded where required
[ ] BigQuery evidence protected
[ ] No anonymous worker endpoint
[ ] No broad Owner/Editor shortcut
```

---

## 53. Brownfield Anti-Patterns

Do not:

- hardcode every workload project in application code
- treat every discovered asset as supported
- mutate unsupported resources
- run organisation-wide remediation as the first production test
- create one Cloud Task per resource when the configured architecture uses batches
- assume orchestrator completion means worker completion
- replace unrelated existing labels
- use stale discovery metadata when the service requires current fingerprints/ETags
- grant Owner/Editor to fix adapter permission failures
- silently ignore failed resources
- allow one resource failure to terminate the entire estate run
- use static repository snapshots as live dashboard data
- hardcode governance project exclusions inside every adapter

---

## 54. DEV Acceptance Checklist

```text
[ ] Registered workload project selected
[ ] Project discovery works
[ ] Cloud Asset Inventory returns expected resources
[ ] resource_snapshot populated
[ ] Registry resolves correctly
[ ] Capability filtering correct
[ ] Live enrichment succeeds
[ ] compliance_snapshot populated
[ ] Compliant resources are not unnecessarily changed
[ ] remediation_plan contains expected actions
[ ] Batch creation correct
[ ] Cloud Tasks created
[ ] /worker authentication succeeds
[ ] Correct adapter executes
[ ] Existing unrelated metadata preserved
[ ] Target metadata updated
[ ] remediation_execution populated
[ ] Failed resource does not stop unrelated work
[ ] Dashboard matches BigQuery evidence
```

---

## 55. Production Readiness Checklist

Before organisation-wide production execution:

```text
[ ] platform-metadata-prod infrastructure validated
[ ] PROD registry validated
[ ] PROD runtime identity validated
[ ] Organisation discovery IAM approved
[ ] Custom remediation IAM approved
[ ] Active capability list approved
[ ] Exclusions approved
[ ] Single-project production validation completed
[ ] Dry-run behaviour validated where used
[ ] Batch size validated
[ ] Parallelism validated
[ ] Cloud Tasks retries reviewed
[ ] Cloud Run scaling reviewed
[ ] API quotas reviewed
[ ] BigQuery evidence verified
[ ] Dashboard reporting verified
[ ] Monitoring/alerts available
[ ] Rollback/recovery runbook approved
```

---

## 56. Architecture Summary

Brownfield governance provides controlled remediation of existing Google Cloud resources using a central serverless governance platform.

The core flow is:

```text
Organisation / Project Scope
        |
        v
Cloud Asset Inventory
        |
        v
Resource Snapshot
        |
        v
Application Registry
        |
        v
Capability Gate
        |
        v
Compliance Snapshot
        |
        v
Remediation Plan
        |
        v
Cloud Tasks Batches
        |
        v
Cloud Run Worker
        |
        v
Resource Adapter
        |
        v
Native GCP API
        |
        v
BigQuery Execution Evidence
```

The architecture separates discovery, compliance, planning and execution so that enterprise remediation remains traceable and scalable.

Cloud Tasks and Cloud Run provide asynchronous serverless execution, while capability controls, registry-driven metadata, exclusions and least-privilege IAM prevent the central runtime from treating every discovered resource as an automatic remediation target.

---

## 57. Related Documentation

```text
docs/
├── ARCHITECTURE.md
├── DEPLOYMENT.md
├── IAM.md
├── GREENFIELD.md
├── BROWNFIELD.md
├── APPLICATION_REGISTRY.md
├── SUPPORTED_RESOURCES.md
├── API.md
├── DATA_MODEL.md
├── OPERATIONS.md
├── SECURITY.md
├── TESTING.md
└── PRODUCTION_READINESS.md
```

See:

- `ARCHITECTURE.md` for the overall platform design.
- `GREENFIELD.md` for event-driven governance of newly created resources.
- `IAM.md` for organisation discovery and remediation permissions.
- `APPLICATION_REGISTRY.md` for project-to-application metadata resolution.
- `SUPPORTED_RESOURCES.md` for the authoritative capability matrix.
- `OPERATIONS.md` for production execution, monitoring and troubleshooting.
