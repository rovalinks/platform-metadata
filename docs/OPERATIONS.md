# Enterprise Metadata Governance Platform - Operations

## 1. Purpose

This document defines the operational runbook for the Enterprise Metadata Governance Platform on Google Cloud.

It covers day-to-day operation of:

- Greenfield event-driven governance
- Brownfield discovery and remediation
- Cloud Run
- Cloud Tasks
- Pub/Sub
- Eventarc
- organisation-level Cloud Logging routing
- Cloud Asset Inventory
- Application Registry
- BigQuery operational evidence
- dashboard/reporting
- failures, retries and incident diagnosis

The platform operates through two dedicated governance projects:

```text
DEV  -> platform-metadata-dev
PROD -> platform-metadata-prod
```

Production operations must remain isolated from DEV.

---

## 2. Operational Architecture

```text
                         GCP ORGANISATION
                                |
              +-----------------+-----------------+
              |                                   |
              v                                   v
         GREENFIELD                           BROWNFIELD
              |                                   |
       Cloud Audit Logs                    Cloud Asset Inventory
              |                                   |
       Organisation Sink                          |
              |                                   |
           Pub/Sub                                |
              |                                   |
          Eventarc                                |
              |                                   |
              +----------------+------------------+
                               |
                               v
                  Cloud Run - metadata-governance
                               |
                    +----------+----------+
                    |                     |
                    v                     v
             Application Registry    Compliance Engine
                                          |
                                          v
                                  Remediation Planning
                                          |
                                          v
                                      Cloud Tasks
                                          |
                                          v
                                    Cloud Run /worker
                                          |
                                          v
                                   Resource Adapters
                                          |
                                          v
                                     Native GCP APIs
                                          |
                                          v
                                  BigQuery Evidence
                                          |
                                          v
                                       Dashboard
```

---

## 3. Operational Principles

Production operation follows these principles:

```text
Observe before changing
Validate in DEV first
Use least privilege
Do not hardcode workload projects
Do not bypass capability controls
Do not hide failures
Use BigQuery as operational evidence
Treat Greenfield and Brownfield independently
Protect control-plane resources
Prefer targeted diagnosis over broad changes
```

---

## 4. Daily Platform Health

Operators should confirm the following platform layers are healthy:

```text
[ ] Cloud Run service available
[ ] Correct Cloud Run revision serving
[ ] Application Registry accessible
[ ] BigQuery writes succeeding
[ ] Cloud Tasks queue healthy
[ ] Eventarc trigger healthy
[ ] Pub/Sub topic available
[ ] Organisation Logging sink enabled
[ ] No unusual IAM-denied spike
[ ] No unusual remediation-failure spike
[ ] Dashboard operational data current
```

The exact monitoring frequency should reflect the client's operational requirements.

---

## 5. Cloud Run Operations

Primary service:

```text
metadata-governance
```

Check:

- service status
- active revision
- deployment timestamp
- request count
- error count
- latency
- instance count
- CPU/memory behaviour
- maximum-instance configuration
- environment variables
- runtime service account

Unexpected revision changes should be investigated before governance runs continue.

---

## 6. Cloud Run Logs

Cloud Run logs are the primary runtime troubleshooting source.

Useful structured context includes:

```text
run_id
execution_mode
project_id
asset_type
resource_name
service_name
method_name
status
duration_ms
error
```

When investigating a failure, filter as narrowly as possible by:

```text
run_id
project_id
resource_name
timestamp
```

Avoid troubleshooting large enterprise runs using unfiltered logs.

---

## 7. Application Registry Operations

Before a significant Brownfield run, verify:

```text
[ ] Registry object(s) available
[ ] Registry validation passed
[ ] Expected project bindings exist
[ ] No duplicate bindings
[ ] Correct environment values used
[ ] Runtime can read registry
[ ] Recent registry changes are intentional
```

Remember that runtime instances may cache registry content according to:

```text
REGISTRY_CACHE_TTL
```

---

## 8. Registry Change Operations

For a production registry change:

```text
Source change
    |
    v
Validation
    |
    v
Peer review
    |
    v
DEV publication
    |
    v
DEV governance validation
    |
    v
Impact review
    |
    v
PROD approval
    |
    v
PROD publication
```

A registry ownership change can cause existing resources to become non-compliant during the next Brownfield run.

---

## 9. Greenfield Operations

Greenfield is near-real-time event-driven governance.

Operational path:

```text
Workload resource created
        |
        v
Cloud Audit Log
        |
        v
Organisation Logging sink
        |
        v
metadata-governance-events
        |
        v
Eventarc
        |
        v
metadata-governance Cloud Run
        |
        v
Classifier / Registry / Adapter
        |
        v
remediation_execution
```

The central governance project does not need to contain the workload resource.

---

## 10. Greenfield Health Check

A controlled Greenfield test should periodically validate the full path using an approved DEV or production test project.

Verify:

```text
[ ] Supported resource created
[ ] Audit event generated
[ ] Organisation sink matches
[ ] Pub/Sub receives event
[ ] Eventarc delivers event
[ ] Cloud Run receives request
[ ] Classifier recognises resource
[ ] Registry resolves project
[ ] Capability allows Greenfield
[ ] Adapter succeeds
[ ] Required metadata is present
[ ] BigQuery GREENFIELD evidence exists
```

Do not test only inside the governance control-plane project when validating organisation-level routing.

---

## 11. Greenfield - No Cloud Run Logs

If a resource is created and there are no governance Cloud Run logs, troubleshoot upstream in this exact order:

```text
Resource creation
      |
      v
Audit Log exists?
      |
      v
Organisation sink matches?
      |
      v
Pub/Sub receives message?
      |
      v
Eventarc delivers?
      |
      v
Cloud Run receives?
```

Do not modify adapter code until event delivery reaches Cloud Run.

---

## 12. Step 1 - Verify Audit Event

In the workload project, verify the resource creation produced the expected audit record.

Inspect:

```text
protoPayload.serviceName
protoPayload.methodName
resource/project context
timestamp
```

Use the real observed event as the basis for classification.

Do not guess the Audit Log method from the REST API name.

---

## 13. Step 2 - Verify Organisation Sink

If the audit event exists, verify the organisation-level sink.

Check:

```text
sink enabled
organisation scope correct
filter matches log category
filter matches serviceName
filter matches methodName
destination topic correct
```

A valid Logging sink can still have a filter that excludes the event.

---

## 14. Step 3 - Verify Sink Writer IAM

The Logging sink writer identity requires permission to publish to:

```text
metadata-governance-events
```

Check that the actual sink writer identity has:

```text
roles/pubsub.publisher
```

on the destination topic.

Do not substitute the runtime service account for the Logging sink writer identity.

---

## 15. Step 4 - Verify Pub/Sub

Check:

```text
topic exists
correct environment project
sink destination matches topic
messages are arriving
no unexpected publishing errors
```

The platform topic must not be confused with unrelated workload Pub/Sub topics.

---

## 16. Step 5 - Verify Eventarc

Trigger:

```text
metadata-governance-trigger
```

Expected event type:

```text
google.cloud.pubsub.topic.v1.messagePublished
```

Check:

```text
trigger active
correct source topic
correct destination service
correct region
delivery identity valid
Cloud Run Invoker granted
```

An ACTIVE trigger does not prove messages are reaching the source topic.

---

## 17. Step 6 - Verify Cloud Run Intake

If Eventarc delivers the event, inspect Cloud Run logs.

Check:

```text
CloudEvent accepted
Pub/Sub payload decoded
Audit Log parsed
serviceName extracted
methodName extracted
project resolved
resource resolved
```

If parsing fails, capture the real event structure before changing parser logic.

---

## 18. Step 7 - Verify Classifier and Capability

If the event reaches Cloud Run but no remediation occurs:

```text
event
 |
 v
classifier match?
 |
 v
canonical asset type?
 |
 v
Greenfield capability enabled?
```

A resource adapter existing in the repository does not automatically enable Greenfield.

---

## 19. Step 8 - Verify Registry

If classification succeeds:

```text
project_id
    |
    v
Application Registry
    |
    +-- bound -> continue
    |
    +-- unbound -> skip/report according to policy
```

Never apply guessed application metadata to an unbound project.

---

## 20. Step 9 - Verify Adapter

If the registry resolves but metadata is not updated, inspect:

- adapter selection
- resource lookup
- location
- current labels
- fingerprint/ETag where required
- exact IAM denial
- native API response
- operation polling
- exclusion logic

Fix the failed layer rather than broadening all IAM.

---

## 21. Greenfield Duplicate Events

Duplicate event delivery must be expected.

A duplicate should converge safely:

```text
Read current metadata
      |
      +-- already compliant -> no-op/success
      |
      +-- still non-compliant -> reconcile
```

Do not design Greenfield assuming exactly-once delivery.

---

## 22. Greenfield Temporary 404

A newly created resource may not be immediately readable through its native API.

Where validated, use bounded retry behaviour.

Distinguish:

```text
temporary not-yet-readable resource
```

from:

```text
permanently incorrect resource identifier
```

Unbounded retry loops are not acceptable.

---

## 23. Brownfield Operations

Brownfield processing governs existing resources.

Operational flow:

```text
Scope
  |
  v
Cloud Asset Inventory
  |
  v
resource_snapshot
  |
  v
Registry / Capability
  |
  v
compliance_snapshot
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
remediation_execution
```

---

## 24. Before Starting a Brownfield Run

Verify:

```text
[ ] Correct environment
[ ] Correct requested scope
[ ] Registry validated
[ ] Project bindings valid
[ ] Exclusions reviewed
[ ] Capabilities reviewed
[ ] Runtime IAM healthy
[ ] BigQuery healthy
[ ] Cloud Tasks queue healthy
[ ] Cloud Run healthy
[ ] API quotas reviewed for large runs
[ ] Dry-run decision confirmed
```

For new capabilities, begin with a representative single project.

---

## 25. Brownfield Run Execution

A run should produce:

```text
run_id
```

Record the run ID immediately.

Use it for all subsequent troubleshooting and reporting.

A run can report discovery/evaluation/planning completion while asynchronous worker batches continue.

---

## 26. Brownfield Run Evidence

Check the run in this order:

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

The first missing stage normally indicates where investigation should begin.

---

## 27. No `resource_snapshot`

Investigate:

- requested scope
- organisation/project visibility
- Cloud Asset Inventory permissions
- discovery filters
- project status
- exclusions
- discovery exceptions

Do not investigate Cloud Tasks if discovery never produced resources.

---

## 28. Snapshot Exists, Compliance Missing

Investigate:

- Application Registry binding
- capability mapping
- current-state enrichment
- compliance engine
- BigQuery write failure
- schema mismatch
- run ID filters

Do not substitute static repository data for missing compliance evidence.

---

## 29. Compliance Exists, Plan Missing

This may be correct if resources are already compliant.

If non-compliant resources exist but no plans are generated, check:

- remediation capability enabled
- dry-run behaviour
- exclusion policy
- required metadata calculation
- planner errors
- unsupported asset types

---

## 30. Plan Exists, No Cloud Tasks

Check:

```text
metadata-remediation queue
queue location
task enqueue permissions
task creation logs
batch construction
Cloud Run target URL configuration
OIDC service-account configuration
```

The current default batch configuration is:

```text
REMEDIATION_BATCH_SIZE = 500
```

unless runtime configuration overrides it.

---

## 31. Cloud Tasks Operations

Queue:

```text
metadata-remediation
```

Monitor:

- tasks created
- dispatch rate
- retry count
- task age
- failures
- queue pause/resume state
- target response codes

Do not purge or delete production tasks merely to clear an error without first understanding the impact.

---

## 32. Worker Not Invoked

If tasks exist but `/worker` has no logs, check:

```text
task target URL
Cloud Run service URL
OIDC identity
OIDC audience where configured
Cloud Run Invoker permission
service availability
HTTP route
```

Do not make `/worker` public to solve an authentication problem.

---

## 33. Worker Invoked, Resource Fails

Use the specific execution row and logs.

Check:

```text
asset type
resource name
project
location
adapter
current-state read
IAM
native API response
fingerprint/ETag
retry classification
```

Capture the exact denied permission before changing IAM.

---

## 34. IAM Denied

When a remediation receives `PERMISSION_DENIED`:

1. identify the runtime service account
2. identify the exact target resource/project
3. identify the exact denied permission
4. confirm the resource capability requires that operation
5. update the approved custom role only if justified
6. validate in DEV
7. promote through normal IAM change control

Do not grant:

```text
roles/owner
roles/editor
```

as a troubleshooting shortcut.

---

## 35. Resource Deleted During Brownfield

A resource can disappear between discovery and worker execution.

Expected behaviour:

```text
discovered historically
        |
        v
worker lookup
        |
        v
resource no longer exists
        |
        v
record appropriate outcome
```

Do not delete historical snapshot/compliance evidence.

---

## 36. Resource Becomes Compliant Before Worker

A user or another automation may correct metadata after planning but before execution.

The worker should read current state where required.

If already compliant:

```text
no unnecessary mutation
```

and record the appropriate result according to implementation semantics.

---

## 37. Fingerprint / ETag Conflict

For services using optimistic concurrency:

```text
1. Read current resource
2. Obtain current fingerprint/ETag
3. Merge managed metadata safely
4. Submit update
```

If a conflict occurs, use bounded safe retry only where the adapter is designed for it.

Do not reuse stale discovery fingerprints.

---

## 38. API Quota / Rate Limit

Symptoms may include:

```text
429
RESOURCE_EXHAUSTED
quota exceeded
rate limit exceeded
```

Actions:

- identify affected service/API
- inspect current concurrency
- inspect Cloud Tasks dispatch
- inspect `MAX_PARALLEL_WORKERS`
- reduce throughput if necessary
- verify quota in the target environment
- request quota increase only when justified

Do not increase Cloud Run concurrency blindly.

---

## 39. Cloud Run Resource Exhaustion

If containers experience memory/CPU pressure:

- identify request type
- inspect batch size
- inspect parallel workers
- inspect memory usage
- inspect long-running adapter calls
- reduce per-instance work if required
- adjust Cloud Run resources after measurement

Large Brownfield batches should not be loaded into memory unnecessarily.

---

## 40. BigQuery Operations

Monitor the four core tables:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

Check:

- insert/write errors
- schema mismatches
- query errors
- data freshness
- unexpected row growth
- dashboard query scan volume
- DEV/PROD isolation

---

## 41. BigQuery Write Failure

If remediation succeeds but evidence is missing:

```text
1. Check Cloud Run error logs
2. Confirm dataset/project configuration
3. Confirm table exists
4. Confirm schema matches payload
5. Confirm runtime BigQuery IAM
6. Confirm field types
7. Confirm quota/service health
```

A successful resource mutation with failed evidence persistence is an operational defect and must be visible.

---

## 42. Dashboard Operations

The dashboard should report operational data from backend APIs/BigQuery.

Validate:

```text
Executive Summary
Compliance
Resource distribution
Brownfield run status
Greenfield activity
Recent remediation
Failures
```

Do not use repository capability snapshots as live execution counts.

---

## 43. Dashboard Stale Data

Troubleshoot:

```text
BigQuery source row
    |
    v
backend query
    |
    v
API response
    |
    v
browser request
    |
    v
JavaScript rendering
```

Determine which layer is stale before changing UI code.

---

## 44. Dashboard Access

Dashboard access should be restricted to approved authenticated organisation users.

The backend and governance internals remain protected through Cloud Run IAM and service identities.

A user who can view the dashboard does not automatically require:

- BigQuery direct access
- Cloud Tasks access
- registry bucket access
- resource remediation IAM

Keep viewer and runtime permissions separate.

---

## 45. Platform Exclusions

Review configured exclusions before broad runs.

Controls include:

```text
EXCLUDED_PROJECTS
EXCLUDED_BUCKETS
```

Typical protected resources include:

- governance control-plane projects
- Application Registry bucket
- governance Cloud Run service
- governance Pub/Sub/Eventarc resources
- explicitly exempted client resources

Exclusions should remain configuration-driven.

---

## 46. Unsupported Resources

Unsupported resources should be skipped safely.

Example previously identified:

```text
API Keys
```

The platform should not repeatedly attempt an unsupported label operation.

If a new unsupported type appears:

```text
identify
classify
record
disable capability
document
```

until proper support is designed and validated.

---

## 47. Production Incident Severity

The client should map incidents to its own severity framework.

A practical technical classification is:

### Critical

Potential widespread incorrect metadata mutation or loss of governance control.

Examples:

- wrong application metadata being applied across projects
- uncontrolled organisation-wide remediation
- compromised runtime identity
- DEV configuration operating against PROD unexpectedly

### High

Major governance processing unavailable or broadly failing.

Examples:

- Greenfield routing stopped organisation-wide
- Brownfield workers broadly failing
- registry unavailable
- BigQuery evidence writes broadly failing

### Medium

Limited project/resource-family impact.

### Low

Non-critical reporting or isolated operational defect.

---

## 48. Emergency Stop - Brownfield

If Brownfield remediation must be stopped:

```text
1. Stop initiating new Brownfield runs
2. Pause controlled task dispatch if required
3. Identify queued/in-flight work
4. Preserve logs and BigQuery evidence
5. Identify affected run_id values
6. Correct configuration/code/IAM
7. Validate in DEV
8. Resume only after approval
```

Avoid deleting evidence during incident response.

---

## 49. Emergency Stop - Greenfield

If Greenfield is applying incorrect metadata:

```text
1. Disable/stop the affected Greenfield capability or event path
2. Preserve audit/log evidence
3. Identify affected resource type/service/method
4. Identify impacted execution rows
5. Correct classifier/registry/adapter/configuration
6. Validate with controlled DEV event
7. Re-enable after approval
8. Reconcile affected resources through controlled Brownfield if required
```

Use the least disruptive control that safely stops incorrect mutations.

---

## 50. Registry Incident

If incorrect registry metadata reaches PROD:

```text
1. Stop broad remediation if required
2. Identify affected registry commit/version
3. Identify affected projects
4. Restore validated known-good registry
5. Account for runtime cache TTL
6. Identify resources already changed
7. Validate corrected metadata
8. Reconcile affected resources
9. Preserve incident evidence
```

Restoring the registry does not automatically undo already applied resource changes.

---

## 51. Deployment Incident

If a new Cloud Run revision introduces failures:

```text
1. Identify current and previous revisions
2. Stop new broad runs
3. Determine Greenfield impact
4. Roll traffic back to known-good revision where appropriate
5. Preserve failing revision logs
6. Fix in DEV
7. redeploy through normal promotion
```

Rollback must consider schema/configuration compatibility.

---

## 52. IAM Incident

If excessive IAM is discovered:

```text
1. Identify affected identity
2. Identify excess role/permission
3. Determine whether active workloads depend on it
4. Replace with approved least privilege
5. Validate runtime
6. Remove excess grant
7. record change
```

Do not remove production permissions blindly during an active enterprise run without impact analysis.

---

## 53. Retry Strategy

Retries exist at multiple layers:

```text
application retry
Cloud Tasks retry
Event delivery retry
native API operation polling
```

Review them together.

Poorly coordinated retries can amplify failures.

For permanent errors:

```text
fail clearly
record evidence
avoid endless retry
```

For transient errors:

```text
bounded retry
backoff
preserve idempotency
```

---

## 54. Logging Standards

Production logs should be:

- structured
- searchable
- correlated
- minimally sensitive
- actionable

Recommended context:

```text
environment
run_id
execution_mode
project_id
asset_type
resource_name
operation
status
duration_ms
error_code
```

Never intentionally log secret payloads or identity tokens.

---

## 55. Recommended Alerts

Production monitoring should consider alerts for:

```text
Cloud Run 5xx increase
Cloud Run request failure rate
Greenfield event-processing failures
Cloud Tasks retry/backlog growth
BigQuery write failures
IAM-denied spikes
Registry load failures
Unsupported-event spikes
Remediation failure-rate increase
No Greenfield activity when activity is expected
```

Thresholds must be established from real production baselines.

---

## 56. Greenfield Latency Monitoring

Near-real-time governance should measure meaningful stages where possible:

```text
resource creation time
audit event time
Cloud Run receipt time
remediation execution time
```

This helps distinguish:

- audit/log routing latency
- Eventarc delivery latency
- application processing latency
- target API latency

Do not describe adapter execution duration alone as full Greenfield latency.

---

## 57. Brownfield Throughput Monitoring

Track:

```text
resources discovered
resources evaluated
plans generated
batches created
worker throughput
successful executions
failed executions
remaining work
```

Use this data to tune:

```text
REMEDIATION_BATCH_SIZE
MAX_PARALLEL_WORKERS
Cloud Tasks dispatch
Cloud Run scaling
```

---

## 58. Cost Operations

Monitor consumption for:

- Cloud Run
- Cloud Tasks
- Pub/Sub
- Eventarc
- Cloud Logging
- BigQuery
- Cloud Asset Inventory where applicable

Cost analysis should use actual billing data and current Google Cloud pricing.

Do not rely indefinitely on POC estimates for production forecasting.

---

## 59. BigQuery Cost Control

Operational reporting should use:

- partition filters
- bounded date ranges
- selected columns
- aggregation
- latest-run filtering where appropriate

Investigate dashboard queries that repeatedly scan large historical tables unnecessarily.

---

## 60. Change Management

Changes requiring controlled DEV validation include:

```text
new resource adapter
new Greenfield event mapping
organisation sink filter change
new mutation permission
registry schema change
BigQuery schema change
Cloud Tasks tuning
Cloud Run scaling change
dashboard query change
runtime dependency upgrade
```

Production should not be the first environment where these behaviours are tested.

---

## 61. New Resource Operational Onboarding

Before enabling a new resource family:

```text
[ ] Official metadata support confirmed
[ ] CAI discovery confirmed
[ ] Native API confirmed
[ ] Read IAM confirmed
[ ] Mutation IAM confirmed
[ ] Adapter tested
[ ] Brownfield tested
[ ] Real creation Audit Log captured
[ ] Greenfield classifier tested
[ ] Sink coverage tested
[ ] BigQuery evidence verified
[ ] Dashboard reporting verified
[ ] Security review complete
[ ] Production approval complete
```

---

## 62. DEV to PROD Promotion

Operational promotion sequence:

```text
Code / Terraform / Registry Change
          |
          v
platform-metadata-dev
          |
          v
Controlled Validation
          |
          v
Evidence Review
          |
          v
Approval
          |
          v
platform-metadata-prod
          |
          v
Controlled Production Test
          |
          v
Normal Operations
```

DEV and PROD must use separate identities and data stores.

---

## 63. Post-Deployment Validation

After every production deployment:

```text
[ ] Correct revision active
[ ] Health check passes
[ ] Registry loads
[ ] BigQuery access works
[ ] Cloud Tasks invocation works
[ ] Eventarc invocation works
[ ] Dashboard loads
[ ] Controlled Brownfield test works if changed
[ ] Controlled Greenfield test works if changed
[ ] No new IAM errors
[ ] No unexpected 5xx spike
```

---

## 64. Backup and Recovery

Critical recoverable platform components include:

```text
Terraform infrastructure definitions
application source
registry definitions
capability configuration
BigQuery schema definitions
CI/CD configuration
documentation/runbooks
```

Production operational evidence retention/backup must follow client requirements.

---

## 65. Disaster Recovery Considerations

The platform is serverless and can be rebuilt from infrastructure/code configuration, but recovery planning must separately address:

```text
control-plane infrastructure
registry content
BigQuery historical evidence
IAM bindings
organisation sink configuration
production secrets/configuration
```

A rebuilt service without registry/data/IAM restoration is not a complete recovery.

---

## 66. Operator Access

Operators should receive only access required for their function.

Examples:

```text
Dashboard viewer
Platform operator
Deployment engineer
Security/IAM administrator
Registry approver
```

Do not grant remediation runtime permissions directly to every dashboard user.

---

## 67. Audit Review

Periodic review should cover:

```text
IAM changes
registry changes
capability changes
production deployments
Brownfield runs
Greenfield failures
remediation failures
exclusions
unexpected unsupported resources
```

This provides evidence that the platform itself remains governed.

---

## 68. Operational Anti-Patterns

Do not:

- troubleshoot Greenfield adapters before proving event delivery
- make `/worker` public to fix Cloud Tasks authentication
- grant Owner/Editor to fix IAM errors
- run organisation-wide remediation as the first test
- hardcode client projects to fix discovery
- hide missing BigQuery data with static dashboard values
- purge failed tasks without understanding impact
- assume Cloud Run request completion means Brownfield completion
- assume Eventarc ACTIVE means source events are arriving
- assume duplicate events cannot occur
- reuse stale fingerprints/ETags
- edit production registry without validation
- mix DEV and PROD evidence
- remove historical records to make metrics look correct

---

## 69. Quick Greenfield Runbook

```text
NO GREENFIELD REMEDIATION

1. Check workload Audit Log
2. Check serviceName/methodName
3. Check organisation sink filter
4. Check sink writer Pub/Sub IAM
5. Check central Pub/Sub
6. Check Eventarc
7. Check Cloud Run logs
8. Check classifier
9. Check capability
10. Check registry binding
11. Check adapter/IAM
12. Check remediation_execution
```

---

## 70. Quick Brownfield Runbook

```text
BROWNFIELD NOT WORKING

1. Capture run_id
2. Check resource_snapshot
3. Check compliance_snapshot
4. Check remediation_plan
5. Check Cloud Tasks
6. Check /worker logs
7. Check adapter
8. Check exact IAM
9. Check target API
10. Check remediation_execution
11. Check dashboard/API
```

---

## 71. Quick Dashboard Runbook

```text
DASHBOARD WRONG/STALE

1. Check PROD vs DEV environment
2. Query BigQuery source
3. Confirm run/time scope
4. Confirm execution_mode
5. Confirm backend API response
6. Confirm browser request
7. Confirm JavaScript rendering
8. Check caching
9. Never replace missing data with hardcoded values
```

---

## 72. Production Operational Checklist

```text
[ ] Dedicated platform-metadata-prod project
[ ] Runtime service account healthy
[ ] Organisation discovery permissions healthy
[ ] Custom remediation IAM reviewed
[ ] Registry validated
[ ] Organisation sink enabled
[ ] Sink writer IAM correct
[ ] Pub/Sub healthy
[ ] Eventarc healthy
[ ] Cloud Run healthy
[ ] Cloud Tasks healthy
[ ] BigQuery healthy
[ ] Dashboard authenticated
[ ] Exclusions correct
[ ] Alerts configured
[ ] Runbooks available
[ ] DEV validation process enforced
```

---

## 73. Architecture Summary

Operations follow the same principle as the architecture itself - isolate each stage and use evidence to determine where a failure occurred.

For Greenfield:

```text
Audit Log
 -> Sink
 -> Pub/Sub
 -> Eventarc
 -> Cloud Run
 -> Classifier
 -> Registry
 -> Adapter
 -> BigQuery
```

For Brownfield:

```text
CAI
 -> resource_snapshot
 -> compliance_snapshot
 -> remediation_plan
 -> Cloud Tasks
 -> /worker
 -> Adapter
 -> remediation_execution
```

This makes the platform operationally diagnosable without broad IAM grants, hardcoded fixes or speculative changes.

---

## 74. Related Documentation

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

- `ARCHITECTURE.md` for overall platform architecture.
- `GREENFIELD.md` for Greenfield design.
- `BROWNFIELD.md` for Brownfield design.
- `IAM.md` for least-privilege permissions.
- `DATA_MODEL.md` for operational evidence.
- `SECURITY.md` for production security controls.
- `TESTING.md` for validation procedures.
