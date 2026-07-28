# Enterprise Metadata Governance Platform - Security

## 1. Purpose

This document defines the security architecture and production security controls for the Enterprise Metadata Governance Platform on Google Cloud.

The platform operates from two dedicated governance projects:

```text
DEV  -> platform-metadata-dev
PROD -> platform-metadata-prod
```

The security model covers:

- organisation-level governance
- Cloud Run
- Cloud Tasks
- Cloud Logging
- Pub/Sub
- Eventarc
- Cloud Asset Inventory
- BigQuery
- Application Registry
- resource remediation IAM
- dashboard access
- service identities
- secrets and configuration
- auditability
- DEV/PROD separation

The primary security principle is:

```text
Centralised governance
+
least privilege
+
authenticated service-to-service access
+
explicit resource capabilities
+
auditable execution
```

---

## 2. Security Objectives

The platform must:

```text
[ ] Prevent unauthorised dashboard access
[ ] Prevent anonymous remediation invocation
[ ] Prevent unauthorised worker invocation
[ ] Prevent arbitrary application metadata injection
[ ] Minimise organisation-level permissions
[ ] Restrict mutation permissions to supported resources
[ ] Protect governance control-plane resources
[ ] Keep DEV and PROD isolated
[ ] Preserve audit evidence
[ ] Prevent secrets from entering governance metadata/logs
[ ] Avoid hardcoded credentials and client-specific identities
```

---

## 3. Trust Boundaries

The architecture contains several distinct trust boundaries.

```text
GCP Organisation
      |
      +-- Workload Projects
      |       |
      |       +-- governed resources
      |
      +-- platform-metadata-prod
              |
              +-- Cloud Run
              +-- Cloud Tasks
              +-- Pub/Sub
              +-- Eventarc
              +-- BigQuery
              +-- Registry
```

The governance project is a control plane.

Workload projects remain separate resource planes.

---

## 4. Identity Model

Different operations must use dedicated identities where appropriate.

Logical identities include:

```text
Governance runtime service account
Cloud Tasks invocation identity
Eventarc delivery identity
Logging sink writer identity
CI/CD deployment identity
Dashboard user identity
Registry publisher identity
```

Do not collapse all platform operations into one broadly privileged service account merely for convenience.

---

## 5. Runtime Service Account

The Cloud Run governance service must use a dedicated runtime service account.

Its responsibilities include only the permissions required for:

- registry reads
- BigQuery operational access
- discovery where applicable
- supported resource reads
- supported resource metadata remediation
- other explicitly implemented runtime dependencies

It must not receive general-purpose administrator permissions.

---

## 6. No Owner or Editor

The runtime must not rely on:

```text
roles/owner
roles/editor
```

for production operation.

If an adapter fails with `PERMISSION_DENIED`, identify the exact required permission and update the approved least-privilege role only when justified.

Broad predefined administrative roles are not an acceptable permanent fix.

---

## 7. Organisation-Level Access

Organisation-level governance does not mean organisation-level unrestricted administration.

Organisation permissions should be limited to the operations required for:

```text
resource discovery
project visibility
event routing configuration where applicable
```

Resource mutation permissions should be granted according to the approved governance model and supported-resource catalogue.

---

## 8. Resource Mutation Permissions

The candidate mutation permission catalogue includes:

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

This is not permission to blindly include every entry in the final production role.

Only permissions required by enabled, validated production capabilities should remain.

---

## 9. Read Permissions

Many metadata updates require current resource state.

Examples include:

```text
current labels
fingerprint
ETag
resource location
current configuration
```

The security design must therefore account for both:

```text
read permission
+
mutation permission
```

for each enabled adapter.

The exact permission set should be documented in `IAM.md` and `SUPPORTED_RESOURCES.md`.

---

## 10. Capability-Driven IAM

IAM should follow platform capabilities.

```text
Supported Resource
       |
       v
Required Read API
       |
       v
Required Mutation API
       |
       v
Minimum IAM
```

If a resource capability is removed permanently, review whether its permissions can also be removed.

This prevents privilege accumulation.

---

## 11. Cloud Run Authentication

Production Cloud Run must be authenticated.

Do not grant:

```text
allUsers
```

the Cloud Run Invoker role.

Cloud Run access should be granted only to approved callers.

---

## 12. Dashboard Access

The dashboard should be accessible only to authorised organisation users.

A dashboard user requires permission to invoke/view the dashboard application.

A dashboard user does not automatically require:

```text
BigQuery direct access
Cloud Tasks access
Pub/Sub access
Registry bucket access
resource remediation permissions
runtime service-account impersonation
```

The backend should perform authorised operational queries.

---

## 13. Dashboard Authorisation

Authentication answers:

```text
Who is the caller?
```

Authorisation answers:

```text
Is this caller allowed to use this dashboard/API?
```

Production access should use an approved organisation identity/group model.

Prefer group-based access where practical rather than maintaining large lists of individual users.

---

## 14. Internal Endpoints

Internal processing endpoints such as:

```text
/worker
Greenfield event intake
```

must not become anonymously accessible simply because they use HTTP.

Their caller identity must be validated through Cloud Run IAM and the corresponding Google Cloud service integration.

---

## 15. Cloud Tasks Security

Cloud Tasks invokes:

```text
/worker
```

using authenticated service-to-service invocation.

The task should use an approved OIDC identity.

The invocation identity needs Cloud Run Invoker on the governance service but does not need the runtime service account's resource-remediation permissions.

Separate:

```text
permission to invoke worker
```

from:

```text
permission used by worker to modify GCP resources
```

---

## 16. Eventarc Security

Eventarc delivers Greenfield Pub/Sub events to Cloud Run using its configured identity.

The Eventarc delivery identity requires the minimum invocation permissions needed by the trigger.

It does not require broad resource-remediation IAM.

The Cloud Run runtime identity performs the application operation after the event is accepted.

---

## 17. Logging Sink Writer Identity

The organisation Logging sink has its own writer identity.

Its responsibility is:

```text
publish matching exported logs
```

to the central Pub/Sub destination.

It should receive:

```text
roles/pubsub.publisher
```

on the required topic.

It does not require Cloud Run Invoker or resource-remediation permissions.

---

## 18. Pub/Sub Security

The central Greenfield topic:

```text
metadata-governance-events
```

is platform transport infrastructure.

Access should be limited to:

```text
Logging sink writer -> publish
Eventarc/platform integration -> consume as required
approved platform administrators -> manage
```

Do not grant broad organisation users publish permissions unless there is a documented requirement.

---

## 19. Event Injection Risk

The application must not trust a message solely because it structurally resembles an Audit Log.

Controls include:

```text
authenticated Eventarc delivery
expected Pub/Sub source
event envelope validation
serviceName/methodName classification
capability validation
registry binding
resource lookup
```

A received event does not bypass the governance decision path.

---

## 20. Application Registry Security

The Application Registry controls ownership and required metadata.

An unauthorised registry modification could alter metadata applied across many resources.

The production registry must therefore be treated as security-sensitive configuration.

---

## 21. Registry Bucket Controls

Production registry storage should use:

```text
uniform_bucket_level_access = true
force_destroy = false
```

and should not be publicly accessible.

Logical permissions:

```text
Runtime
    -> read

Approved registry publisher
    -> write

General dashboard users
    -> no direct access required
```

---

## 22. Registry Change Control

Production registry changes should require:

```text
source control
schema validation
peer review
DEV validation
impact assessment
production approval
```

Direct unmanaged modification of production registry objects should be avoided.

---

## 23. Registry Data Restrictions

Registry YAML must not contain:

```text
passwords
API tokens
service-account private keys
OAuth refresh tokens
database credentials
secret payloads
```

The registry is metadata configuration, not a secrets store.

---

## 24. Secret Manager

If the platform requires secrets, use an approved secrets-management mechanism such as Secret Manager.

The Cloud Run runtime should receive only the secrets it actually requires.

Secret values should not be:

- embedded in container images
- committed to Git
- written to BigQuery
- logged
- placed in dashboard JavaScript

---

## 25. Secret Manager Governance Target

The platform may govern metadata on Secret Manager Secret resources where that capability is validated.

Candidate permission:

```text
secretmanager.secrets.update
```

This does not justify access to secret payload versions.

Metadata governance must not read secret values.

---

## 26. Environment Configuration

Non-secret environment-specific values can be supplied through Terraform/Cloud Run configuration.

Examples include:

```text
governance project ID
dataset ID
registry bucket
queue name
topic name
organisation scope
cache TTL
batch size
parallelism
exclusions
```

Do not duplicate these values as constants throughout Python or JavaScript.

---

## 27. No Hardcoded Credentials

Never place:

```text
service-account JSON keys
access tokens
refresh tokens
private keys
passwords
```

inside:

```text
Python files
Terraform variables committed to source
dashboard.js
HTML
Docker image layers
registry YAML
README examples
```

Use workload identity and Google-managed service identities wherever possible.

---

## 28. Service Account Keys

Long-lived service-account keys should not be required for normal runtime operation.

Cloud Run, Cloud Tasks and Eventarc support identity-based authentication without embedding private service-account keys in the application.

If a key exists unnecessarily, plan controlled removal after confirming no valid dependency remains.

---

## 29. CI/CD Authentication

CI/CD should use short-lived identity federation where supported rather than stored long-lived Google Cloud keys.

For GitHub-based deployment, Workload Identity Federation is preferred over committing or storing reusable service-account JSON keys.

Repository/provider conditions must restrict which workflow/repository identity can impersonate the deployment account.

---

## 30. CI/CD Deployment Identity

The deployment identity is separate from the runtime identity.

Deployment may require permissions for:

```text
Cloud Run deployment
Terraform-managed resources
Artifact Registry
IAM changes approved for deployment
```

It should not automatically inherit runtime organisation-wide remediation permissions unless explicitly necessary.

---

## 31. DEV and PROD Separation

The platform uses:

```text
platform-metadata-dev
platform-metadata-prod
```

They must have separate:

```text
Cloud Run services/revisions
service accounts
registry storage
BigQuery datasets
Cloud Tasks queues
Pub/Sub resources
Eventarc configuration
environment configuration
```

where applicable.

---

## 32. DEV Must Not Control PROD Accidentally

DEV configuration must not contain production mutation scope unless explicitly required for an approved test.

Controls should prevent:

```text
DEV runtime
    -> accidental production workload remediation
```

Production organisation-level permissions must be granted only to the intended PROD runtime identity.

---

## 33. Workload Project Security

The governance platform modifies only approved metadata on workload resources.

It must not alter unrelated configuration such as:

```text
VM machine type
networking
storage contents
database data
KMS key material
secret payload
Cloud Run container image
GKE workload configuration
```

unless a separate explicitly approved governance feature is designed.

---

## 34. Metadata Preservation

Adapters must preserve metadata outside the managed governance keys.

Conceptually:

```text
existing labels
      +
required managed labels
      =
safe merged result
```

Do not replace the entire label set with only governance labels unless the underlying API semantics and approved policy explicitly require it.

---

## 35. Concurrency Protection

For APIs using fingerprints or ETags:

```text
read current state
      |
      v
obtain current concurrency token
      |
      v
merge metadata
      |
      v
update
```

This reduces the risk of overwriting concurrent legitimate changes.

---

## 36. Exclusion Controls

Control-plane and exempt resources must be protected through explicit configuration.

Examples include:

```text
EXCLUDED_PROJECTS
EXCLUDED_BUCKETS
```

Potential protected assets include:

- governance registry bucket
- governance Cloud Run service
- governance event topic
- governance Eventarc trigger
- dedicated platform projects where required
- client-approved exemptions

Do not scatter exclusion names across adapters.

---

## 37. Self-Remediation Risk

Because the platform can support resource types such as:

```text
Cloud Run
Pub/Sub
Eventarc
BigQuery
Cloud Storage
```

it could potentially discover its own control-plane resources.

Production configuration must explicitly decide which governance resources are excluded.

The platform must not accidentally modify infrastructure required for its own operation.

---

## 38. BigQuery Security

BigQuery stores operational governance evidence.

Runtime permissions should be limited to required dataset/table operations.

Dashboard users should normally consume data through the authenticated backend rather than receive broad direct dataset access.

---

## 39. BigQuery Data Restrictions

Do not store:

```text
secret payloads
credentials
tokens
private keys
unnecessary confidential request bodies
```

Operational tables should contain governance metadata and execution evidence only.

---

## 40. BigQuery Environment Isolation

DEV dashboard/API must use DEV evidence.

PROD dashboard/API must use PROD evidence.

Do not combine environments into one operational table without an explicitly designed and secured multi-environment reporting architecture.

---

## 41. Audit Logging

Security-relevant operations should be auditable through:

```text
Cloud Audit Logs
Cloud Run structured logs
BigQuery remediation evidence
Git/source-control history
Terraform history
CI/CD deployment history
registry change history
```

No single log source should be expected to answer every forensic question.

---

## 42. Execution Evidence

`remediation_execution` should record sufficient context to determine:

```text
what resource
which project
which execution mode
what operation
when
success/failure
error where applicable
```

This provides an application-level audit trail in addition to Google Cloud Audit Logs.

---

## 43. Logging Sensitive Data

Logs must not intentionally contain:

```text
ID tokens
OAuth tokens
service-account private keys
secret payloads
passwords
full sensitive headers
```

Exception stack traces should be reviewed to ensure sensitive values are not included.

---

## 44. Error Responses

Browser/API error responses must not expose:

```text
Python stack traces
internal credentials
environment secrets
raw tokens
sensitive configuration
```

Return structured operational error information instead.

---

## 45. Dashboard Browser Security

Browser JavaScript must not contain privileged Google Cloud credentials.

The browser should communicate with the authenticated backend.

Do not embed:

```text
service-account keys
BigQuery credentials
Cloud Tasks credentials
registry credentials
```

in `dashboard.js`.

---

## 46. CORS

If dashboard and API share the same origin, broad CORS is unnecessary.

Do not configure:

```text
Access-Control-Allow-Origin: *
```

without a documented cross-origin requirement.

If a separate front end is introduced, restrict origins to approved domains.

---

## 47. Content Security Policy

For a production web dashboard, consider an appropriate Content Security Policy to reduce browser-side injection risk.

The exact policy must match the dashboard's actual asset loading model.

Avoid adding unsafe directives merely to make a broken script load.

---

## 48. Dependency Security

Python, container and JavaScript dependencies should be:

- explicitly declared
- version-managed
- reviewed
- updated through controlled testing
- scanned by the organisation's approved security tooling where available

Do not upgrade production dependencies without DEV validation.

---

## 49. Container Security

The Cloud Run container should:

```text
[ ] Contain only required runtime files
[ ] Avoid embedded credentials
[ ] Use maintained base images
[ ] Minimise unnecessary packages
[ ] Be rebuilt for security updates
[ ] Be stored in approved Artifact Registry
```

Where practical, run as a non-root user if compatible with the application and base image.

---

## 50. Artifact Registry Security

Only approved build/deployment identities should push production images.

Runtime consumers should have only the access required by Cloud Run deployment/execution.

Do not allow general dashboard users to publish container images.

---

## 51. Cloud Tasks Payload Security

Task payloads should contain only information necessary for remediation.

Do not place credentials or secret payloads in task bodies.

Resource metadata in tasks should be treated as internal governance data.

---

## 52. Pub/Sub Payload Security

The Greenfield Pub/Sub topic carries exported Audit Log events.

Access to the topic should therefore be restricted.

Do not expose the topic publicly or grant unnecessary subscriber access.

---

## 53. Organisation Sink Scope

The Logging sink should export only events required for supported Greenfield governance.

Overly broad logging export can increase:

- unnecessary data exposure
- Pub/Sub traffic
- processing noise
- cost
- attack surface

Filters should be based on validated event requirements.

---

## 54. Event Filtering

A broad expression such as matching every method containing `create` or `insert` should not be treated as the final security boundary.

Application classification and capability validation remain mandatory.

Defence in depth:

```text
Sink filter
    |
    v
Eventarc source
    |
    v
Cloud Run IAM
    |
    v
Event validation
    |
    v
Classifier
    |
    v
Capability gate
```

---

## 55. Cloud Asset Inventory Security

Brownfield discovery requires visibility into organisation resources.

Discovery permissions must be read-oriented.

Cloud Asset Inventory visibility does not itself justify mutation permissions.

Separate:

```text
ability to discover
```

from:

```text
ability to modify
```

---

## 56. Brownfield Safety

Organisation-wide Brownfield runs can affect large numbers of resources.

Security controls include:

```text
scope validation
registry validation
capability gate
exclusions
dry-run where configured
remediation planning
batching
rate control
least-privilege adapters
execution evidence
```

Do not bypass planning for convenience during production bulk remediation.

---

## 57. Greenfield Safety

Greenfield is automated and near real-time.

Controls include:

```text
validated creation event
authenticated Eventarc delivery
classifier
capability gate
registry binding
current-state read
safe metadata merge
bounded retry
BigQuery evidence
```

No single incoming event should be sufficient to bypass these controls.

---

## 58. Application Ownership Integrity

Project-to-application binding is security-sensitive.

The platform must not infer ownership from untrusted resource labels.

Ownership should come from the approved Application Registry.

A workload resource cannot self-declare a different application and thereby cause the platform to apply another application's metadata.

---

## 59. Unbound Projects

If a project is not in the registry:

```text
do not guess
do not inherit another project mapping
do not apply arbitrary metadata
```

Follow the approved unbound-project policy and report the condition.

---

## 60. Unsupported Resources

Unsupported resource types must be skipped.

Do not repeatedly call mutation APIs that do not support the required metadata model.

For example, API Keys were excluded when the required label capability was not available for this platform.

---

## 61. Denial of Service and Rate Protection

The serverless design can scale automatically, but scaling must remain controlled.

Controls include:

```text
Cloud Run max instances
Cloud Tasks queue rate
batch size
MAX_PARALLEL_WORKERS
request validation
authenticated invocation
bounded payloads
```

Automatic scaling is not a substitute for rate governance.

---

## 62. Quota Protection

Large Brownfield remediation can consume target service API quotas.

Cloud Tasks and worker concurrency should be configured to prevent accidental API saturation.

Quotas should be reviewed per target service before large production runs.

---

## 63. Replay Protection and Idempotency

Cloud Tasks and event systems can redeliver.

The platform should converge safely by reading current state before mutation where required.

A replay must not repeatedly corrupt or append duplicate metadata.

BigQuery reporting should account for retries when calculating unique-resource metrics.

---

## 64. Change Management

Security-impacting changes include:

```text
IAM permissions
service-account changes
organisation sink filters
Eventarc identities
Cloud Run authentication
registry schema
registry ownership values
supported-resource capabilities
new adapters
new APIs
new secrets
BigQuery access
dashboard authentication
```

These changes require DEV validation and controlled production promotion.

---

## 65. Terraform Security

Security-sensitive infrastructure should be managed through Terraform where practical.

Benefits include:

```text
reviewable changes
repeatability
DEV/PROD consistency
drift visibility
auditable configuration
```

Avoid undocumented console-only production IAM changes.

Emergency changes should be reconciled back into Terraform.

---

## 66. Terraform State

Terraform state can contain sensitive infrastructure information.

Store state in an approved secured backend with restricted access.

Do not commit Terraform state files to source control.

Access to production Terraform state should be more restricted than ordinary repository read access.

---

## 67. Source Repository Security

Repository controls should include:

```text
protected production branches
peer review
CI validation
secret scanning where available
restricted deployment workflows
auditable merges
```

Application code, Terraform and registry changes can all affect production governance.

---

## 68. Workload Identity Federation

Where GitHub Actions is used, Workload Identity Federation should restrict trust to the approved repository/workflow context.

Do not create a federation rule broad enough for unrelated repositories to impersonate the production deployment identity.

---

## 69. Production Access Reviews

Periodically review:

```text
Cloud Run Invoker members
runtime service-account roles
deployment identity roles
registry bucket access
BigQuery dataset access
Pub/Sub IAM
Cloud Tasks IAM
Eventarc identity
organisation-level grants
Terraform state access
```

Remove obsolete access.

---

## 70. Separation of Duties

Where client governance requires it, separate:

```text
code author
code approver
registry owner
production deployer
IAM administrator
security reviewer
dashboard viewer
```

The exact model depends on the client's operating organisation.

---

## 71. Break-Glass Access

If the client uses break-glass administrative access:

- keep it separate from normal runtime identities
- require strong authentication
- monitor its use
- record justification
- remove temporary grants promptly

The governance service should never run routinely using a break-glass identity.

---

## 72. Incident Response - Suspected Incorrect Remediation

If the platform is applying incorrect metadata:

```text
1. Stop the affected execution path
2. Preserve logs and BigQuery evidence
3. Identify run_id/execution_mode
4. Identify affected projects/resources
5. Verify registry version
6. Verify capability configuration
7. Verify deployed Cloud Run revision
8. Verify runtime identity
9. Correct in DEV
10. Reconcile affected resources safely
```

Do not delete evidence during the incident.

---

## 73. Incident Response - Suspected Credential Exposure

If a credential or token is exposed:

```text
1. Identify credential type
2. Disable/revoke/rotate as appropriate
3. Identify where it was exposed
4. Review access logs
5. Remove exposed material
6. Replace with identity-based authentication where possible
7. Review related permissions
8. document incident
```

Long-lived service-account keys should receive particular scrutiny.

---

## 74. Incident Response - Registry Compromise

If unauthorised registry modification is suspected:

```text
1. Stop broad remediation
2. Restrict registry write access
3. Preserve object/audit history
4. Identify changed entries
5. Restore known-good validated registry
6. Account for cache TTL
7. Identify affected executions
8. Reconcile affected resources
9. review publisher IAM
```

---

## 75. Security Monitoring

Consider monitoring for:

```text
unexpected Cloud Run Invoker changes
unexpected runtime IAM changes
registry access denied
registry write activity
organisation sink changes
Pub/Sub IAM changes
Eventarc trigger changes
Cloud Run authentication changes
remediation PERMISSION_DENIED spikes
unusual remediation volume
unexpected project scope
```

Alert thresholds should reflect the client's security baseline.

---

## 76. Security Evidence

For production review, retain evidence of:

```text
IAM role definitions
service-account assignments
Cloud Run IAM
registry bucket IAM
Pub/Sub IAM
organisation sink configuration
Eventarc identity
BigQuery IAM
WIF configuration
capability matrix
DEV validation
production approval
```

This supports architecture review and audit.

---

## 77. Security Anti-Patterns

Do not:

- grant Owner or Editor to the runtime
- expose Cloud Run to `allUsers`
- expose `/worker` anonymously
- put service-account keys in source control
- put secrets in registry YAML
- put privileged credentials in dashboard JavaScript
- allow DEV runtime to mutate PROD unintentionally
- use one service account for every trust boundary
- trust event payloads without classification
- grant mutation IAM solely because CAI can discover a resource
- overwrite unrelated labels
- hardcode client project IDs in adapters
- directly edit PROD registry without validation
- broaden organisation sink filters without need
- hide security failures from operational evidence

---

## 78. Production Security Checklist

### Identity

```text
[ ] Dedicated PROD runtime service account
[ ] Dedicated deployment identity
[ ] Eventarc identity reviewed
[ ] Cloud Tasks invocation identity reviewed
[ ] Logging sink writer identity reviewed
[ ] No unnecessary service-account keys
```

### Cloud Run

```text
[ ] Authentication required
[ ] No allUsers Invoker
[ ] Dashboard users explicitly authorised
[ ] Internal callers explicitly authorised
[ ] Runtime SA least privilege
```

### IAM

```text
[ ] No Owner/Editor runtime dependency
[ ] Discovery and mutation permissions separated
[ ] Custom role matches enabled capabilities
[ ] Organisation-level grants reviewed
[ ] Obsolete permissions removed
```

### Registry

```text
[ ] Dedicated PROD bucket
[ ] Uniform bucket-level access
[ ] Public access prevented
[ ] Runtime read-only where possible
[ ] Write access restricted
[ ] CI/schema validation
[ ] Production review required
```

### Event Pipeline

```text
[ ] Organisation sink scope reviewed
[ ] Sink writer only publishes as required
[ ] Pub/Sub IAM restricted
[ ] Eventarc delivery authenticated
[ ] Event classifier validated
[ ] Capability gate enforced
```

### Data

```text
[ ] DEV/PROD BigQuery isolated
[ ] Dashboard does not need direct privileged BigQuery access
[ ] No secret payloads stored
[ ] Operational evidence retained
[ ] Sensitive logs reviewed
```

### Application

```text
[ ] Input validation
[ ] Safe metadata merge
[ ] Fingerprint/ETag handling where required
[ ] Bounded retries
[ ] Unsupported resources skipped
[ ] Exclusions enforced
[ ] No hardcoded credentials
[ ] No hardcoded workload projects
```

---

## 79. Security Architecture Summary

The platform security model deliberately separates identities and permissions by function.

```text
Organisation Logging Sink
        |
        | publish only
        v
      Pub/Sub
        |
        v
     Eventarc
        |
        | invoke only
        v
     Cloud Run
        |
        | dedicated runtime identity
        v
Capability-Controlled Native GCP APIs
```

Brownfield follows the same principle:

```text
CAI read visibility
      |
      v
Compliance / Planning
      |
      v
Cloud Tasks
      |
      | authenticated invocation
      v
/worker
      |
      | runtime least privilege
      v
Supported Resource APIs
```

Dashboard users receive authenticated visibility without inheriting remediation privileges.

The Application Registry remains protected configuration, BigQuery remains auditable operational evidence, and DEV/PROD remain isolated through dedicated projects and identities.

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

- `ARCHITECTURE.md` for overall trust boundaries.
- `IAM.md` for exact identity and permission design.
- `GREENFIELD.md` for event-pipeline security.
- `BROWNFIELD.md` for bulk-remediation safety.
- `APPLICATION_REGISTRY.md` for registry controls.
- `SUPPORTED_RESOURCES.md` for capability-driven IAM.
- `API.md` for endpoint authentication.
- `OPERATIONS.md` for incident response and monitoring.
