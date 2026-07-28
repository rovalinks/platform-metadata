# Enterprise Metadata Governance Platform - Production Readiness

## 1. Purpose

This document defines the final production-readiness and go-live acceptance criteria for the Enterprise Metadata Governance Platform on Google Cloud.

It is the final gate before enabling production governance at enterprise scale.

The platform uses two dedicated governance projects:

```text
DEV  -> platform-metadata-dev
PROD -> platform-metadata-prod
```

Production enablement must occur only after the required controls in this document have been validated.

---

## 2. Production Readiness Objectives

Before go-live, the platform must demonstrate:

```text
[ ] Architecture is deployed as designed
[ ] DEV and PROD are isolated
[ ] Infrastructure is reproducible
[ ] Runtime identities use least privilege
[ ] Dashboard access is authenticated and authorised
[ ] Application Registry is controlled
[ ] Brownfield processing works end-to-end
[ ] Greenfield processing works end-to-end for enabled capabilities
[ ] Operational evidence is complete
[ ] Supported resources are explicitly validated
[ ] Failure and retry behaviour is safe
[ ] Monitoring and operational runbooks exist
[ ] Cost and scale behaviour have been reviewed
[ ] Rollback/emergency-stop procedures are understood
[ ] No production behaviour depends on hardcoded workload projects
```

---

## 3. Go-Live Decision Model

Production readiness is not based on whether the application deploys successfully.

The final decision should consider:

```text
Architecture
     +
Security
     +
IAM
     +
Functional Validation
     +
Operational Readiness
     +
Data Integrity
     +
Scale
     +
Cost
     +
Recovery
     =
Production Approval
```

---

## 4. Environment Architecture

The approved environment model is:

```text
GCP ORGANISATION
       |
       +------------------------------+
       |                              |
       v                              v
platform-metadata-dev         platform-metadata-prod
       |                              |
       v                              v
Development / Validation      Production Governance
```

DEV and PROD must not share operational state accidentally.

---

## 5. Environment Isolation Gate

Verify:

```text
[ ] Separate governance projects
[ ] Separate Cloud Run deployments
[ ] Separate runtime service accounts
[ ] Separate registry storage
[ ] Separate BigQuery operational datasets
[ ] Separate Cloud Tasks configuration
[ ] Separate Pub/Sub/Eventarc resources where applicable
[ ] Separate environment configuration
[ ] PROD runtime identity is distinct
[ ] DEV runtime cannot unintentionally mutate PROD workloads
```

Status:

```text
PASS / FAIL / NOT APPLICABLE
```

---

## 6. Infrastructure as Code Gate

Production infrastructure should be managed through Terraform where practical.

Verify:

```text
[ ] Terraform configuration reviewed
[ ] terraform fmt passes
[ ] terraform validate passes
[ ] PROD plan reviewed
[ ] Environment-specific values supplied through configuration
[ ] No unnecessary console-only dependencies
[ ] Terraform state backend secured
[ ] No Terraform state committed to source control
[ ] Emergency manual changes are reconciled into code
```

---

## 7. No-Hardcoding Gate

The production application must not depend on hardcoded workload-specific values.

Verify that reusable application logic does not hardcode:

```text
client workload project IDs
application names
owner values
environment values
resource names
registry bucket names where configuration is available
dataset project paths
queue URLs
Cloud Run URLs
organisation-specific resource exceptions
```

Approved environment configuration is not considered application hardcoding.

---

## 8. Cloud Run Production Gate

Verify the production `metadata-governance` service:

```text
[ ] Deployed in approved region
[ ] Correct container image/revision
[ ] Dedicated runtime service account
[ ] Authentication enabled
[ ] No unintended allUsers Invoker
[ ] Environment variables correct
[ ] CPU/memory reviewed
[ ] Concurrency reviewed
[ ] Maximum instances reviewed
[ ] Request timeout reviewed
[ ] Health endpoint works
[ ] Structured logs available
```

---

## 9. Dashboard Access Gate

The dashboard must be available only to approved authenticated users.

Verify:

```text
[ ] Unauthenticated user cannot access protected dashboard functionality
[ ] Approved organisation user can access
[ ] Unauthorised organisation user is denied
[ ] Access model is group-based where appropriate
[ ] Dashboard user does not require remediation IAM
[ ] Dashboard user does not require Cloud Tasks access
[ ] Dashboard user does not require registry write access
[ ] Privileged credentials are not embedded in browser JavaScript
```

---

## 10. Runtime IAM Gate

The production runtime must follow least privilege.

Verify:

```text
[ ] Dedicated runtime identity
[ ] No Owner dependency
[ ] No Editor dependency
[ ] Discovery permissions reviewed
[ ] Resource read permissions reviewed
[ ] Resource mutation permissions reviewed
[ ] BigQuery permissions reviewed
[ ] Registry read permissions reviewed
[ ] Obsolete permissions removed
[ ] Permission set matches enabled capabilities
```

---

## 11. Mutation Permission Review

Review every production mutation permission against an enabled capability.

Candidate catalogue includes:

```text
resourcemanager.projects.get
resourcemanager.projects.update
compute.instances.setLabels
compute.disks.setLabels
compute.snapshots.setLabels
compute.images.setLabels
compute.forwardingRules.setLabels
compute.addresses.setLabels
storage.buckets.update
bigquery.datasets.update
bigquery.tables.update
cloudsql.instances.update
container.clusters.update
redis.instances.update
cloudkms.cryptoKeys.update
secretmanager.secrets.update
pubsub.topics.update
pubsub.subscriptions.update
artifactregistry.repositories.update
run.services.update
appengine.applications.update
appengine.services.update
appengine.versions.update
cloudbuild.builds.update
developerconnect.connections.update
developerconnect.gitRepositoryLinks.update
osconfig.osPolicyAssignments.update
eventarc.triggers.update
apigee.instances.update
monitoring.alertPolicies.update
```

A permission must not remain merely because it appeared in an earlier POC role.

---

## 12. Service Identity Gate

Verify each trust boundary uses the correct identity:

```text
Cloud Run runtime
Cloud Tasks caller
Eventarc delivery identity
Logging sink writer identity
CI/CD deployment identity
Registry publisher
```

Check:

```text
[ ] Identity purpose documented
[ ] IAM scope documented
[ ] No unnecessary impersonation
[ ] No unnecessary long-lived keys
[ ] Service-to-service authentication tested
```

---

## 13. CI/CD Gate

Verify:

```text
[ ] Production branch/workflow protected
[ ] Required validation blocks failed releases
[ ] Deployment identity restricted
[ ] Workload Identity Federation configured where used
[ ] Federation trust restricted to approved repository/context
[ ] No service-account JSON key required for normal deployment
[ ] Container build reproducible
[ ] Deployment is auditable
```

---

## 14. Application Registry Gate

The Application Registry is production-critical desired-state configuration.

Verify:

```text
[ ] PROD registry location correct
[ ] Bucket is not public
[ ] Uniform bucket-level access enabled
[ ] force_destroy disabled
[ ] Runtime has required read access
[ ] Write access restricted
[ ] Schema validation enforced
[ ] Duplicate project bindings rejected
[ ] Environment values validated
[ ] Production changes reviewed
[ ] Registry rollback procedure exists
```

---

## 15. Registry Data Gate

Review all production application records.

Verify:

```text
[ ] Application identifiers correct
[ ] Project bindings correct
[ ] Owner metadata correct
[ ] Environment metadata correct
[ ] Cost/governance metadata correct where used
[ ] No duplicate ownership
[ ] No secrets stored
[ ] No obsolete project mappings
```

Incorrect registry data can produce correct technical execution with incorrect governance results.

---

## 16. Supported Resources Gate

Every resource type enabled in production must have explicit capability evidence.

For each resource:

```text
[ ] CAI discovery validated if Brownfield enabled
[ ] Native metadata read validated
[ ] Native metadata update validated
[ ] Read IAM validated
[ ] Mutation IAM validated
[ ] Brownfield validated
[ ] Greenfield validated if enabled
[ ] Real Audit Log method captured if Greenfield enabled
[ ] Metadata preservation validated
[ ] BigQuery evidence validated
[ ] Known limitations documented
```

---

## 17. Support-State Gate

Production support status should follow:

```text
PLANNED
   |
   v
IMPLEMENTED_NOT_VALIDATED
   |
   v
VALIDATED_DEV
   |
   v
SUPPORTED
```

Only `SUPPORTED` capabilities should be broadly enabled in PROD.

---

## 18. Brownfield Production Gate

Validate the complete path:

```text
Cloud Asset Inventory
        |
        v
resource_snapshot
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
Native GCP API
        |
        v
remediation_execution
```

All stages must be observable.

---

## 19. Brownfield Scope Gate

Before organisation-scale enablement:

```text
[ ] Organisation scope correct
[ ] Discovery visibility verified
[ ] Excluded projects reviewed
[ ] Excluded resources reviewed
[ ] Governance control-plane protected
[ ] Unbound-project behaviour verified
[ ] Unsupported-resource behaviour verified
[ ] Dry-run behaviour verified where configured
```

---

## 20. Brownfield Controlled Production Test

Before broad production remediation:

```text
1. Select approved low-risk project
2. Confirm registry binding
3. Select supported resources
4. Capture current metadata
5. Start controlled Brownfield run
6. Capture run_id
7. Verify all four BigQuery stages
8. Verify Cloud Tasks
9. Verify resource metadata
10. Verify unrelated metadata preserved
11. Verify dashboard
12. Review errors
```

Do not make the first production run organisation-wide.

---

## 21. Brownfield Asynchronous Completion Gate

Verify the platform distinguishes:

```text
orchestration complete
```

from:

```text
all remediation workers complete
```

Production reporting must reconcile:

```text
planned
queued
executed
successful
failed
remaining
```

before declaring a run fully remediated.

---

## 22. Cloud Tasks Gate

Queue:

```text
metadata-remediation
```

Verify:

```text
[ ] Correct region
[ ] Correct target URL
[ ] OIDC authentication works
[ ] Invoker IAM is least privilege
[ ] Retry configuration reviewed
[ ] Dispatch rate reviewed
[ ] Queue backlog observable
[ ] Permanent failures diagnosable
[ ] Duplicate delivery safe
```

---

## 23. Worker Gate

Verify `/worker`:

```text
[ ] Not anonymously exposed
[ ] Authenticated Cloud Tasks invocation works
[ ] Batch payload validated
[ ] Adapter dispatch correct
[ ] Current state read where required
[ ] Metadata merge safe
[ ] Fingerprint/ETag handled where required
[ ] Bounded retries
[ ] Execution evidence written
```

---

## 24. Greenfield Production Gate

For every Greenfield-enabled resource type, prove:

```text
Real Resource Creation
        |
        v
Real Cloud Audit Log
        |
        v
Organisation Logging Sink
        |
        v
Central Pub/Sub
        |
        v
Eventarc
        |
        v
Cloud Run
        |
        v
Classifier
        |
        v
Registry
        |
        v
Capability Gate
        |
        v
Adapter
        |
        v
Native API
        |
        v
BigQuery Evidence
```

A manually fabricated HTTP payload is not sufficient production evidence.

---

## 25. Organisation Logging Sink Gate

Verify:

```text
[ ] Sink exists at correct organisation scope
[ ] Destination is correct PROD Pub/Sub topic
[ ] Sink enabled
[ ] Filter reviewed
[ ] Required Greenfield creation events match
[ ] Unnecessary event export minimised
[ ] Writer identity documented
[ ] Writer has only required Pub/Sub publish access
```

---

## 26. Pub/Sub Gate

Verify the production event topic:

```text
metadata-governance-events
```

Check:

```text
[ ] Correct project
[ ] Correct IAM
[ ] Sink writer can publish
[ ] Unnecessary publishers removed
[ ] Eventarc integration works
[ ] Message delivery observable
```

---

## 27. Eventarc Gate

Trigger:

```text
metadata-governance-trigger
```

Verify:

```text
[ ] Correct region
[ ] Correct source topic
[ ] Correct event type
[ ] Correct Cloud Run destination
[ ] Delivery identity correct
[ ] Cloud Run Invoker granted only as required
[ ] Controlled PROD event successfully delivered
```

---

## 28. Greenfield Classification Gate

For each supported Greenfield resource:

```text
[ ] serviceName captured from real Audit Log
[ ] methodName captured from real Audit Log
[ ] Canonical asset type correct
[ ] Resource parser correct
[ ] Project parser correct
[ ] Location parser correct where required
[ ] Unsupported methods safely ignored
```

Do not infer all create methods from naming conventions.

---

## 29. Greenfield Idempotency Gate

Verify duplicate delivery does not create unsafe repeated mutation.

Expected behaviour:

```text
event
  |
  v
read current metadata
  |
  +-- compliant -> no unnecessary mutation
  |
  +-- non-compliant -> reconcile
```

---

## 30. Greenfield Retry Gate

Verify:

```text
[ ] Temporary resource-read 404 handled where applicable
[ ] Transient API failure bounded
[ ] Permanent errors stop appropriately
[ ] Duplicate/retry remains idempotent
[ ] No infinite retry loop
[ ] Failure evidence retained
```

---

## 31. BigQuery Production Gate

Core tables:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

Verify:

```text
[ ] PROD dataset exists
[ ] DEV and PROD separated
[ ] Schema matches application
[ ] Runtime writes succeed
[ ] Dashboard reads succeed
[ ] IAM least privilege
[ ] Timestamps consistent
[ ] run_id correlation correct
[ ] execution_mode correct
[ ] Failures visible
```

---

## 32. Data Integrity Gate

For representative Brownfield resources, prove:

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

For Greenfield, prove execution evidence correctly identifies:

```text
project
resource
asset type
execution mode
status
timestamp
service/method where implemented
```

---

## 33. Dashboard Data Gate

Verify the dashboard derives current operational metrics from the platform's operational data.

Check:

```text
[ ] Executive Summary dynamic
[ ] Resource counts dynamic
[ ] Compliance dynamic
[ ] Brownfield runs dynamic
[ ] Greenfield activity dynamic
[ ] Failures dynamic
[ ] Recent activity dynamic
[ ] Correct PROD environment
[ ] Empty states correct
[ ] No fabricated demo metrics
```

---

## 34. Current-State Semantics Gate

Dashboard stakeholders must understand the difference between:

```text
latest observed compliance
historical compliance
successful remediation history
current resource state
```

Do not present lifetime successful executions as current compliance.

Metric definitions should be documented.

---

## 35. Exclusion Gate

Review all production exclusions.

Verify:

```text
[ ] EXCLUDED_PROJECTS reviewed
[ ] EXCLUDED_BUCKETS reviewed
[ ] Registry bucket protected
[ ] Governance resources protected where required
[ ] Client-approved exemptions documented
[ ] Exclusions configuration-driven
[ ] No scattered adapter-specific hardcoded exclusions
```

---

## 36. Self-Governance Safety Gate

Because the platform can govern Cloud Run, Pub/Sub, Eventarc, Storage and BigQuery resources, validate that it cannot accidentally disrupt its own control plane.

Explicitly review:

```text
platform-metadata-prod
registry bucket
metadata-governance service
metadata-remediation queue
metadata-governance-events topic
metadata-governance-trigger
operational BigQuery dataset
```

---

## 37. Metadata Preservation Gate

For every adapter, verify:

```text
existing unrelated metadata
        +
managed governance metadata
        =
final metadata
```

Production approval must fail if an adapter deletes unrelated labels unexpectedly.

---

## 38. Concurrency Gate

For services using fingerprints, ETags or equivalent concurrency controls:

```text
[ ] Current token read immediately before update
[ ] Safe merge performed
[ ] Stale-token conflict handled
[ ] Unrelated concurrent changes preserved
```

Do not rely on stale discovery-time concurrency tokens.

---

## 39. Unsupported Resource Gate

Unsupported resources must:

```text
skip safely
remain observable
not cause uncontrolled retries
not block other resources
```

API Keys remain excluded unless a validated supported metadata implementation is introduced.

---

## 40. Monitoring Gate

Production monitoring should cover:

```text
Cloud Run availability
Cloud Run 5xx
Cloud Run latency
Cloud Tasks backlog
Cloud Tasks retry growth
Greenfield failures
BigQuery write failures
registry load failures
IAM-denied spikes
remediation failure rate
unexpected execution volume
```

Thresholds should be agreed using measured baseline behaviour.

---

## 41. Logging Gate

Verify production logs contain sufficient structured context:

```text
environment
run_id
execution_mode
project_id
asset_type
resource_name
operation
status
duration
error code
```

Verify they do not intentionally expose:

```text
tokens
credentials
secret payloads
private keys
```

---

## 42. Alerting Gate

Verify operational ownership for alerts.

For each alert:

```text
Who receives it?
What constitutes failure?
What is the first diagnostic step?
What runbook applies?
What escalation path applies?
```

An alert without an owner/runbook is not operationally complete.

---

## 43. Security Gate

Verify:

```text
[ ] Cloud Run authenticated
[ ] No unintended public invocation
[ ] Worker protected
[ ] Dashboard authorised
[ ] Registry protected
[ ] Pub/Sub protected
[ ] BigQuery protected
[ ] Service identities separated
[ ] No unnecessary service-account keys
[ ] No credentials in source
[ ] No credentials in browser JavaScript
[ ] No secrets in registry
[ ] No Owner/Editor runtime dependency
```

---

## 44. Auditability Gate

Production must provide evidence for:

```text
code change
registry change
Terraform change
IAM change
deployment
Brownfield run
Greenfield execution
resource remediation
failure
operator action
```

Use the appropriate combination of Git, CI/CD, Cloud Audit Logs, application logs and BigQuery.

---

## 45. Failure Handling Gate

Validate representative failures:

```text
registry unavailable
resource deleted
permission denied
temporary 404
API 429
API 5xx
BigQuery write failure
Cloud Tasks retry
unsupported event
unsupported resource
invalid registry binding
```

Production must fail safely and visibly.

---

## 46. Emergency Stop Gate

Operators must know how to stop:

```text
Brownfield initiation
Brownfield task dispatch where necessary
Greenfield event processing
affected capability
```

without destroying evidence.

Runbooks must be available before broad enablement.

---

## 47. Rollback Gate

Verify rollback paths for:

```text
Cloud Run revision
Terraform change
registry change
IAM change
capability change
dashboard change
BigQuery schema change
```

Not every change can be rolled back identically.

For example, reverting a registry does not automatically reverse metadata already written to workload resources.

---

## 48. Disaster Recovery Gate

Verify recovery requirements for:

```text
source code
Terraform
Terraform state
container images
registry
BigQuery operational evidence
IAM
organisation sink
Pub/Sub
Eventarc
Cloud Tasks
Cloud Run configuration
```

Document which components are rebuilt and which contain state requiring preservation/restoration.

---

## 49. Scale Gate

Before enterprise-wide Brownfield execution, complete representative scale tests.

Measure:

```text
discovery throughput
evaluation throughput
task generation
worker throughput
target API latency
quota utilisation
Cloud Run scaling
BigQuery ingestion
failure rate
```

Use measured results for capacity planning.

---

## 50. One-Million-Resource Readiness

For a target estate approaching 1,000,000 resources, production readiness should be based on measured scale behaviour rather than theoretical execution time.

Validate:

```text
[ ] CAI discovery strategy
[ ] BigQuery volume
[ ] Task count/batching
[ ] Worker concurrency
[ ] Per-service quotas
[ ] Retry amplification risk
[ ] Run completion tracking
[ ] Dashboard query scalability
[ ] Operational support capacity
```

---

## 51. Batch and Concurrency Gate

Current runtime defaults such as:

```text
REMEDIATION_BATCH_SIZE = 500
MAX_PARALLEL_WORKERS = <configured value>
```

must be treated as tunable configuration.

Before go-live:

```text
[ ] Batch size tested
[ ] Worker parallelism tested
[ ] Target API quotas reviewed
[ ] Cloud Run memory reviewed
[ ] Queue dispatch reviewed
```

Do not tune purely for maximum speed.

---

## 52. Cost Readiness Gate

Production cost estimates should use actual DEV/load-test measurements and current Google Cloud pricing.

Review:

```text
Cloud Run
Cloud Tasks
Pub/Sub
Eventarc
Cloud Logging
BigQuery
Cloud Asset Inventory where chargeable/applicable
network/data transfer where applicable
```

Do not treat earlier POC estimates as guaranteed production cost.

---

## 53. Zero-Idle Infrastructure Principle

The architecture is designed around serverless managed services so that the platform does not require continuously running VMs or Kubernetes worker infrastructure for governance processing.

Validate that production has not accidentally introduced:

```text
always-on VM workers
permanent polling hosts
unnecessary GKE clusters
manual scheduler servers
```

unless separately justified.

---

## 54. Availability Expectations

Document expected behaviour if:

```text
Cloud Run unavailable temporarily
Pub/Sub/Eventarc delivery delayed
Cloud Tasks backlog develops
BigQuery write temporarily fails
registry read fails
target service API is unavailable
```

The serverless design provides managed platform resilience, but application-level recovery and retry semantics must still be understood.

---

## 55. Performance Acceptance

Agree measurable acceptance targets for:

```text
Greenfield end-to-end latency
Brownfield completion window
worker failure rate
queue backlog
dashboard response time
remediation success rate
```

Do not use undefined terms such as "real-time" in production acceptance without a measurable target.

---

## 56. Documentation Gate

Before handover/go-live, confirm the repository includes:

```text
README.md
docs/ARCHITECTURE.md
docs/DEPLOYMENT.md
docs/IAM.md
docs/GREENFIELD.md
docs/BROWNFIELD.md
docs/APPLICATION_REGISTRY.md
docs/SUPPORTED_RESOURCES.md
docs/API.md
docs/DATA_MODEL.md
docs/OPERATIONS.md
docs/SECURITY.md
docs/TESTING.md
docs/PRODUCTION_READINESS.md
```

Documentation must reflect the deployed implementation.

---

## 57. Client Handover Gate

The client operations/platform team should understand:

```text
how to deploy
how to update registry
how to start Brownfield
how to identify run_id
how to determine completion
how to troubleshoot Greenfield
how to troubleshoot worker failures
how to view evidence
how to control dashboard access
how to stop processing
how to add a resource capability
```

A platform that only the original developer can operate is not production-ready.

---

## 58. Ownership Gate

Assign operational ownership for:

```text
platform code
Terraform
registry
IAM
production deployment
dashboard access
incident response
cost review
supported-resource certification
```

Avoid ambiguous ownership for security-sensitive configuration.

---

## 59. Production Change Process

Recommended flow:

```text
Change
  |
  v
Code / Terraform / Registry Review
  |
  v
DEV
  |
  v
Automated Validation
  |
  v
Controlled Functional Test
  |
  v
Evidence Review
  |
  v
Approval
  |
  v
PROD
  |
  v
Smoke Test
  |
  v
Controlled Production Test
  |
  v
Normal Operation
```

---

## 60. Initial Production Rollout

Recommended rollout sequence:

```text
Stage 1 - Platform infrastructure
Stage 2 - Dashboard/read-only visibility
Stage 3 - Controlled Brownfield single project
Stage 4 - Controlled Greenfield resource types
Stage 5 - Additional validated projects
Stage 6 - Wider Brownfield scope
Stage 7 - Enterprise-scale operation
```

Progress only after reviewing evidence from the previous stage.

---

## 61. First Enterprise Brownfield Run

Before the first broad run:

```text
[ ] Registry coverage reviewed
[ ] Unbound projects quantified
[ ] Resource counts understood
[ ] Supported-resource mix understood
[ ] Exclusions approved
[ ] API quotas reviewed
[ ] Task throughput reviewed
[ ] Runtime scaling reviewed
[ ] Monitoring active
[ ] Operators available
[ ] Emergency-stop procedure ready
[ ] Client change window approved if required
```

---

## 62. Post-Go-Live Validation

After production enablement, verify:

```text
[ ] No unexpected mutation volume
[ ] No significant IAM denial spike
[ ] No unexpected unsupported-resource failures
[ ] Registry resolution healthy
[ ] BigQuery evidence complete
[ ] Dashboard current
[ ] Greenfield events arriving
[ ] Brownfield tasks completing
[ ] Cost within expected range
[ ] Control-plane exclusions working
```

---

## 63. First-Week Operational Review

After the initial production period, review:

```text
remediation success rate
top failure causes
Greenfield latency
Brownfield throughput
queue backlog
API quota behaviour
Cloud Run scaling
BigQuery query cost
dashboard usage
registry data-quality issues
unbound projects
unexpected resource types
```

Use findings to tune configuration rather than hardcode special cases.

---

## 64. Production Readiness Anti-Patterns

Do not approve production if:

- Owner/Editor is required by runtime
- Cloud Run must be public for internal processing
- PROD registry changes are unmanaged
- DEV can unintentionally remediate PROD
- dashboard uses hardcoded operational metrics
- unsupported resources are silently treated as supported
- Greenfield support is based only on fake events
- Brownfield completion cannot be determined
- unrelated labels can be deleted
- failures are not persisted/observable
- organisation-wide remediation is the first production test
- workload project IDs are hardcoded
- there is no emergency-stop procedure
- there is no operational owner

---

## 65. Final Go-Live Checklist

### Architecture

```text
[ ] Dedicated DEV project
[ ] Dedicated PROD project
[ ] Serverless architecture deployed
[ ] No unnecessary always-on infrastructure
[ ] Control-plane resources protected
```

### Application

```text
[ ] Correct production revision
[ ] No hardcoded workload-specific values
[ ] Registry-driven desired state
[ ] Capability-driven dispatch
[ ] Safe metadata merge
[ ] Idempotent processing
```

### Brownfield

```text
[ ] CAI discovery validated
[ ] Compliance validated
[ ] Planning validated
[ ] Cloud Tasks validated
[ ] Worker validated
[ ] Completion tracking validated
[ ] Controlled PROD test passed
```

### Greenfield

```text
[ ] Organisation sink validated
[ ] Pub/Sub validated
[ ] Eventarc validated
[ ] Real Audit Logs captured
[ ] Classifier validated
[ ] Controlled PROD test passed
[ ] Duplicate/retry behaviour validated
```

### Security

```text
[ ] Least privilege
[ ] Dashboard authenticated
[ ] Worker protected
[ ] Event delivery authenticated
[ ] Registry protected
[ ] No long-lived credentials required by normal runtime
[ ] No secrets in source/browser/registry
```

### Data

```text
[ ] Four core BigQuery tables validated
[ ] DEV/PROD isolation
[ ] run_id correlation
[ ] execution_mode correlation
[ ] Failure evidence
[ ] Dashboard uses operational data
```

### Operations

```text
[ ] Monitoring
[ ] Alerts
[ ] Runbooks
[ ] Emergency stop
[ ] Rollback
[ ] Incident ownership
[ ] Cost monitoring
```

### Scale

```text
[ ] Representative load test
[ ] API quota review
[ ] Batch size validated
[ ] Parallelism validated
[ ] Million-resource model based on measurements
```

### Documentation

```text
[ ] Architecture
[ ] Deployment
[ ] IAM
[ ] Greenfield
[ ] Brownfield
[ ] Registry
[ ] Supported resources
[ ] API
[ ] Data model
[ ] Operations
[ ] Security
[ ] Testing
[ ] Production readiness
```

---

## 66. Formal Acceptance Record

Recommended final acceptance record:

```text
Platform:
Enterprise Metadata Governance Platform

Environment:
platform-metadata-prod

Release / Revision:
____________________________

Terraform Version / Commit:
____________________________

Application Commit:
____________________________

Registry Version:
____________________________

Validation Date:
____________________________

Brownfield Acceptance:
PASS / FAIL / N/A

Greenfield Acceptance:
PASS / FAIL / N/A

Security Review:
PASS / FAIL

IAM Review:
PASS / FAIL

Operational Readiness:
PASS / FAIL

Scale Review:
PASS / FAIL

Cost Review:
PASS / FAIL

Known Exceptions:
____________________________
____________________________

Approved By - Platform:
____________________________

Approved By - Security:
____________________________

Approved By - Client:
____________________________

Go-Live Decision:
APPROVED / NOT APPROVED
```

---

## 67. Production Acceptance Principle

Production approval means more than successful deployment.

The platform is ready only when it can demonstrate:

```text
Correct desired state
        +
Correct resource discovery/event detection
        +
Correct compliance decision
        +
Safe metadata remediation
        +
Least-privilege execution
        +
Complete operational evidence
        +
Controlled scale
        +
Operational recoverability
```

---

## 68. Final Architecture Summary

The production architecture provides two complementary governance paths.

### Greenfield

```text
Resource Creation
      |
      v
Cloud Audit Logs
      |
      v
Organisation Logging Sink
      |
      v
Pub/Sub
      |
      v
Eventarc
      |
      v
Cloud Run
      |
      v
Application Registry
      |
      v
Capability / Adapter
      |
      v
Native GCP API
      |
      v
BigQuery Evidence
```

### Brownfield

```text
Cloud Asset Inventory
      |
      v
Resource Snapshot
      |
      v
Compliance
      |
      v
Remediation Plan
      |
      v
Cloud Tasks
      |
      v
Cloud Run Worker
      |
      v
Capability / Adapter
      |
      v
Native GCP API
      |
      v
BigQuery Evidence
```

The design remains serverless, event-driven, auditable and configuration-driven, with no requirement for continuously running governance compute infrastructure.

---

## 69. Final Recommendation

Production enablement should proceed incrementally.

The recommended order is:

```text
1. Complete all critical security and IAM gates
2. Validate PROD infrastructure and dashboard
3. Validate one controlled Brownfield project
4. Validate each enabled Greenfield capability using a real resource event
5. Review BigQuery evidence
6. Review failures and quotas
7. Expand to a controlled project cohort
8. Measure throughput and cost
9. Expand to enterprise scale only after evidence supports it
```

This approach preserves the benefits of the serverless architecture while controlling enterprise-wide remediation risk.

---

## 70. Related Documentation

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

This document is the final production acceptance gate and should be reviewed together with all preceding technical documentation before go-live.
