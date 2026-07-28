# Enterprise Metadata Governance Platform - IAM and Access Control

## 1. Purpose

This document defines the Identity and Access Management model for the Enterprise Metadata Governance Platform on Google Cloud.

It covers the governance runtime identity, DEV/PROD separation, organisation-level discovery and remediation, Cloud Run, Cloud Tasks, Pub/Sub/Eventarc, BigQuery, Application Registry, Artifact Registry, GitHub Actions Workload Identity Federation (WIF), dashboard access and production least-privilege controls.

The IAM model must support enterprise governance without hardcoding application-specific project IDs, users or service-account addresses in application business logic.

## 2. Core IAM Principles

### 2.1 Dedicated environment identities

| Environment | Governance Project | Runtime Identity |
| --- | --- | --- |
| Development | `platform-metadata-dev` | Dedicated DEV `metadata-governance` service account |
| Production | `platform-metadata-prod` | Dedicated PROD `metadata-governance` service account |

The DEV identity must never be reused as the production governance identity.

### 2.2 Least privilege

IAM follows the capabilities actually enabled by the platform. The presence of an adapter, client or classifier in the repository does not justify granting its mutation permissions in production.

### 2.3 Central control plane

The governance runtime operates from a dedicated governance project while authorised organisation-level IAM provides visibility and metadata-remediation access to governed workload projects.

### 2.4 Human and machine access separation

Dashboard users receive only authenticated dashboard/service invocation access. Event delivery, workers, deployment and remediation use machine identities.

### 2.5 Keyless CI-CD

GitHub Actions uses WIF. Long-lived Google Cloud service-account JSON keys must not be used for the normal deployment path.

## 3. IAM Trust Model

```text
GCP Organisation
      |
      +-- Organisation Discovery IAM
      |       |
      |       +-- Project visibility
      |       +-- Cloud Asset Inventory visibility
      |
      +-- Metadata Remediation Custom Role
      |       |
      |       +-- Enabled resource update permissions
      |
      +-- Governed Workload Projects
      |
      +-- platform-metadata-prod / platform-metadata-dev
              |
              +-- Cloud Run
              +-- Cloud Tasks
              +-- Pub/Sub
              +-- Eventarc
              +-- BigQuery
              +-- Registry Bucket
              +-- Artifact Registry
              +-- WIF
```

## 4. Governance Runtime Service Account

The primary application runtime identity is the environment-specific `metadata-governance` service account.

The exact email is supplied by environment/deployment configuration rather than hardcoded in application logic.

Its responsibilities include:

- Cloud Asset Inventory discovery
- project/resource visibility
- Application Registry reads
- governance BigQuery reads/writes
- compliance processing
- remediation planning
- Cloud Tasks enqueue
- authenticated worker execution
- service-specific resource reads
- service-specific metadata mutation
- Greenfield processing
- audit/reporting operations

## 5. DEV and PROD Isolation

```text
platform-metadata-dev
    -> DEV service account
    -> DEV registry
    -> DEV BigQuery
    -> DEV Pub/Sub/Eventarc
    -> DEV Cloud Tasks
    -> DEV deployment trust

platform-metadata-prod
    -> PROD service account
    -> PROD registry
    -> PROD BigQuery
    -> PROD Pub/Sub/Eventarc
    -> PROD Cloud Tasks
    -> PROD deployment trust
```

The following must not occur:

- DEV service account used for PROD governance
- PROD depending on DEV registry data
- shared DEV/PROD queues
- shared governance BigQuery datasets
- unintended cross-environment WIF impersonation
- DEV dashboard access automatically granting PROD access

## 6. Organisation-Level Discovery

Brownfield governance requires organisation-level visibility across authorised workload projects.

Discovery and remediation are separate permission concerns.

The runtime requires project visibility, including:

```text
resourcemanager.projects.get
```

Where project labels themselves are an enabled remediation capability, the custom remediation role may additionally require:

```text
resourcemanager.projects.update
```

`resourcemanager.projects.update` must not be granted merely for project discovery.

Cloud Asset Inventory permissions should be read/search oriented and scoped to the discovery operations used by the application.

## 7. Resource Remediation Custom Role

A custom organisation role is used for service-specific metadata mutation. The role must be built from production-enabled capabilities rather than every integration present in the source repository.

### Candidate permission catalogue

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

### Critical rule

This is the candidate permission catalogue - not an instruction to grant all permissions.

The production role should be derived as:

```text
Enabled capability
    -> validated adapter
    -> required read/update operations
    -> required IAM permissions
    -> production custom role
```

If a capability is not enabled and validated, its mutation permission should not be included solely because code exists for that service.

## 8. Resource Read Permissions

Many service update APIs require current resource state, such as:

- labels
- fingerprints
- ETags
- versions
- current metadata

Therefore an enabled adapter can require both a resource read permission and the corresponding update/setLabels permission.

The exact read/update pair must be documented per resource in `SUPPORTED_RESOURCES.md`.

Do not assume the mutation permission alone is sufficient.

## 9. Governance BigQuery IAM

The governance application requires access to its central dataset containing:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

Runtime access must support the application's actual evidence writes and dashboard/reporting queries.

Governance dataset permissions are separate from permissions such as `bigquery.datasets.update` or `bigquery.tables.update` used when BigQuery resources in workload projects are themselves being remediated.

## 10. Application Registry IAM

The runtime loads the Application Registry from the governance Cloud Storage bucket.

Production runtime access should be limited to the object/list/read operations actually required by the registry loader.

Registry mutation should be owned by the registry validation/promotion process rather than ordinary resource-remediation logic.

Recommended separation:

```text
Runtime identity
    -> read approved registry

Registry deployment identity/process
    -> validate and publish registry
```

If DEV currently grants broader object administration for engineering convenience, PROD should review whether runtime access can be reduced.

## 11. Cloud Tasks IAM

Brownfield execution has two distinct IAM flows.

### Task creation

The orchestrator needs permission to enqueue work into:

```text
metadata-remediation
```

### Worker invocation

Cloud Tasks sends an authenticated request to the Cloud Run worker endpoint.

```text
Governance Runtime
      |
      | enqueue
      v
Cloud Tasks
      |
      | OIDC-authenticated request
      v
Cloud Run /worker
```

The OIDC identity must have Cloud Run invocation permission.

The worker endpoint must not depend on anonymous public access.

## 12. Pub/Sub IAM

Greenfield event transport uses:

```text
metadata-governance-events
```

### Organisation Logging sink writer

The organisation-level Cloud Logging sink has its own writer identity. That writer identity requires permission to publish to the central Pub/Sub topic.

```text
Organisation Logging Sink
        |
        | sink writer identity
        | Pub/Sub publish
        v
metadata-governance-events
```

The sink writer identity is not the same concept as the governance runtime service account.

### Governed Pub/Sub resources

If Pub/Sub topics/subscriptions are themselves governed resources, `pubsub.topics.update` and `pubsub.subscriptions.update` belong to the remediation capability role. They are separate from permissions used by the platform's Greenfield transport.

## 13. Eventarc IAM

The Eventarc trigger delivers Pub/Sub `messagePublished` events to Cloud Run.

The event-delivery identity requires the permissions necessary to receive events and invoke the Cloud Run destination.

```text
Pub/Sub
   -> Eventarc
   -> authenticated Cloud Run invocation
   -> metadata-governance
```

Eventarc delivery permissions must not be confused with resource-remediation permissions such as `eventarc.triggers.update`, which are required only if Eventarc triggers themselves are governed resources.

## 14. Cloud Run IAM

Cloud Run hosts governance APIs, Brownfield orchestration, Greenfield processing, the Cloud Tasks worker, reporting APIs and the dashboard.

Machine callers such as Eventarc and Cloud Tasks require authenticated invocation.

Authorised dashboard users may receive:

```text
roles/run.invoker
```

on the governance service.

Production must not grant Cloud Run Invoker to:

```text
allUsers
```

for this platform.

## 15. Dashboard Access

The dashboard is intended only for authenticated authorised organisation users.

```text
Authorised organisation identity
          |
          | Cloud Run IAM
          v
Enterprise Governance Dashboard
```

Dashboard access alone does not require:

- organisation remediation permissions
- Cloud Asset Inventory organisation access
- Cloud Tasks administration
- registry modification
- service-account impersonation
- WIF access

This keeps dashboard access separate from operational control-plane privileges.

## 16. Artifact Registry IAM

Artifact Registry hosts the governance application container.

CI-CD requires the permissions needed to push the application image. The deployment path requires the permissions needed to deploy the selected image to Cloud Run.

Artifact Registry deployment permissions must not be bundled into the organisation metadata-remediation custom role.

## 17. GitHub Actions Workload Identity Federation

CI-CD uses WIF rather than service-account keys.

The deployed configuration uses:

```text
Workload Identity Pool: github-actions-pool
Provider: github-provider
Issuer: https://token.actions.githubusercontent.com
Approved repository: RouseServices/platform-metadata
```

Trust must remain restricted at both:

- provider attribute condition
- service-account principal binding

The intended flow is:

```text
RouseServices/platform-metadata
        |
        v
GitHub OIDC
        |
        v
Google WIF Provider
        |
        v
Approved Deployment Service Account
        |
        v
Artifact Registry / Cloud Run Deployment
```

Do not broaden this trust to arbitrary GitHub repositories.

Do not store a long-lived service-account JSON key in GitHub secrets as a replacement.

## 18. Logical Identity Separation

Even where DEV currently reuses one service account for multiple responsibilities, documentation and production review should distinguish these logical identities:

| Identity Function | Responsibility |
| --- | --- |
| Runtime | Execute governance, discovery, compliance and remediation |
| Deployment | Push image and deploy Cloud Run revision |
| Event Delivery | Deliver Eventarc events and invoke Cloud Run |
| Logging Sink Writer | Export organisation audit logs to Pub/Sub |
| Cloud Tasks Caller | Invoke worker endpoint |
| Dashboard User | Authenticated human dashboard access |

This separation allows least-privilege hardening without changing application architecture.

## 19. Service Account Impersonation

Service-account impersonation must be tightly controlled.

Permissions capable of generating access or identity tokens must be granted only to approved deployment principals.

Do not grant Service Account Token Creator broadly at project or organisation level.

GitHub principals should reach Google Cloud through the approved WIF-to-service-account trust boundary.

## 20. Organisation IAM vs Governance Project IAM

These must be treated separately.

### Organisation IAM

Used for:

- project/resource discovery
- Cloud Asset Inventory visibility
- validated metadata remediation against workload resources

### Governance project IAM

Used for:

- BigQuery governance data
- registry storage
- Cloud Tasks
- Pub/Sub
- Eventarc
- Cloud Run
- Artifact Registry
- logging/monitoring
- CI-CD deployment

Project-level access to `platform-metadata-prod` does not automatically provide remediation rights in workload projects.

## 21. Central Workload Project Access

The platform does not require a governance service account deployed separately into every workload project when the central runtime has approved organisation-level permissions.

```text
platform-metadata-prod runtime identity
               |
               | organisation IAM
               v
        governed workload projects
```

Actual remediation is still controlled by:

- registry/project binding
- supported-resource capability
- exclusions
- compliance evaluation
- service-specific adapter logic
- custom IAM permissions

IAM permission alone must never be treated as an instruction to mutate a resource.

## 22. IAM and Capability Lifecycle

IAM must evolve with the supported-resource matrix.

Example:

```text
Cloud SQL capability enabled
        |
        v
Cloud SQL adapter validated
        |
        v
Required read operation confirmed
        |
        v
cloudsql.instances.update confirmed
        |
        v
Permission approved for PROD role
```

If the capability is subsequently disabled, the corresponding mutation permission should be reviewed for removal.

## 23. IAM Change Process

Production IAM changes should follow:

```text
1. Identify capability/change
2. Identify exact API operations
3. Identify required IAM permissions
4. Determine required scope
5. Update Terraform
6. Review Terraform plan
7. Obtain platform/security approval
8. Apply and validate in platform-metadata-dev
9. Promote to platform-metadata-prod
10. Validate runtime and audit evidence
```

Avoid unmanaged manual production IAM changes.

Emergency manual changes must be reconciled into Terraform after the incident/change.

## 24. IAM Validation

### Brownfield

Verify:

```text
[ ] Runtime can discover intended projects
[ ] Runtime can query Cloud Asset Inventory
[ ] Runtime can read Application Registry
[ ] resource_snapshot writes succeed
[ ] compliance_snapshot writes succeed
[ ] remediation_plan writes succeed
[ ] Runtime can enqueue Cloud Tasks
[ ] Worker authentication succeeds
[ ] Adapter can read target resource metadata
[ ] Adapter can mutate an enabled resource
[ ] remediation_execution write succeeds
```

### Greenfield

Verify:

```text
[ ] Organisation Logging sink writer can publish to central Pub/Sub
[ ] Event reaches Eventarc
[ ] Eventarc identity can invoke Cloud Run
[ ] Runtime can classify the event
[ ] Runtime can resolve registry metadata
[ ] Runtime can remediate the enabled resource
[ ] GREENFIELD execution evidence is written
```

### CI-CD

Verify:

```text
[ ] GitHub OIDC authentication succeeds
[ ] Only approved repository is trusted
[ ] Approved principal can impersonate deployment identity
[ ] Artifact Registry push succeeds
[ ] Cloud Run deployment succeeds
[ ] No static service-account key is required
```

### Dashboard

Verify:

```text
[ ] Authorised user can access dashboard
[ ] Unauthorised user cannot invoke the service
[ ] Dashboard access alone does not grant remediation privileges
```

## 25. IAM Troubleshooting

For every permission denial, capture:

- caller principal/service account
- exact denied permission
- API/service
- target project/resource
- execution mode
- relevant Cloud Audit Log
- Terraform role/binding expected to provide access

Do not fix permission failures by immediately granting:

```text
roles/owner
roles/editor
```

Determine whether the missing permission belongs to:

- governance runtime
- organisation discovery
- metadata remediation
- Logging sink writer
- Eventarc delivery
- Cloud Run invocation
- Cloud Tasks
- WIF/deployment

and update the appropriate Terraform-managed role/binding.

## 26. IAM Anti-Patterns

Do not:

- use `roles/owner` for the governance runtime
- use `roles/editor` as a remediation shortcut
- grant all candidate update permissions before capability validation
- share DEV and PROD runtime identities
- grant dashboard users remediation permissions unnecessarily
- expose the production Cloud Run service to `allUsers`
- store service-account JSON keys in GitHub
- trust arbitrary GitHub repositories through WIF
- grant Service Account Token Creator broadly
- grant Pub/Sub publisher to the wrong identity instead of the Logging sink writer
- confuse Eventarc delivery IAM with Eventarc resource-remediation IAM
- hardcode service-account emails in application logic
- manually change production IAM without Terraform reconciliation
- confuse governance BigQuery access with BigQuery resource-remediation permissions

## 27. Production IAM Checklist

### Environment isolation

```text
[ ] Dedicated platform-metadata-prod runtime identity exists
[ ] DEV runtime identity is not used by PROD
[ ] PROD registry access points only to PROD registry
[ ] PROD governance BigQuery access points to PROD dataset
[ ] PROD event/queue infrastructure uses PROD identities
```

### Organisation access

```text
[ ] Project discovery permissions validated
[ ] Cloud Asset Inventory permissions validated
[ ] Metadata-remediation custom role reviewed
[ ] Only enabled resource mutation permissions retained
[ ] Organisation scope approved
```

### Greenfield

```text
[ ] Logging sink writer can publish to PROD topic
[ ] Eventarc event receiver access validated
[ ] Eventarc can invoke PROD Cloud Run
[ ] No anonymous invocation is required
```

### Brownfield

```text
[ ] Runtime can enqueue PROD Cloud Tasks
[ ] Worker authentication succeeds
[ ] Required resource read permissions validated
[ ] Required mutation permissions validated
[ ] BigQuery execution evidence succeeds
```

### CI-CD

```text
[ ] PROD WIF trust reviewed
[ ] Approved GitHub repository only
[ ] No service-account key required
[ ] Impersonation scope limited
[ ] Artifact Registry push validated
[ ] Cloud Run deployment validated
```

### Dashboard

```text
[ ] Only approved organisation users/groups can invoke dashboard
[ ] No allUsers binding exists
[ ] Dashboard access does not grant remediation IAM
```

## 28. Recommended Logical Role Separation

| IAM Function | Scope | Purpose |
| --- | --- | --- |
| Governance Runtime | Governance project | Registry, BigQuery, Tasks and runtime platform access |
| Organisation Discovery | Organisation | Project and resource inventory visibility |
| Metadata Remediation | Organisation | Validated resource metadata mutation only |
| Logging Sink Publisher | Central Pub/Sub topic | Export organisation audit events |
| Eventarc Delivery | Governance service | Deliver Greenfield events to Cloud Run |
| CI-CD Deployment | Governance project | Push/deploy application |
| WIF Impersonation | Deployment service account | Approved GitHub repository authentication |
| Dashboard User | Cloud Run service | Authenticated human dashboard invocation |

## 29. Client Permission Catalogue

The candidate resource-update permissions identified for the platform are:

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

For client approval, every permission should be mapped to:

```text
Asset type
Adapter
Required read permission
Required mutation permission
Brownfield support
Greenfield support
Validation status
```

Only permissions required by enabled and tested capabilities should remain in the production custom role.

## 30. Related Documentation

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

See `ARCHITECTURE.md` for trust boundaries, `DEPLOYMENT.md` for Terraform/CI-CD deployment, and `SUPPORTED_RESOURCES.md` for the authoritative resource-to-permission capability matrix.
