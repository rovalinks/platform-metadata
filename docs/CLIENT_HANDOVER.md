# Enterprise Metadata Governance Platform - Client Handover

## 1. Purpose

This document defines the formal technical and operational handover of the Enterprise Metadata Governance Platform to the client.

It explains:

- what has been delivered
- how the architecture operates
- what the client owns
- how DEV and PROD are separated
- how to operate Brownfield and Greenfield governance
- how to manage the Application Registry
- how to onboard new applications and resource types
- how to troubleshoot the platform
- how to deploy safely
- what must be reviewed before enterprise-scale production operation

The platform uses two dedicated governance projects:

```text
DEV  -> platform-metadata-dev
PROD -> platform-metadata-prod
```

---

## 2. Platform Objective

The platform provides centralised metadata governance across Google Cloud resources.

It supports two complementary operating modes:

```text
GREENFIELD
Near-real-time governance of newly created supported resources

BROWNFIELD
Discovery, compliance evaluation and remediation of existing supported resources
```

The platform is designed to be:

```text
serverless
event-driven
configuration-driven
auditable
least-privilege
scalable
cost-conscious
```

---

## 3. High-Level Architecture

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

## 4. Delivered Environments

### Development

```text
platform-metadata-dev
```

Purpose:

```text
development
integration testing
new adapter validation
Greenfield event validation
IAM validation
registry validation
dashboard validation
scale testing
```

### Production

```text
platform-metadata-prod
```

Purpose:

```text
production governance
organisation event processing
production Brownfield remediation
production operational evidence
authorised dashboard access
```

---

## 5. Environment Separation

DEV and PROD must remain separate.

Do not intentionally share:

```text
runtime service accounts
registry buckets
BigQuery operational datasets
Cloud Tasks queues
environment configuration
production remediation identities
```

unless an explicitly approved architecture change requires it.

DEV must not unintentionally gain production remediation scope.

---

## 6. Delivered Core Components

The solution includes the following logical components:

```text
Cloud Run governance service
Cloud Tasks remediation queue
Cloud Asset Inventory discovery
Organisation Cloud Logging sink
Pub/Sub Greenfield event topic
Eventarc trigger
Application Registry
Resource adapters
Compliance engine
Remediation planner
BigQuery operational evidence
Dashboard
Terraform infrastructure
CI/CD integration
Technical documentation
```

---

## 7. Application Registry

The Application Registry is the source of approved application/project ownership metadata.

Conceptually:

```text
Application
   |
   +-- application metadata
   |
   +-- environment
   |
   +-- owner/governance metadata
   |
   +-- project bindings
```

The platform uses the registry to determine what managed metadata should be applied.

---

## 8. Registry Ownership

The client must assign ownership for:

```text
registry schema
application records
project bindings
owner values
environment values
production approvals
```

Platform Engineering should not invent application ownership when registry data is missing.

---

## 9. Adding a New Application

Recommended process:

```text
1. Create/update application registry YAML
2. Add correct project binding
3. Add required metadata
4. Run registry validation
5. Peer review
6. Publish to DEV
7. Validate project resolution
8. Validate controlled governance behaviour
9. Approve
10. Publish to PROD
```

Do not directly edit production registry data without validation.

---

## 10. Unbound Projects

If a workload project is not registered:

```text
do not guess application ownership
do not copy another project's metadata
do not silently assign defaults
```

The project should follow the approved unbound-project handling policy.

The client should periodically review unbound projects.

---

## 11. Greenfield Operation

Greenfield flow:

```text
New Resource
    |
    v
Cloud Audit Log
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
Classifier
    |
    v
Registry
    |
    v
Capability
    |
    v
Resource Adapter
    |
    v
Native GCP API
    |
    v
BigQuery Evidence
```

The design avoids continuous polling for newly created resources.

---

## 12. Greenfield Support Requirement

A resource type is not considered Greenfield-supported merely because an adapter exists.

Before production support:

```text
[ ] Real resource created
[ ] Real Cloud Audit Log captured
[ ] serviceName validated
[ ] methodName validated
[ ] Organisation sink validated
[ ] Pub/Sub validated
[ ] Eventarc validated
[ ] Cloud Run classifier validated
[ ] Adapter validated
[ ] Metadata update validated
[ ] BigQuery evidence validated
```

---

## 13. Brownfield Operation

Brownfield flow:

```text
Requested Scope
      |
      v
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
Resource Adapter
      |
      v
Native GCP API
      |
      v
remediation_execution
```

---

## 14. Brownfield Run Ownership

The client should define who is authorised to initiate large production Brownfield runs.

Before a broad run:

```text
[ ] Registry reviewed
[ ] Scope reviewed
[ ] Exclusions reviewed
[ ] Supported resources reviewed
[ ] API quotas reviewed
[ ] Monitoring active
[ ] Operators available
[ ] Emergency-stop procedure understood
```

---

## 15. Brownfield Run ID

Every run should be tracked using:

```text
run_id
```

Use `run_id` to correlate:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
Cloud Run logs
dashboard run reporting
```

The run ID should be captured immediately when a Brownfield run begins.

---

## 16. Brownfield Completion

Do not assume the initial API/orchestrator response means all remediation is complete.

Cloud Tasks processing is asynchronous.

Completion should be determined from:

```text
planned
queued
executed
successful
failed
remaining
```

and corresponding BigQuery evidence.

---

## 17. BigQuery Operational Evidence

The core data model is:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

These tables provide traceability across discovery, decision, planning and execution.

They are operational evidence and should not be replaced by static repository snapshots.

---

## 18. Dashboard

The dashboard provides an operational view of the platform.

Expected areas include:

```text
Executive Summary
Compliance
Resource Distribution
Brownfield Runs
Greenfield Activity
Recent Remediation
Failures
```

The dashboard should use backend/BigQuery operational data.

---

## 19. Dashboard Access

Dashboard access must be restricted to approved authenticated organisation users.

Dashboard users should not automatically receive:

```text
runtime remediation IAM
Cloud Tasks administration
registry write access
direct privileged BigQuery access
service-account impersonation
```

Viewer access and runtime privileges must remain separate.

---

## 20. Runtime Identity

Cloud Run uses a dedicated runtime service account.

It should have only permissions required for:

```text
registry reads
BigQuery operations
resource discovery where applicable
supported resource reads
supported metadata mutations
```

Do not grant Owner or Editor as a runtime shortcut.

---

## 21. Service Identities

The client should understand that the platform uses different identities for different purposes:

```text
Cloud Run runtime identity
Cloud Tasks invocation identity
Eventarc delivery identity
Logging sink writer identity
CI/CD deployment identity
Registry publisher identity
```

These identities should not be merged without architectural review.

---

## 22. Supported Resource Catalogue

The repository contains the supported-resource/capability documentation.

A capability should progress through:

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

Only validated capabilities should be enabled broadly in production.

---

## 23. Resource Permission Catalogue

The implementation has considered resource mutation permissions including:

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

The final production IAM role must contain only permissions justified by enabled capabilities.

---

## 24. Adding a New Resource Type

Do not add a resource type only by adding an IAM permission.

Required workflow:

```text
1. Confirm metadata/label support in official Google Cloud documentation
2. Confirm CAI asset type
3. Confirm native read API
4. Confirm native update API
5. Implement adapter
6. Add dispatcher/capability mapping
7. Validate read IAM
8. Validate mutation IAM
9. Test Brownfield
10. Create real resource
11. Capture real Audit Log
12. Add Greenfield mapping if supported
13. Test full Greenfield path
14. Verify BigQuery evidence
15. Update documentation
16. Promote capability status
```

---

## 25. Unsupported Resources

If a resource does not support the required metadata model, it should remain unsupported.

Do not create fake support through unrelated metadata mechanisms.

API Keys were previously excluded because the required label capability was not available for this platform.

---

## 26. Metadata Safety

Adapters must preserve unrelated labels/metadata.

Conceptually:

```text
existing metadata
      +
managed governance metadata
      =
final metadata
```

The platform should manage only its approved keys.

---

## 27. Fingerprints and ETags

Some Google Cloud APIs require concurrency tokens.

Where applicable:

```text
read current resource
obtain current fingerprint/ETag
merge metadata
update
```

Do not reuse stale discovery-time tokens.

---

## 28. Exclusions

Production exclusions are configuration-driven.

Examples include:

```text
EXCLUDED_PROJECTS
EXCLUDED_BUCKETS
```

The client should review exclusions before large Brownfield runs.

Control-plane resources must be protected where required.

---

## 29. Governance Control Plane

Particular care should be taken with resources inside:

```text
platform-metadata-prod
```

because the platform can potentially support resource types used by its own infrastructure.

Examples:

```text
Cloud Run
Pub/Sub
Eventarc
Cloud Storage
BigQuery
```

Self-remediation behaviour must be explicitly controlled.

---

## 30. Deployment Process

Recommended deployment flow:

```text
Code / Terraform / Registry Change
          |
          v
Review
          |
          v
platform-metadata-dev
          |
          v
Validation
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
Smoke Test
```

Production should never be the first validation environment.

---

## 31. CI/CD

Where GitHub Actions is used, the preferred authentication model is Workload Identity Federation.

Avoid long-lived service-account JSON keys.

The deployment identity should be restricted to the approved repository/workflow context and required deployment permissions.

---

## 32. Terraform

Terraform should remain the authoritative definition for managed infrastructure where practical.

Before production changes:

```text
terraform fmt
terraform validate
terraform plan
review
DEV apply
functional validation
PROD approval
PROD apply
```

Manual emergency changes should be reconciled back into Terraform.

---

## 33. Routine Daily Operations

Recommended checks:

```text
Cloud Run health
Cloud Tasks backlog
Greenfield failures
BigQuery write failures
registry load failures
IAM-denied spikes
remediation failure rate
dashboard freshness
```

Detailed procedures are documented in `OPERATIONS.md`.

---

## 34. Greenfield Troubleshooting

Use this order:

```text
1. Workload Audit Log
2. serviceName/methodName
3. Organisation sink
4. Sink writer IAM
5. Pub/Sub
6. Eventarc
7. Cloud Run
8. Classifier
9. Capability
10. Registry
11. Adapter
12. Native API/IAM
13. BigQuery evidence
```

Do not begin by changing adapter code when the event never reached Cloud Run.

---

## 35. Brownfield Troubleshooting

Use:

```text
1. Capture run_id
2. Check resource_snapshot
3. Check compliance_snapshot
4. Check remediation_plan
5. Check Cloud Tasks
6. Check /worker logs
7. Check adapter
8. Check exact IAM error
9. Check target API
10. Check remediation_execution
11. Check dashboard/API
```

---

## 36. IAM Troubleshooting

For `PERMISSION_DENIED`:

```text
1. Identify caller service account
2. Identify target project/resource
3. Capture exact denied permission
4. Confirm capability requires it
5. Validate permission in DEV
6. Update approved custom role if justified
7. Promote through change control
```

Do not grant Owner or Editor to solve individual adapter failures.

---

## 37. Emergency Stop

The client operations team must know how to stop incorrect processing.

### Brownfield

```text
stop new runs
pause controlled task dispatch if required
preserve queued/in-flight evidence
identify run_id
correct issue
validate in DEV
resume after approval
```

### Greenfield

```text
stop/disable affected capability or event path
preserve evidence
identify affected events/resources
correct issue
validate in DEV
re-enable after approval
```

---

## 38. Rollback

Rollback considerations include:

```text
Cloud Run revision rollback
Terraform rollback/correction
registry rollback
IAM correction
capability disablement
dashboard rollback
BigQuery schema migration/rollback
```

Reverting code or registry configuration does not automatically undo metadata already applied to workload resources.

---

## 39. Monitoring Ownership

The client should assign owners for:

```text
Cloud Run alerts
Cloud Tasks backlog
Greenfield pipeline
BigQuery failures
IAM failures
registry failures
cost anomalies
security alerts
```

Every production alert should have an owner and runbook.

---

## 40. Cost Management

The architecture is serverless and consumption-based.

Primary cost components include:

```text
Cloud Run
Cloud Tasks
Pub/Sub
Eventarc
Cloud Logging
BigQuery
Cloud Asset Inventory where applicable
```

See `COST_MODEL.md` for the detailed cost framework.

Do not use the earlier POC cost estimate as a guaranteed production financial statement.

---

## 41. Scale Management

For large Brownfield estates, tune:

```text
REMEDIATION_BATCH_SIZE
MAX_PARALLEL_WORKERS
Cloud Tasks dispatch
Cloud Run scaling
```

against:

```text
target API quotas
worker duration
failure rate
memory
cost
```

Do not tune only for maximum speed.

---

## 42. One-Million-Resource Operation

For estates approaching 1,000,000 resources:

```text
[ ] Measure CAI discovery
[ ] Measure compliance ratio
[ ] Measure task/batch count
[ ] Measure worker throughput
[ ] Measure target API quotas
[ ] Measure BigQuery growth
[ ] Measure retry rate
[ ] Measure actual cost
```

Enterprise estimates should come from measured representative workloads.

---

## 43. Security Responsibilities

The client should periodically review:

```text
runtime IAM
Cloud Run Invoker
Cloud Tasks caller
Eventarc identity
Logging sink writer
registry bucket IAM
BigQuery IAM
CI/CD identity
WIF trust
Terraform state access
```

Remove obsolete access.

---

## 44. Secrets

Do not store secrets in:

```text
registry YAML
source code
Terraform committed variables
dashboard JavaScript
BigQuery evidence
logs
```

Use approved secrets-management services when secrets are actually required.

---

## 45. Documentation Delivered

The technical documentation set consists of:

```text
README.md
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
├── PRODUCTION_READINESS.md
├── COST_MODEL.md
└── CLIENT_HANDOVER.md
```

These documents should be maintained with the implementation.

---

## 46. Client Ownership After Handover

Recommended ownership:

| Area | Primary Owner |
| --- | --- |
| Platform source | Platform Engineering |
| Terraform | Cloud Platform Engineering |
| Application Registry | Application Governance / nominated owner |
| Runtime IAM | Cloud Security / Platform Engineering |
| Production deployment | Platform Engineering |
| Greenfield event pipeline | Platform Engineering |
| BigQuery operational evidence | Platform Engineering |
| Dashboard access | Platform/Security administration |
| Cost review | FinOps / Platform Engineering |
| Incident response | Client Cloud Operations |
| Resource capability approval | Platform Architecture / Security |

The client may adapt these roles to its operating model.

---

## 47. Knowledge Transfer Checklist

Before final handover:

```text
[ ] Architecture walkthrough completed
[ ] Repository walkthrough completed
[ ] Terraform walkthrough completed
[ ] Registry update demonstrated
[ ] Brownfield run demonstrated
[ ] run_id troubleshooting demonstrated
[ ] Greenfield troubleshooting demonstrated
[ ] Dashboard access demonstrated
[ ] IAM model explained
[ ] New resource onboarding explained
[ ] Emergency stop demonstrated/explained
[ ] Rollback explained
[ ] Cost model explained
[ ] Production readiness checklist reviewed
```

---

## 48. Access Handover Checklist

Verify the client has approved access to:

```text
source repository
CI/CD workflows
DEV project
PROD project
Terraform backend
registry administration path
Cloud Run operational logs
BigQuery operational data
monitoring/alerts
billing/cost reporting where required
```

Do not share credentials manually when access can be granted through IAM.

---

## 49. Production Handover Checklist

```text
[ ] PROD project confirmed
[ ] Correct production revision confirmed
[ ] Runtime identity confirmed
[ ] Registry validated
[ ] Supported-resource matrix reviewed
[ ] Organisation sink confirmed
[ ] Pub/Sub confirmed
[ ] Eventarc confirmed
[ ] Cloud Tasks confirmed
[ ] BigQuery confirmed
[ ] Dashboard confirmed
[ ] Monitoring confirmed
[ ] Alerts confirmed
[ ] Exclusions confirmed
[ ] Controlled Brownfield test completed
[ ] Controlled Greenfield test completed for enabled capabilities
```

---

## 50. Known Limitations

Known limitations should be maintained explicitly rather than hidden.

Examples may include:

```text
resource types not yet validated
Greenfield methods not yet validated
service-specific metadata limitations
quota constraints
dashboard reporting limitations
unsupported APIs
```

Update `SUPPORTED_RESOURCES.md` whenever capability status changes.

---

## 51. Future Enhancement Process

Future enhancements should follow:

```text
Requirement
   |
   v
Architecture Review
   |
   v
Official GCP Capability Validation
   |
   v
DEV Implementation
   |
   v
Testing
   |
   v
Security/IAM Review
   |
   v
Documentation
   |
   v
PROD Approval
```

Avoid one-off production special cases.

---

## 52. Handover Acceptance Record

```text
Platform:
Enterprise Metadata Governance Platform

DEV Project:
platform-metadata-dev

PROD Project:
platform-metadata-prod

Repository:
____________________________

Application Release:
____________________________

Terraform Release:
____________________________

Registry Version:
____________________________

Handover Date:
____________________________

Architecture Walkthrough:
COMPLETE / PENDING

Operations Walkthrough:
COMPLETE / PENDING

Security/IAM Walkthrough:
COMPLETE / PENDING

Brownfield Demonstration:
COMPLETE / PENDING

Greenfield Demonstration:
COMPLETE / PENDING

Dashboard Demonstration:
COMPLETE / PENDING

Documentation Review:
COMPLETE / PENDING

Known Exceptions:
____________________________
____________________________

Handed Over By:
____________________________

Accepted By:
____________________________

Client Approval:
____________________________
```

---

## 53. Final Handover Position

The client receives a centralised Google Cloud metadata governance platform with:

```text
Application Registry-driven desired state
Brownfield discovery and remediation
Greenfield event-driven remediation
capability-based resource adapters
asynchronous Cloud Tasks execution
BigQuery audit evidence
authenticated operational dashboard
Terraform-managed infrastructure
DEV/PROD separation
least-privilege security model
production runbooks and testing guidance
cost and scale framework
```

The architecture is designed to remain serverless and consumption-based, with no requirement for continuously running governance worker infrastructure.

The platform should continue to evolve through validated capabilities rather than hardcoded client-specific logic.

---

## 54. Related Documentation

For detailed information, refer to:

```text
ARCHITECTURE.md            -> system architecture
DEPLOYMENT.md              -> deployment
IAM.md                     -> permissions and identities
GREENFIELD.md              -> event-driven governance
BROWNFIELD.md              -> existing-resource governance
APPLICATION_REGISTRY.md    -> desired-state registry
SUPPORTED_RESOURCES.md     -> capability catalogue
API.md                     -> application endpoints
DATA_MODEL.md              -> BigQuery evidence
OPERATIONS.md              -> operational runbooks
SECURITY.md                -> security architecture
TESTING.md                 -> validation strategy
PRODUCTION_READINESS.md    -> go-live gate
COST_MODEL.md              -> cost framework
CLIENT_HANDOVER.md         -> client transition and ownership
```
