# Enterprise Metadata Governance Platform - Supported Resources

## 1. Purpose

This document defines the authoritative capability model for GCP resource types governed by the Enterprise Metadata Governance Platform.

It separates five questions that must never be treated as equivalent:

```text
Can the platform discover the resource?
Can the platform read its current metadata?
Can the platform remediate its metadata?
Is Brownfield supported?
Is Greenfield supported?
```

A Google Cloud client, API permission or adapter existing in the repository does not automatically mean that a resource is production-supported.

Production support requires validated discovery, metadata semantics, IAM, adapter behaviour and - for Greenfield - validated creation-event routing.

---

## 2. Capability States

Every resource type should be assigned an explicit status.

Recommended states:

```text
SUPPORTED
VALIDATED_DEV
IMPLEMENTED_NOT_VALIDATED
PLANNED
UNSUPPORTED
EXCLUDED
```

### SUPPORTED

Validated end-to-end and approved for production.

### VALIDATED_DEV

Successfully validated in `platform-metadata-dev` but not yet approved for production.

### IMPLEMENTED_NOT_VALIDATED

Code exists, but complete end-to-end behaviour has not been proven.

### PLANNED

Intended for future implementation.

### UNSUPPORTED

The required metadata operation is not supported by the platform or underlying service.

### EXCLUDED

Technically possible but deliberately excluded by governance policy.

---

## 3. Environment Model

Development:

```text
platform-metadata-dev
```

Production:

```text
platform-metadata-prod
```

A capability must be validated in DEV before production enablement.

The capability model must not depend on hardcoded workload project IDs.

---

## 4. Brownfield vs Greenfield

Brownfield and Greenfield support must be tracked independently.

### Brownfield

Requires:

```text
Cloud Asset Inventory discovery
        |
        v
Asset classification
        |
        v
Registry resolution
        |
        v
Current metadata read
        |
        v
Compliance
        |
        v
Resource adapter
        |
        v
Native update API
```

### Greenfield

Requires:

```text
Real resource creation
        |
        v
Cloud Audit Log
        |
        v
Organisation sink
        |
        v
Pub/Sub
        |
        v
Eventarc
        |
        v
Classifier
        |
        v
Registry resolution
        |
        v
Resource adapter
```

A resource can therefore support Brownfield while Greenfield remains unvalidated.

---

## 5. Resource Capability Matrix

The following resource families are represented in the platform's current remediation permission catalogue.

The final `Status`, `Brownfield` and `Greenfield` values must reflect actual end-to-end validation evidence before production approval.

| GCP Resource | Primary Mutation Permission | Brownfield | Greenfield | Production Rule |
| --- | --- | --- | --- | --- |
| Resource Manager Project | `resourcemanager.projects.update` | Capability-controlled | Capability-controlled | Enable only if project metadata remediation is explicitly required |
| Compute Engine Instance | `compute.instances.setLabels` | Capability-controlled | Capability-controlled | Requires current label/fingerprint-safe behaviour and validated create event |
| Compute Engine Disk | `compute.disks.setLabels` | Capability-controlled | Capability-controlled | Validate zonal/regional identity and event behaviour |
| Compute Snapshot | `compute.snapshots.setLabels` | Capability-controlled | Capability-controlled | Validate asset mapping and create event |
| Compute Image | `compute.images.setLabels` | Capability-controlled | Capability-controlled | Validate project/global resource handling |
| Compute Forwarding Rule | `compute.forwardingRules.setLabels` | Capability-controlled | Capability-controlled | Validate regional/global variants |
| Compute Address | `compute.addresses.setLabels` | Capability-controlled | Capability-controlled | Validate regional/global variants |
| Cloud Storage Bucket | `storage.buckets.update` | Capability-controlled | Capability-controlled | Preserve unrelated labels and exclude platform registry buckets |
| BigQuery Dataset | `bigquery.datasets.update` | Capability-controlled | Capability-controlled | Distinguish governed workload datasets from governance BigQuery |
| BigQuery Table | `bigquery.tables.update` | Capability-controlled | Capability-controlled | Validate table metadata update semantics |
| Cloud SQL Instance | `cloudsql.instances.update` | Capability-controlled | Capability-controlled | Validate asynchronous update behaviour |
| GKE Cluster | `container.clusters.update` | Capability-controlled | Capability-controlled | Validate supported label operation and location |
| Memorystore Redis Instance | `redis.instances.update` | Capability-controlled | Capability-controlled | Validate region and update semantics |
| Cloud KMS CryptoKey | `cloudkms.cryptoKeys.update` | Capability-controlled | Capability-controlled | Validate metadata support and resource path |
| Secret Manager Secret | `secretmanager.secrets.update` | Capability-controlled | Capability-controlled | Govern secret metadata only - never secret payload |
| Pub/Sub Topic | `pubsub.topics.update` | Capability-controlled | Capability-controlled | Separate workload-resource governance from platform event transport |
| Pub/Sub Subscription | `pubsub.subscriptions.update` | Capability-controlled | Capability-controlled | Validate subscription metadata semantics |
| Artifact Registry Repository | `artifactregistry.repositories.update` | Capability-controlled | Capability-controlled | Validate location-aware resource identity |
| Cloud Run Service | `run.services.update` | Capability-controlled | Capability-controlled | Separate governed workload services from governance Cloud Run service |
| App Engine Application | `appengine.applications.update` | Capability-controlled | Capability-controlled | Enable only after metadata operation validation |
| App Engine Service | `appengine.services.update` | Capability-controlled | Capability-controlled | Enable only after metadata operation validation |
| App Engine Version | `appengine.versions.update` | Capability-controlled | Capability-controlled | Enable only after metadata operation validation |
| Cloud Build Build | `cloudbuild.builds.update` | Capability-controlled | Capability-controlled | Do not enable solely because permission exists |
| Developer Connect Connection | `developerconnect.connections.update` | Capability-controlled | Capability-controlled | Validate metadata support |
| Developer Connect Git Repository Link | `developerconnect.gitRepositoryLinks.update` | Capability-controlled | Capability-controlled | Validate metadata support |
| OS Config Policy Assignment | `osconfig.osPolicyAssignments.update` | Capability-controlled | Capability-controlled | Validate update semantics |
| Eventarc Trigger | `eventarc.triggers.update` | Capability-controlled | Capability-controlled | Separate governed triggers from governance event infrastructure |
| Apigee Instance | `apigee.instances.update` | Capability-controlled | Capability-controlled | Validate supported metadata operation |
| Monitoring Alert Policy | `monitoring.alertPolicies.update` | Capability-controlled | Capability-controlled | Validate label/user-label semantics |

`Capability-controlled` deliberately means that repository implementation and DEV/PROD capability configuration determine enablement. It does not claim production validation without test evidence.

---

## 6. Permission Catalogue

The current candidate mutation permission catalogue is:

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

This is a candidate capability catalogue - not the final production custom role.

---

## 7. Read Permissions

Mutation permissions alone may not be sufficient.

Adapters can require current resource state before updating metadata.

Examples include:

```text
labels
label fingerprints
ETags
versions
current metadata
location
resource state
```

Each supported-resource entry must therefore document:

```text
Asset type
Read operation
Read permission
Mutation operation
Mutation permission
```

Only permissions actually required by the adapter should be included in production IAM.

---

## 8. Authoritative Capability Record

For every supported resource, maintain a record containing at least:

| Field | Purpose |
| --- | --- |
| Canonical asset type | Internal dispatch/discovery identity |
| Google service | Native API service |
| CAI asset type | Brownfield discovery mapping |
| Adapter | Resource-specific implementation |
| Client | Native API access layer |
| Metadata type | Labels/user labels/other supported metadata |
| Read permission | Current-state retrieval |
| Mutation permission | Metadata update |
| Brownfield enabled | Existing-resource support |
| Greenfield enabled | Creation-event support |
| Greenfield serviceName | Validated Audit Log service |
| Greenfield methodName | Validated creation method |
| Location model | Global/regional/zonal |
| Retry behaviour | Safe transient retry model |
| Validation status | DEV/PROD evidence |
| Notes | Service-specific constraints |

This matrix should become the single technical source of truth for capability support.

---

## 9. Brownfield Support Criteria

A resource must not be marked Brownfield-supported until:

```text
[ ] Cloud Asset Inventory asset type identified
[ ] Discovery tested
[ ] Internal asset mapping tested
[ ] Registry resolution tested
[ ] Current resource read tested
[ ] Required metadata extracted correctly
[ ] Compliance comparison tested
[ ] Adapter implemented
[ ] Existing unrelated metadata preservation tested
[ ] Mutation API tested
[ ] Required IAM identified
[ ] Retry/error behaviour tested
[ ] remediation_plan evidence verified
[ ] remediation_execution evidence verified
[ ] DEV end-to-end test passed
```

Production support additionally requires approval and PROD deployment validation.

---

## 10. Greenfield Support Criteria

Greenfield requires everything needed for safe remediation plus event-path validation.

A resource must not be marked Greenfield-supported until:

```text
[ ] Real resource creation performed
[ ] Actual Audit Log captured
[ ] Audit Log category identified
[ ] protoPayload.serviceName confirmed
[ ] protoPayload.methodName confirmed
[ ] Organisation sink filter matches event
[ ] Central Pub/Sub receives event
[ ] Eventarc delivers event
[ ] Cloud Run receives event
[ ] Parser handles payload
[ ] Classifier identifies canonical asset type
[ ] Project ID resolves correctly
[ ] Resource identifier resolves correctly
[ ] Capability gate explicitly enables resource
[ ] Registry binding resolves
[ ] Adapter reads current resource
[ ] Required IAM identified
[ ] Metadata mutation succeeds
[ ] Duplicate event is safe
[ ] Temporary resource-not-found behaviour is safe
[ ] GREENFIELD execution evidence is written
[ ] DEV end-to-end test passed
```

---

## 11. Greenfield Event Matrix

Every Greenfield-supported resource should have an explicit event definition.

Example structure:

| Asset Type | `serviceName` | `methodName` | Log Category | Classifier | Status |
| --- | --- | --- | --- | --- | --- |
| Compute Instance | Captured from real DEV event | Captured from real DEV event | Validated | Compute classifier | Evidence required |
| Storage Bucket | Captured from real DEV event | Captured from real DEV event | Validated | Storage classifier | Evidence required |
| Cloud SQL Instance | Captured from real DEV event | Captured from real DEV event | Validated | Cloud SQL classifier | Evidence required |

Do not populate production event values from assumptions.

Capture them from real DEV resource creation and confirm against official Google Cloud behaviour.

---

## 12. Why Generic Method Matching Is Insufficient

A filter such as:

```text
protoPayload.methodName =~ ".*insert.*"
```

or:

```text
protoPayload.methodName =~ ".*create.*"
```

does not prove that every matched event represents a resource the platform can safely remediate.

Even within a single Google service:

- different resource families use different methods
- helper operations can match broad patterns
- API versions may differ
- payload resource paths may differ
- some operations may not represent final resource creation

The production event matrix must therefore be capability-driven.

---

## 13. Compute Engine

The permission catalogue includes:

```text
compute.instances.setLabels
compute.disks.setLabels
compute.snapshots.setLabels
compute.images.setLabels
compute.forwardingRules.setLabels
compute.addresses.setLabels
```

Compute resources require careful handling because they may be:

```text
zonal
regional
global
```

The adapter must derive location/resource identity from authoritative resource data rather than assume every Compute resource is zonal.

Where label fingerprints are required, the current fingerprint must be retrieved immediately before mutation.

---

## 14. Cloud Storage

Candidate mutation permission:

```text
storage.buckets.update
```

Special controls include:

- preserve unrelated labels
- protect registry/control-plane buckets
- use configuration-driven bucket exclusions
- avoid remediating platform infrastructure unintentionally

The governance registry bucket is a platform dependency and must remain excluded where required by policy.

---

## 15. BigQuery

Candidate permissions:

```text
bigquery.datasets.update
bigquery.tables.update
```

There are two separate BigQuery concerns:

```text
Governance BigQuery
    -> platform evidence storage

Workload BigQuery
    -> governed Dataset/Table resources
```

Do not confuse governance dataset access with workload metadata-remediation IAM.

---

## 16. Cloud SQL

Candidate mutation permission:

```text
cloudsql.instances.update
```

Cloud SQL support must account for:

- regional resource identity
- current settings/metadata
- asynchronous update operations where applicable
- operation completion/error handling

Brownfield and Greenfield support must be validated independently.

---

## 17. GKE

Candidate mutation permission:

```text
container.clusters.update
```

GKE support must validate:

- regional versus zonal clusters
- correct metadata field
- update-mask/update semantics
- asynchronous operation behaviour
- current resource state

NodePool support must not be inferred automatically from Cluster support.

Each asset type requires its own capability record.

---

## 18. Memorystore for Redis

Candidate permission:

```text
redis.instances.update
```

Validation must include:

- regional resource identity
- supported metadata field
- update behaviour
- operation completion

---

## 19. Cloud KMS

Candidate permission:

```text
cloudkms.cryptoKeys.update
```

Governance must affect only supported CryptoKey metadata.

It must not alter:

- cryptographic key material
- key versions
- rotation settings
- IAM policy

unless a separate approved governance capability is explicitly designed for those operations.

---

## 20. Secret Manager

Candidate permission:

```text
secretmanager.secrets.update
```

Metadata governance applies to the Secret resource.

The platform must never read or modify secret payload values as part of label governance.

---

## 21. Pub/Sub

Candidate permissions:

```text
pubsub.topics.update
pubsub.subscriptions.update
```

Keep two concerns separate:

```text
Workload Pub/Sub resources
    -> may be governance targets

metadata-governance-events
    -> platform Greenfield transport
```

The platform transport topic/subscriptions must be protected from unintended governance behaviour where appropriate.

---

## 22. Artifact Registry

Candidate permission:

```text
artifactregistry.repositories.update
```

Repository identity includes location.

The adapter must correctly handle the repository's project, location and name.

---

## 23. Cloud Run

Candidate permission:

```text
run.services.update
```

Workload Cloud Run services may be governance targets.

The central:

```text
metadata-governance
```

Cloud Run service is platform control-plane infrastructure and must be protected from unintended self-remediation where required.

Cloud Run deployment IAM is separate from Cloud Run workload metadata-remediation IAM.

---

## 24. App Engine

Candidate permissions:

```text
appengine.applications.update
appengine.services.update
appengine.versions.update
```

Each App Engine resource type must be validated separately.

Do not assume Application support proves Service or Version support.

---

## 25. Cloud Build

Candidate permission:

```text
cloudbuild.builds.update
```

The permission appearing in the candidate catalogue does not prove that Build resources expose the metadata semantics required by the platform.

Production enablement requires validation of:

- supported metadata field
- mutable state
- API operation
- IAM
- Brownfield discovery
- Greenfield event

If these cannot be proven, mark the capability unsupported rather than forcing an implementation.

---

## 26. Developer Connect

Candidate permissions:

```text
developerconnect.connections.update
developerconnect.gitRepositoryLinks.update
```

Connections and Git Repository Links require separate capability records.

---

## 27. OS Config

Candidate permission:

```text
osconfig.osPolicyAssignments.update
```

Validation must include location/resource path and update semantics.

---

## 28. Eventarc

Candidate permission:

```text
eventarc.triggers.update
```

A workload Eventarc trigger may be a governance target.

This permission is unrelated to the Eventarc permissions required for the platform's own Greenfield delivery trigger.

The two IAM paths must remain separate.

---

## 29. Apigee

Candidate permission:

```text
apigee.instances.update
```

Apigee capability must be enabled only after the supported metadata operation is confirmed and tested.

---

## 30. Cloud Monitoring Alert Policies

Candidate permission:

```text
monitoring.alertPolicies.update
```

Validation must confirm the exact user-label/metadata semantics used by Alert Policies and ensure the adapter does not overwrite unrelated policy configuration.

---

## 31. Resource Manager Projects

Candidate permissions:

```text
resourcemanager.projects.get
resourcemanager.projects.update
```

`resourcemanager.projects.get` supports project visibility.

`resourcemanager.projects.update` is required only if project metadata itself is intentionally governed.

Do not grant project update merely because Brownfield needs to discover projects.

---

## 32. Resources Without Label Support

Not every Google Cloud resource supports labels.

The platform must not simulate label support where the underlying service does not provide a supported metadata mechanism.

For example, a previously encountered API Keys integration was excluded because API Keys do not provide the required label capability for this platform.

Unsupported resources should be explicitly represented as:

```text
UNSUPPORTED
```

rather than left to fail repeatedly at runtime.

---

## 33. Resources Discovered but Not Remediable

Cloud Asset Inventory can expose resource types that the platform does not remediate.

This is expected.

The correct flow is:

```text
CAI discovers resource
       |
       v
Capability lookup
       |
       +-- supported -> evaluate/remediate
       |
       +-- unsupported -> skip safely
```

Discovery coverage should not be confused with remediation coverage.

---

## 34. Adapter Registration

The dispatcher should route canonical asset types to dedicated resource handlers/adapters.

Conceptually:

```text
Canonical Asset Type
       |
       v
Dispatcher
       |
       +-- Compute adapter
       +-- Storage adapter
       +-- BigQuery adapter
       +-- Cloud SQL adapter
       +-- GKE adapter
       +-- ...
```

Avoid a single monolithic `app.py` containing service-specific update logic.

---

## 35. No Hardcoding

Resource capability decisions must be data/configuration-driven.

Do not hardcode:

- client workload project IDs
- application ownership values
- DEV-only project names in resource logic
- PROD-only service-account emails
- resource support decisions in dashboard JavaScript
- generic service assumptions scattered through handlers

Environment infrastructure configuration belongs to Terraform/runtime configuration.

Application ownership belongs to the Application Registry.

Resource support belongs to the capability model.

---

## 36. Capability Configuration

A resource capability definition should allow the platform to determine behaviour without editing orchestration code for each execution.

Conceptually:

```yaml
asset_type: example.googleapis.com/Resource
brownfield:
  enabled: true
greenfield:
  enabled: false
adapter: example
```

This example is conceptual only.

The repository's actual configuration schema remains authoritative.

---

## 37. Capability Promotion

A resource should progress through controlled stages:

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

Promotion requires evidence.

Do not jump directly from code implementation to production-supported status.

---

## 38. Capability Removal

If a previously supported resource becomes unsafe or incompatible:

```text
1. Disable capability
2. Stop new remediation
3. Preserve historical evidence
4. Investigate root cause
5. Correct adapter/event/IAM behaviour
6. Revalidate in DEV
7. Reapprove for production
```

Removing support must not delete historical BigQuery execution records.

---

## 39. Capability and IAM Coupling

The production custom IAM role should follow active capabilities.

```text
Capability enabled
      |
      v
Required adapter operation
      |
      v
Required IAM permission
      |
      v
Production custom role
```

When a capability is permanently removed, its mutation permission should be reviewed for removal.

This prevents permission accumulation over time.

---

## 40. Capability and Organisation Sink Coupling

Greenfield-enabled capabilities should drive the organisation sink/event classification requirements.

```text
Greenfield capability
      |
      v
Validated serviceName/methodName
      |
      v
Sink filter coverage
      |
      v
Classifier mapping
```

The sink should not be expanded merely because a service has an API client in the repository.

---

## 41. Capability and Dashboard Coupling

The dashboard must distinguish:

```text
Configured capabilities
```

from:

```text
Live operational resource counts
```

Supported-resource definitions can be displayed as platform capability information.

Actual discovered/compliant/remediated counts must come from operational evidence such as BigQuery.

Do not derive live governance counts from repository snapshots.

---

## 42. Capability Test Evidence

For every production-supported resource, retain evidence including:

```text
Resource type
Test project
Test date
Brownfield test result
Greenfield test result
Observed serviceName
Observed methodName
Required IAM
Metadata before
Metadata after
Existing metadata preservation result
BigQuery evidence result
Known limitations
Reviewer/approval
```

This becomes the defensible basis for client support claims.

---

## 43. New Resource Onboarding

Recommended workflow:

```text
1. Confirm official metadata/label support
2. Identify CAI asset type
3. Identify native read API
4. Identify native mutation API
5. Identify exact IAM
6. Implement client
7. Implement adapter
8. Register dispatcher mapping
9. Add Brownfield capability
10. Validate Brownfield in DEV
11. Create real resource
12. Capture real Audit Log
13. Implement/validate Greenfield classifier
14. Update sink filter if required
15. Validate Greenfield in DEV
16. Verify BigQuery evidence
17. Update capability matrix
18. Security/IAM review
19. Promote to PROD
```

---

## 44. Validation Failure

If a resource fails validation, do not broaden IAM or event filters blindly.

Identify the failed layer:

```text
Discovery?
Classification?
Registry?
Current-state read?
Compliance?
Adapter?
IAM?
API mutation?
Operation polling?
Event routing?
BigQuery evidence?
```

The capability remains non-production until the failure is resolved.

---

## 45. Production Safety Rules

```text
[ ] Unsupported resources are skipped
[ ] Resource support is explicit
[ ] Brownfield and Greenfield flags are independent
[ ] Real Greenfield events are captured before enablement
[ ] Existing unrelated metadata is preserved
[ ] Native APIs are used for mutation
[ ] IAM is least privilege
[ ] Platform control-plane resources are excluded where required
[ ] DEV validation precedes PROD
[ ] BigQuery evidence is available
```

---

## 46. Client-Facing Support Definition

A resource should be described to the client as **supported** only when:

```text
The platform can discover/identify it,
resolve its application metadata,
safely read its current state,
evaluate compliance,
apply the approved metadata operation,
and record auditable evidence
for the execution mode being claimed.
```

If only Brownfield has been validated, state:

```text
Brownfield supported
Greenfield not yet validated
```

Do not claim generic "support" that hides the distinction.

---

## 47. Supported Resources Checklist

For each resource:

```text
[ ] Canonical asset type documented
[ ] CAI asset type documented
[ ] Native service documented
[ ] Adapter documented
[ ] Read permission documented
[ ] Mutation permission documented
[ ] Metadata field documented
[ ] Location model documented
[ ] Brownfield status documented
[ ] Greenfield status documented
[ ] Greenfield serviceName documented if enabled
[ ] Greenfield methodName documented if enabled
[ ] Retry behaviour documented
[ ] Existing metadata preservation tested
[ ] DEV evidence recorded
[ ] PROD approval recorded
```

---

## 48. Architecture Summary

The supported-resource model is the safety boundary between discovering Google Cloud resources and changing them.

The governing principle is:

```text
Resource exists
      |
      v
Resource discovered
      |
      v
Capability explicitly enabled?
      |
   +--+--+
   |     |
   No    Yes
   |     |
   v     v
 Skip   Validate metadata
             |
             v
        Safe remediation
```

This prevents the platform from assuming that every Google Cloud resource visible through Cloud Asset Inventory or Audit Logs can be safely modified.

Brownfield and Greenfield are independently validated, IAM follows enabled capabilities, and production support claims are based on end-to-end evidence rather than code presence.

---

## 49. Related Documentation

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
- `IAM.md` for the custom remediation permission model.
- `GREENFIELD.md` for event support requirements.
- `BROWNFIELD.md` for discovery/remediation support requirements.
- `APPLICATION_REGISTRY.md` for application metadata resolution.
- `TESTING.md` for end-to-end capability validation.
