# Enterprise Metadata Governance Platform - Testing Strategy

## 1. Purpose

This document defines the testing and validation strategy for the Enterprise Metadata Governance Platform on Google Cloud.

Testing covers:

- Application Registry
- Brownfield discovery
- compliance evaluation
- remediation planning
- Cloud Tasks workers
- Greenfield event routing
- resource adapters
- BigQuery evidence
- dashboard APIs and UI
- IAM and security
- DEV-to-PROD promotion
- scale, retries and failure handling

The platform uses two dedicated governance projects:

```text
DEV  -> platform-metadata-dev
PROD -> platform-metadata-prod
```

New functionality must be validated in DEV before production enablement.

---

## 2. Testing Principles

```text
Test real behaviour, not assumptions
Validate each layer independently
Use real GCP resources for integration tests
Capture real Audit Logs for Greenfield
Test Brownfield and Greenfield independently
Verify metadata preservation
Verify operational evidence
Test failure paths
Test least privilege
Never use production as the first test environment
```

Code presence alone is not evidence that a resource type is supported.

---

## 3. Test Layers

The platform should be validated at multiple levels:

```text
Static Validation
      |
      v
Unit Tests
      |
      v
Component Tests
      |
      v
Integration Tests
      |
      v
End-to-End DEV Tests
      |
      v
Scale / Failure Tests
      |
      v
Security Validation
      |
      v
Production Smoke Test
```

A failure at a lower layer should normally be corrected before broader testing continues.

---

## 4. Test Environments

### DEV

`platform-metadata-dev` is the primary implementation and validation environment.

DEV is used for:

- new adapters
- new resource types
- Greenfield event capture
- registry changes
- BigQuery schema changes
- IAM validation
- dashboard changes
- retry behaviour
- controlled failure testing

### PROD

`platform-metadata-prod` receives only validated changes.

PROD testing should be limited to controlled smoke and acceptance tests.

---

## 5. Test Workload Projects

The governance platform should be tested against representative workload projects rather than only against its own control-plane project.

Test projects should cover:

```text
registered application project
unbound project
supported resource types
different environments
different locations
excluded resources where applicable
```

Do not hardcode test project IDs into reusable application logic.

---

## 6. Application Registry Tests

Registry validation must test:

```text
[ ] Valid YAML accepted
[ ] Invalid YAML rejected
[ ] Required fields enforced
[ ] Invalid data types rejected
[ ] Invalid environment rejected
[ ] Duplicate project binding rejected
[ ] Missing project binding handled
[ ] Multiple valid applications load correctly
[ ] Cache refresh behaviour works
```

---

## 7. Registry Environment Validation

If the approved schema allows:

```text
dev
prod
test
uat
```

test each valid value and at least one invalid value.

For example, an unsupported alias such as:

```text
development
```

must fail if it is not part of the schema.

Do not weaken validation simply to accept inconsistent registry data.

---

## 8. Registry Runtime Tests

Validate:

```text
GCS object
    |
    v
Registry Reader
    |
    v
YAML Parser
    |
    v
Application Mapping
    |
    v
Project Resolution
```

Test:

- valid project resolution
- unknown project
- duplicate project protection
- inaccessible bucket
- malformed registry object
- cache expiry
- multiple application definitions

---

## 9. Compliance Engine Unit Tests

For each managed key, test:

```text
required label missing
required label correct
required label incorrect
multiple labels missing
mixed correct/incorrect labels
unrelated labels present
empty existing labels
```

The engine must not mark a resource non-compliant solely because unrelated labels exist.

---

## 10. Metadata Merge Tests

Adapters must preserve unrelated metadata.

Example:

```text
Existing:
  app-label: keep-me
  owner: old-value

Required managed:
  owner: new-value
  environment: dev
```

Expected logical result:

```text
app-label: keep-me
owner: new-value
environment: dev
```

The unrelated `app-label` must survive remediation.

---

## 11. Dispatcher Tests

For every canonical asset type:

```text
canonical asset type
       |
       v
dispatcher
       |
       v
correct adapter
```

Test:

- supported asset
- unsupported asset
- malformed asset type
- missing adapter
- disabled capability

Unsupported resources must fail or skip safely according to platform policy.

---

## 12. Adapter Unit Tests

Each adapter should test:

```text
resource lookup
current metadata extraction
safe merge
correct API request
location handling
fingerprint/ETag handling
success response
404
403
409/precondition conflict
429/quota
5xx/transient error
```

Use mocked clients for pure unit tests.

Real GCP validation is still required separately.

---

## 13. Compute Tests

Validate independently:

```text
VM instance
disk
snapshot
image
forwarding rule
address
```

Where applicable, test:

- zonal resources
- regional resources
- global resources
- label fingerprint
- unrelated label preservation

Do not infer one Compute resource's support from another.

---

## 14. Cloud Storage Tests

Validate:

```text
bucket discovery
existing labels read
managed labels merged
unrelated labels preserved
update succeeds
excluded bucket skipped
registry bucket protected
```

A test must prove that governance does not damage existing application labels.

---

## 15. BigQuery Resource Tests

For governed workload BigQuery resources, test Dataset and Table separately.

Validate:

```text
discovery
current metadata
update semantics
unrelated metadata preservation
IAM
Brownfield evidence
Greenfield event if enabled
```

Do not confuse workload BigQuery tests with tests of the platform's governance evidence dataset.

---

## 16. Cloud SQL Tests

Validate:

```text
instance discovery
current labels
update request
asynchronous operation handling
successful completion
failed operation
timeout behaviour
```

Brownfield and Greenfield tests remain separate.

---

## 17. GKE Tests

Validate:

```text
zonal cluster where applicable
regional cluster
current metadata
update semantics
operation completion
IAM
```

Cluster support does not automatically prove NodePool support.

---

## 18. Additional Adapter Tests

Where enabled, independently validate:

```text
Memorystore Redis
Cloud KMS CryptoKey
Secret Manager Secret
Pub/Sub Topic
Pub/Sub Subscription
Artifact Registry Repository
Cloud Run Service
App Engine Application
App Engine Service
App Engine Version
Cloud Build Build
Developer Connect Connection
Developer Connect Git Repository Link
OS Config Policy Assignment
Eventarc Trigger
Apigee Instance
Monitoring Alert Policy
```

Each requires its own capability evidence.

---

## 19. Unsupported Resource Tests

For resources that do not support the platform's metadata model:

```text
resource encountered
      |
      v
capability gate
      |
      v
safe skip
```

The platform must not repeatedly throw unhandled exceptions.

API Keys are an example previously excluded because the required label capability was unavailable for this platform.

---

## 20. Brownfield End-to-End Test

For a controlled DEV project:

```text
1. Register project
2. Create supported resources
3. Apply deliberately missing/incorrect managed metadata
4. Start Brownfield run
5. Capture run_id
6. Verify CAI discovery
7. Verify resource_snapshot
8. Verify compliance_snapshot
9. Verify remediation_plan
10. Verify Cloud Tasks
11. Verify /worker
12. Verify target resource metadata
13. Verify remediation_execution
14. Verify dashboard
```

---

## 21. Brownfield Compliant Resource Test

Create a resource already containing correct managed metadata.

Expected:

```text
discovered
evaluated
compliant
no unnecessary remediation
```

The platform should not mutate an already compliant resource without reason.

---

## 22. Brownfield Incorrect Metadata Test

Create a resource with a managed key containing the wrong value.

Expected:

```text
non-compliant
planned
remediated
correct registry value applied
unrelated metadata preserved
SUCCESS evidence
```

---

## 23. Brownfield Missing Metadata Test

Create a resource with one or more managed keys absent.

Expected:

```text
missing labels identified
plan created
worker executes
required metadata added
```

---

## 24. Brownfield Unbound Project Test

Use a project not present in the Application Registry.

Expected:

```text
no guessed ownership
no arbitrary application metadata
explicit skip/report behaviour
```

The exact status should match the implementation.

---

## 25. Brownfield Exclusion Test

Use a configured excluded project/resource.

Expected:

```text
resource may be discoverable
but remediation is not performed
```

Verify exclusion evidence/logging.

---

## 26. Brownfield Resource Deletion Test

Test:

```text
discover resource
generate plan
delete resource
worker executes
```

Expected:

- no uncontrolled retry loop
- appropriate execution outcome
- historical snapshot retained

---

## 27. Brownfield Concurrency Test

For an API using fingerprints/ETags:

```text
1. Discover/evaluate resource
2. Change resource metadata externally
3. Execute remediation
```

The adapter should read current state and avoid overwriting unrelated concurrent changes.

---

## 28. Brownfield Asynchronous Completion Test

Verify that:

```text
orchestration response
```

and:

```text
final worker completion
```

are treated separately.

A run must not be reported as fully remediated merely because tasks were successfully queued.

---

## 29. Cloud Tasks Tests

Validate:

```text
task creation
correct target
OIDC authentication
batch payload
worker invocation
successful task acknowledgement
retryable failure
permanent failure handling
duplicate delivery
queue rate
```

---

## 30. Batch Size Tests

The current default is:

```text
REMEDIATION_BATCH_SIZE = 500
```

unless overridden by configuration.

Test:

- small batch
- full configured batch
- final partial batch
- multiple batches
- payload-size limits
- worker memory behaviour

Do not assume 500 is optimal for every production workload.

---

## 31. Parallel Worker Tests

Where configured through:

```text
MAX_PARALLEL_WORKERS
```

validate:

- target API quota behaviour
- Cloud Run CPU/memory
- worker duration
- failure isolation
- throttling
- safe retry

Tune using measured DEV evidence.

---

## 32. Greenfield End-to-End Test

For every Greenfield-supported resource:

```text
1. Create real resource in DEV workload project
2. Capture real Cloud Audit Log
3. Confirm serviceName
4. Confirm methodName
5. Confirm organisation sink match
6. Confirm Pub/Sub delivery
7. Confirm Eventarc delivery
8. Confirm Cloud Run receipt
9. Confirm classifier
10. Confirm project/resource identity
11. Confirm registry resolution
12. Confirm capability
13. Confirm adapter
14. Confirm metadata on resource
15. Confirm GREENFIELD execution row
```

This test is mandatory before claiming Greenfield support.

---

## 33. Real Audit Event Requirement

Do not populate Greenfield mappings based only on API documentation or assumptions.

Capture a real DEV creation event and record:

```text
protoPayload.serviceName
protoPayload.methodName
log category
resource identity fields
project identity fields
```

Then compare the observed behaviour with official Google Cloud documentation.

---

## 34. Greenfield Cross-Project Test

Create a supported resource in a workload project different from:

```text
platform-metadata-dev
```

Expected:

```text
organisation sink captures event
central Pub/Sub receives it
Eventarc invokes central Cloud Run
correct workload project is resolved
metadata is remediated
```

This proves the architecture is organisation-level rather than governance-project-only.

---

## 35. Greenfield No-Log Test

If a supported resource is created and Cloud Run receives nothing, validate the path:

```text
Audit Log
 -> Organisation Sink
 -> Pub/Sub
 -> Eventarc
 -> Cloud Run
```

The test is failed until the missing layer is identified.

Do not mark the adapter as broken when the event never reached it.

---

## 36. Greenfield Duplicate Event Test

Replay/deliver the same logical event more than once.

Expected:

```text
first delivery -> reconcile if needed
duplicate -> resource already compliant -> safe no-op
```

No duplicate destructive behaviour should occur.

---

## 37. Greenfield Temporary 404 Test

Where applicable, simulate or observe a creation event arriving before the resource is readable.

Expected:

```text
bounded retry
eventual success when resource becomes readable
or clear failure after configured retry limit
```

No infinite retry.

---

## 38. Greenfield Unsupported Event Test

Send/observe an event not mapped to an enabled capability.

Expected:

```text
safe acknowledgement/skip or controlled failure
no resource mutation
no uncontrolled redelivery loop
```

Behaviour must match the application's retry strategy.

---

## 39. Greenfield Unbound Project Test

Create a supported resource in an unregistered project.

Expected:

```text
event reaches platform
classification succeeds
registry resolution fails safely
no guessed metadata
```

---

## 40. Event Filter Tests

For each enabled Greenfield resource, verify the organisation sink filter:

```text
includes required creation event
excludes clearly unrelated events
```

Test with real events.

Avoid relying only on broad regex matching.

---

## 41. Eventarc Authentication Test

Verify that the configured Eventarc delivery identity can invoke Cloud Run.

Then verify an unauthorised identity cannot invoke the service where Cloud Run IAM is the enforcement boundary.

---

## 42. Cloud Tasks Authentication Test

Verify:

```text
Cloud Tasks OIDC caller -> /worker succeeds
unauthorised caller -> rejected
```

Do not temporarily enable public access as the acceptance test.

---

## 43. Dashboard Authentication Test

Test with:

```text
authorised organisation user
unauthorised organisation user
unauthenticated browser
```

Expected access must match the approved production design.

Dashboard viewing must not grant runtime remediation privileges.

---

## 44. Dashboard Data Tests

Verify that live dashboard values come from operational data.

Test:

```text
Executive Summary
resource counts
compliance counts
remediation counts
Greenfield activity
Brownfield activity
recent failures
latest run
```

Change operational test data and confirm the dashboard changes accordingly.

---

## 45. No Repository Snapshot Dependency Test

Remove or alter a repository snapshot fixture in DEV without changing BigQuery operational evidence.

The live dashboard must not suddenly report that fixture as current platform state.

This proves the dashboard is operational-data-driven.

---

## 46. Dashboard Empty-State Test

When a query legitimately returns no data:

Expected:

```text
clear empty state / zero where semantically correct
```

Not:

```text
hardcoded demo counts
stale repository counts
fabricated success
```

---

## 47. BigQuery Evidence Tests

Validate each core table:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

Check:

- expected row written
- correct run_id
- correct project
- correct asset type
- correct resource
- correct timestamps
- correct status
- correct execution mode

---

## 48. Brownfield Correlation Test

For one Brownfield resource, prove traceability:

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

using the same `run_id` and canonical resource identity.

---

## 49. Greenfield Evidence Test

For a Greenfield resource, verify:

```text
execution_mode = GREENFIELD
```

and where implemented:

```text
service_name
method_name
project_id
asset_type
resource_name
status
executed_at
```

must reflect the actual event/execution.

---

## 50. BigQuery Schema Failure Test

In DEV, test application behaviour when:

- expected field is missing
- wrong data type is produced
- table unavailable
- runtime IAM denied

The platform must log evidence-write failures clearly.

A successful resource mutation with failed evidence persistence must not be invisible.

---

## 51. IAM Positive Tests

For each supported adapter:

```text
runtime identity
   +
minimum approved permissions
   =
successful read/update
```

Record the permissions proven necessary.

---

## 52. IAM Negative Tests

Where safe in DEV, remove a required permission and confirm:

```text
operation fails with expected permission denial
failure is logged
execution evidence records failure where possible
no broad fallback role is used
```

Restore the approved permission after the test.

---

## 53. Least-Privilege Validation

Before production, review the runtime custom role against enabled capabilities.

For each permission:

```text
Which code path uses this?
Which supported resource requires it?
Was it validated?
```

Permissions without an active justification should be reviewed for removal.

---

## 54. Security Tests

Validate:

```text
[ ] Cloud Run not publicly invokable
[ ] /worker protected
[ ] Eventarc caller authorised
[ ] Dashboard access restricted
[ ] Registry bucket not public
[ ] Runtime cannot read secret payloads unnecessarily
[ ] No service-account keys in application
[ ] No privileged credentials in dashboard.js
[ ] DEV identity does not unintentionally control PROD
[ ] Error responses do not expose stack traces/secrets
```

---

## 55. Exclusion Security Tests

Verify configured platform exclusions.

Examples:

```text
registry bucket
governance project
governance Cloud Run service
governance Pub/Sub topic
governance Eventarc trigger
```

where the approved design requires exclusion.

The test should prove actual skip behaviour, not merely inspect configuration.

---

## 56. Failure Injection Tests

DEV should test controlled failures such as:

```text
registry unavailable
BigQuery unavailable/denied
target resource permission denied
resource deleted
temporary 404
API 429
API 5xx
Cloud Tasks retry
invalid event
unsupported asset type
```

Verify safe and diagnosable behaviour.

---

## 57. Retry Tests

Retries must be tested at each applicable layer:

```text
application retry
Cloud Tasks retry
Event delivery retry
native long-running operation polling
```

Verify:

- bounded retries
- backoff
- idempotency
- permanent error termination
- no retry storm

---

## 58. Scale Tests

Brownfield scale tests should progressively increase resource volume.

Example progression:

```text
10
100
1,000
10,000
larger representative load
```

Measure:

- discovery duration
- evaluation throughput
- task creation
- worker throughput
- Cloud Run scaling
- target API quota
- BigQuery writes
- error rate
- cost

Do not begin enterprise scale validation with the full organisation.

---

## 59. Million-Resource Scale Modelling

If the client target is approximately 1,000,000 resources, validate the architecture using measured throughput from representative tests.

Do not claim an exact million-resource runtime or cost from theoretical API timings alone.

Use:

```text
measured worker duration
measured task throughput
actual API quotas
actual BigQuery volume
actual Cloud Run billing
actual CAI behaviour
```

to produce the production estimate.

---

## 60. Performance Acceptance

Define acceptance thresholds with the client for:

```text
Greenfield remediation latency
Brownfield completion time
worker failure rate
dashboard response time
maximum queue backlog
resource API error rate
```

Thresholds should be measurable and environment-specific.

---

## 61. Cost Validation

During scale tests, review actual billing for:

```text
Cloud Run
Cloud Tasks
Pub/Sub
Eventarc
Cloud Logging
BigQuery
Cloud Asset Inventory where applicable
```

Use current Google Cloud pricing and actual billing export data for production estimates.

---

## 62. Regression Tests

A change to one resource adapter must not break other supported resources.

Maintain regression coverage for:

```text
registry loading
dispatcher
compliance
existing supported adapters
Brownfield
Greenfield
BigQuery evidence
dashboard
authentication
```

---

## 63. Schema Migration Tests

Before changing BigQuery schema:

```text
1. Apply change in DEV
2. Test existing writes
3. Test existing reads
4. Test dashboard queries
5. Test historical rows
6. Test nullable/default behaviour
7. Verify rollback/migration strategy
```

Do not rename/remove production fields without consumer impact analysis.

---

## 64. Terraform Tests

Validate Terraform changes through:

```text
terraform fmt
terraform validate
terraform plan
reviewed DEV apply
post-apply functional validation
```

Production apply should use the approved reviewed configuration.

---

## 65. Terraform Drift Tests

Periodically compare Terraform-managed production configuration with actual infrastructure.

Review unexpected drift in:

```text
IAM
Cloud Run
Cloud Tasks
Pub/Sub
Eventarc
BigQuery
registry bucket
organisation sink
```

Emergency console changes must be reconciled.

---

## 66. CI Tests

CI should include applicable checks for:

```text
Python tests
registry validation
format/lint checks
Terraform validation
security scanning where available
build validation
```

A failed required validation should block promotion.

---

## 67. Container Tests

Before deployment:

```text
container builds successfully
application starts
required modules import
health endpoint works
no credentials embedded
runtime configuration loads
```

Test the exact image intended for promotion.

---

## 68. Deployment Smoke Test

After DEV deployment:

```text
[ ] Correct revision active
[ ] Health endpoint responds
[ ] Registry loads
[ ] BigQuery works
[ ] Cloud Tasks invokes worker
[ ] Eventarc invokes service
[ ] Dashboard loads
```

Only then continue to functional tests.

---

## 69. Production Smoke Test

After PROD deployment:

```text
[ ] Correct revision active
[ ] Authenticated health/dashboard access works
[ ] Unauthorised access rejected
[ ] PROD registry used
[ ] PROD BigQuery used
[ ] Controlled Brownfield test succeeds
[ ] Controlled Greenfield test succeeds if affected
[ ] No new error spike
```

Do not immediately start a full organisation Brownfield run after deployment.

---

## 70. Production Acceptance Test

For a release affecting remediation:

```text
1. Select approved low-risk workload project
2. Create/identify supported test resource
3. Verify registry mapping
4. Run controlled Brownfield or Greenfield test
5. Verify metadata
6. Verify BigQuery evidence
7. Verify dashboard
8. Review logs
9. Approve wider use
```

---

## 71. Test Evidence

For each supported resource, retain:

```text
resource type
test date
environment
test project
adapter version/revision
Brownfield result
Greenfield result
observed serviceName
observed methodName
IAM required
metadata before
metadata after
preservation result
BigQuery evidence
known limitations
reviewer
```

This is the basis for support claims.

---

## 72. Resource Support Promotion

A capability progresses:

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

Do not mark a capability `SUPPORTED` solely because unit tests pass.

---

## 73. Defect Classification

When a test fails, identify the layer:

```text
Registry
Discovery
Event routing
Parser
Classifier
Capability
Compliance
Planner
Cloud Tasks
Worker
Adapter
IAM
Native API
BigQuery
Dashboard
```

This prevents unrelated code changes.

---

## 74. Test Data Cleanup

After tests:

- remove temporary workload resources
- preserve required BigQuery test evidence according to policy
- remove temporary IAM changes
- remove temporary registry bindings
- ensure queues do not contain stale test tasks

Do not delete shared platform infrastructure as part of routine test cleanup.

---

## 75. Production Data Protection During Testing

Never use destructive test cases against client production resources without explicit approval.

Metadata tests should use controlled test resources/projects.

Production acceptance testing should be:

```text
small
reversible
observable
approved
```

---

## 76. Testing Anti-Patterns

Do not:

- test Greenfield only by manually POSTing fake payloads
- claim Greenfield support without a real Audit Log event
- claim Brownfield support without a real CAI-discovered resource
- test only in the governance project
- make Cloud Run public for testing
- grant Owner/Editor to make tests pass
- hardcode project IDs into production code
- use repository snapshots to fake dashboard success
- delete unrelated labels during remediation tests
- skip failure-path testing
- test the entire organisation first
- assume task delivery is exactly once
- assume all resource types use the same create event
- infer support from IAM permission names alone

---

## 77. Minimum Release Gate

A production release affecting governance behaviour must satisfy:

```text
[ ] Code validation passed
[ ] Registry validation passed
[ ] Terraform validation passed where applicable
[ ] Unit tests passed
[ ] DEV integration tests passed
[ ] Brownfield test passed if affected
[ ] Greenfield test passed if affected
[ ] IAM validated
[ ] BigQuery evidence validated
[ ] Dashboard validated if affected
[ ] Security checks passed
[ ] Rollback path understood
[ ] Production smoke-test plan prepared
```

---

## 78. Final End-to-End Acceptance

The complete platform acceptance path is:

```text
Application Registry
       |
       +-------------------------------+
       |                               |
       v                               v
Brownfield                         Greenfield
       |                               |
       v                               v
Cloud Asset Inventory             Audit Logs
       |                               |
       v                               v
Discovery                       Org Sink/PubSub
       |                               |
       v                               v
Compliance                        Eventarc
       |                               |
       +---------------+---------------+
                       |
                       v
                 Capability Gate
                       |
                       v
                 Resource Adapter
                       |
                       v
                 Native GCP API
                       |
                       v
                 BigQuery Evidence
                       |
                       v
                    Dashboard
```

Acceptance requires evidence that both the control flow and the actual target-resource metadata are correct.

---

## 79. Architecture Summary

Testing is capability-driven and evidence-based.

For Brownfield, the platform must prove:

```text
real resource
 -> CAI
 -> compliance
 -> plan
 -> task
 -> worker
 -> native API
 -> BigQuery
```

For Greenfield, it must prove:

```text
real resource creation
 -> real Audit Log
 -> organisation sink
 -> Pub/Sub
 -> Eventarc
 -> Cloud Run
 -> classifier
 -> adapter
 -> native API
 -> BigQuery
```

This prevents production support from being declared based on assumptions, mocked payloads or code presence alone.

---

## 80. Related Documentation

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

- `SUPPORTED_RESOURCES.md` for capability promotion.
- `GREENFIELD.md` for event-driven validation.
- `BROWNFIELD.md` for discovery/remediation validation.
- `IAM.md` and `SECURITY.md` for least-privilege testing.
- `DATA_MODEL.md` for evidence validation.
- `OPERATIONS.md` for production smoke tests and troubleshooting.
