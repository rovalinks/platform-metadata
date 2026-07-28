# Enterprise Metadata Governance Platform - Architecture

## 1. Purpose

This document describes the deployed architecture of the Enterprise Metadata Governance Platform on Google Cloud.

It is intended for cloud engineering, platform engineering, security, operations, FinOps and application teams that need to understand how the platform discovers, evaluates, remediates and reports metadata compliance across the Google Cloud estate.

This document covers both:

- **Brownfield governance** - governance of resources that already exist.
- **Greenfield governance** - event-driven governance of newly created resources.

The architecture is designed around two dedicated governance control-plane projects:

| Environment | Governance Project | Purpose |
| --- | --- | --- |
| Development | `platform-metadata-dev` | Development, integration, event validation, resource-adapter testing, Brownfield testing, dashboard development and controlled scale testing |
| Production | `platform-metadata-prod` | Production organisation-wide metadata governance and reporting |

The development and production environments must remain isolated. Each environment should have its own runtime identity, registry, BigQuery dataset, messaging infrastructure, queues and deployment controls.

---

## 2. Architecture Principles

The platform follows these core principles.

### 2.1 Centralised governance control plane

Governance services run in dedicated metadata-platform projects rather than inside every workload project.

Client workload projects remain governance targets.

### 2.2 Registry-driven metadata

Application ownership and required metadata are resolved from a central Application Registry rather than embedded in resource-remediation code.

This separates application metadata from platform execution logic.

### 2.3 Brownfield and Greenfield share one governance model

Brownfield and Greenfield use different ingestion mechanisms, but converge on common platform services for:

- registry resolution
- capability validation
- compliance evaluation
- resource-specific metadata handling
- remediation
- execution evidence
- reporting

### 2.4 Capability-controlled remediation

The existence of a client, adapter, extractor or classifier in the source repository does not automatically make a GCP resource type production-supported.

Resource support is controlled by the platform capability configuration and must be explicitly enabled and validated.

### 2.5 Serverless execution

The runtime is hosted on Cloud Run and configured to scale to zero.

Cloud Tasks provides asynchronous Brownfield remediation execution.

This avoids permanently running worker infrastructure.

### 2.6 Least privilege

IAM permissions should follow the resource capabilities that are actually enabled.

Development and production use separate security boundaries.

### 2.7 Auditable execution

Resource discovery, compliance results, remediation plans and execution evidence are persisted in BigQuery.

---

## 3. High-Level Architecture

```text
                                      GCP ORGANISATION
                                             |
                 +---------------------------+---------------------------+
                 |                                                       |
                 |                                                       |
          EXISTING RESOURCES                                      NEW RESOURCES
             BROWNFIELD                                             GREENFIELD
                 |                                                       |
                 |                                                       |
       Cloud Asset Inventory                                  Cloud Audit Logs
                 |                                                       |
                 |                                            Organisation Log Sink
                 |                                                       |
                 |                                                  Pub/Sub
                 |                                                       |
                 |                                                   Eventarc
                 |                                                       |
                 +--------------------------+----------------------------+
                                            |
                                            v
                                  +-------------------+
                                  |     Cloud Run     |
                                  | metadata-governance|
                                  +-------------------+
                                            |
             +------------------------------+------------------------------+
             |                              |                              |
             v                              v                              v
     Application Registry             Governance Services             Dashboard/API
       Cloud Storage                  Compliance Engine
                                      Capability Engine
                                      Planner/Executor
                                            |
                                            v
                                      Cloud Tasks
                                            |
                                            v
                                       /worker
                                            |
                                            v
                                   Resource Adapters
                                            |
                                            v
                                     Native GCP APIs
                                            |
                                            v
                                        BigQuery
                                            |
                     +----------------------+----------------------+
                     |                                             |
                Audit Evidence                               Reporting APIs
                                                                  |
                                                                  v
                                                              Dashboard
```

---

## 4. Dedicated Governance Projects

### 4.1 Development

The current Terraform configuration targets:

```text
platform-metadata-dev
```

The project is resolved through Terraform remote state rather than directly hardcoding the underlying generated project ID into the Google provider.

The development environment is used for:

- infrastructure development
- application development
- registry validation
- Cloud Run deployment testing
- Greenfield event validation
- Brownfield remediation testing
- IAM validation
- resource-adapter testing
- dashboard development
- controlled scale testing

### 4.2 Production

The target production control plane is:

```text
platform-metadata-prod
```

Production should reproduce the validated architecture using environment-specific:

- Terraform state
- service account
- Cloud Run service
- Artifact Registry
- registry bucket
- BigQuery dataset
- Pub/Sub/Eventarc infrastructure
- Cloud Tasks queue
- Workload Identity Federation configuration
- authorised dashboard users
- IAM bindings

Development resources must not be reused as production dependencies.

---

## 5. Infrastructure as Code

Google Cloud infrastructure is managed with Terraform.

The supplied Terraform lock file pins:

```text
hashicorp/google      7.41.0
hashicorp/google-beta 7.41.0
```

### 5.1 Terraform state

The development environment uses a GCS backend:

```text
bucket = terraform-admin-state-bucket
prefix = infrastructure/platform-metadata-dev
```

Project structure and Terraform administration information are consumed from separate remote-state locations.

### 5.2 Infrastructure/application deployment boundary

Terraform creates the Cloud Run service with a placeholder container image.

The Cloud Run Terraform lifecycle deliberately ignores:

```text
container image
container environment variables
```

This creates an intentional deployment boundary:

- **Terraform** owns the underlying platform infrastructure.
- **GitHub Actions / CI-CD** owns application image deployment and runtime application configuration.

This boundary must be preserved operationally so Terraform does not roll back an application release to the placeholder image.

---

## 6. Enabled Platform APIs

The Terraform platform enables the following Google Cloud APIs:

| API | Platform Purpose |
| --- | --- |
| Cloud Run | Governance runtime and dashboard |
| Eventarc | Event delivery into the governance runtime |
| Cloud Tasks | Asynchronous remediation execution |
| Pub/Sub | Greenfield event transport |
| Artifact Registry | Governance container images |
| BigQuery | Compliance, remediation and reporting data |
| Cloud Asset Inventory | Brownfield discovery |
| IAM Credentials | Workload Identity Federation token generation |

API resources are configured with `disable_on_destroy = false` so destroying the Terraform resource does not automatically disable the underlying Google API.

---

## 7. Cloud Run Runtime

The primary runtime service is:

```text
metadata-governance
```

The current development deployment region is:

```text
us-central1
```

### 7.1 Scaling

Terraform configures:

```text
minimum instances = 0
maximum instances = 10
```

The minimum of zero allows the runtime to scale to zero when idle.

The maximum provides a control against unbounded runtime scaling while still allowing parallel processing during higher activity.

### 7.2 Runtime responsibilities

The Cloud Run application provides the central execution layer for:

- Brownfield orchestration
- Greenfield event processing
- registry access
- compliance evaluation
- remediation planning
- resource-adapter dispatch
- Cloud Tasks worker execution
- reporting APIs
- governance dashboard

### 7.3 Ingress and authentication

The current Terraform service uses:

```text
INGRESS_TRAFFIC_ALL
```

Access is still controlled by Cloud Run IAM.

Named authorised users receive:

```text
roles/run.invoker
```

The governance service account also receives Cloud Run Invoker so Eventarc can deliver events to the service.

For production, dashboard authentication and machine-to-machine endpoints must remain explicitly controlled and reviewed as part of the security design.

---

## 8. Application Registry

The Application Registry is stored in Cloud Storage.

The development Terraform deployment creates:

```text
rouse-platform-metadata-registry-dev
```

The bucket uses:

```text
uniform_bucket_level_access = true
force_destroy = false
```

Application metadata is maintained independently from runtime source code.

The runtime registry layer loads and caches the application definitions.

The registry is used to resolve governance context such as:

- application/product
- team
- owner
- budget owner
- organisation
- department
- cost centre
- GCP project binding
- environment
- region
- business criticality

This prevents application-specific governance values from being embedded in resource adapters.

---

## 9. Brownfield Architecture

Brownfield governance processes existing resources.

### 9.1 Processing flow

```text
Brownfield Request
       |
       v
Determine Project Scope
       |
       v
Cloud Asset Inventory
       |
       v
Resource Discovery
       |
       v
Live Metadata Enrichment
       |
       v
Application Registry Resolution
       |
       v
Capability Validation
       |
       v
Compliance Evaluation
       |
       v
Remediation Planning
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
Native GCP Update API
       |
       v
BigQuery Execution Evidence
```

### 9.2 Organisation scope

The application supports organisation-scope Brownfield processing by obtaining the set of active projects visible to the governance runtime.

The dedicated governance project itself must be excluded from unintended remediation.

### 9.3 Discovery

Cloud Asset Inventory provides the scalable discovery layer.

Discovery is separated from resource-specific mutation logic.

Where necessary, resource clients obtain live service metadata before compliance or mutation.

### 9.4 Compliance

The compliance layer compares current resource metadata against the metadata required by the Application Registry.

Resources that are already compliant do not require remediation.

### 9.5 Planning

Non-compliant resources requiring a change are converted into remediation-plan records.

The platform persists plans before execution so planned and completed work can be audited separately.

### 9.6 Batched execution

Brownfield remediation uses Cloud Tasks.

The current application default is:

```text
REMEDIATION_BATCH_SIZE = 500
```

Therefore:

```text
1,000,000 remediation actions
÷ 500 actions per batch
≈ 2,000 Cloud Tasks batches
```

before retries or ancillary operations.

The architecture does not require one Cloud Task per resource.

### 9.7 Worker

Cloud Tasks invokes the application worker endpoint.

The worker processes remediation actions through the appropriate resource adapter and records execution evidence.

---

## 10. Greenfield Architecture

Greenfield governance processes newly created resources using events.

### 10.1 Organisation event path

The intended enterprise event path is:

```text
Workload Project
      |
      v
Cloud Audit Logs
      |
      v
Organisation-Level Log Sink
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
Event Parsing / Classification
      |
      v
Capability Validation
      |
      v
Compliance / Remediation
      |
      v
BigQuery Evidence
```

The central Pub/Sub topic is:

```text
metadata-governance-events
```

A standard subscription is also provisioned:

```text
metadata-governance-sub
```

The Eventarc trigger is:

```text
metadata-governance-trigger
```

and matches:

```text
google.cloud.pubsub.topic.v1.messagePublished
```

### 10.2 Organisation-level requirement

For central Greenfield governance, audit events must originate from the governed workload projects and be routed to the central governance event transport.

Creating an Eventarc trigger only inside the governance project does not independently discover resource creation across unrelated projects.

The organisation-level log-routing layer is therefore a critical part of the enterprise Greenfield design.

### 10.3 Classification

Incoming audit events are parsed and mapped into canonical resource events.

Resource-specific classifiers/extractors determine:

- service
- creation method
- project
- resource identifier
- asset type

### 10.4 Greenfield support criteria

A resource type should be declared Greenfield-supported only when all of the following have been validated:

1. The exact creation audit event is known.
2. The organisation event-routing filter captures that event.
3. The event reaches the central Pub/Sub/Eventarc path.
4. The classifier maps it correctly.
5. The asset type is enabled by platform capability configuration.
6. The resource adapter can safely read and update metadata.
7. Runtime IAM contains the required permissions.
8. Retry and duplicate-delivery behaviour is safe.
9. Execution evidence is recorded successfully.

Code presence alone is not sufficient.

---

## 11. Messaging and Asynchronous Processing

### 11.1 Pub/Sub

Terraform provisions:

```text
Topic:        metadata-governance-events
Subscription: metadata-governance-sub
```

Pub/Sub decouples organisation audit-log routing from the Cloud Run runtime.

### 11.2 Eventarc

Eventarc delivers Pub/Sub message-published events to Cloud Run.

The Eventarc trigger runs as the governance service account.

That identity requires both the appropriate Eventarc receiver permissions and permission to invoke the destination Cloud Run service.

### 11.3 Cloud Tasks

Terraform provisions:

```text
metadata-remediation
```

Cloud Tasks is used for controlled asynchronous Brownfield remediation rather than synchronous processing of an entire enterprise estate inside one HTTP request.

---

## 12. BigQuery Data Architecture

The development environment creates the dataset:

```text
metadata_governance
```

The dataset is located in the configured platform region.

Four core tables are provisioned.

### 12.1 `resource_snapshot`

Stores discovered resource inventory.

Important fields include:

- `run_id`
- `snapshot_time`
- `project_id`
- `asset_type`
- `resource_name`
- `location`
- `labels`
- `tags`

### 12.2 `compliance_snapshot`

Stores compliance evaluation results.

Important fields include:

- `run_id`
- `evaluated_time`
- `project_id`
- `asset_type`
- `resource_name`
- `compliant`
- `missing_labels`
- `incorrect_labels`

### 12.3 `remediation_plan`

Stores planned remediation work.

Important fields include:

- `run_id`
- `project_id`
- `asset_type`
- `resource_name`
- `missing_labels`
- `planned_labels`
- `planned_tags`
- `status`
- `created_at`

### 12.4 `remediation_execution`

Stores remediation execution evidence.

Important fields include:

- `execution_id`
- `run_id`
- `project_id`
- `asset_type`
- `resource_name`
- `managed_labels`
- `status`
- `error_message`
- `executed_at`
- `execution_mode`
- `service_name`
- `method_name`
- `duration_ms`

The execution mode allows Brownfield and Greenfield activity to be differentiated.

### 12.5 Clustering

The four operational tables are clustered using:

```text
project_id
asset_type
run_id
```

where configured in Terraform.

This supports common project/resource/run reporting patterns.

---

## 13. Dashboard and Reporting

The governance dashboard is served by the same Cloud Run application.

Reporting data is sourced from BigQuery rather than static dashboard values.

The reporting layer supports views such as:

- executive summary
- Brownfield summary
- Greenfield summary
- project view
- resource-type view
- compliance metrics
- remediation activity
- recent runs
- recent execution activity
- non-compliant resources

Human access to the Cloud Run service is controlled through IAM.

---

## 14. Artifact Registry and Application Delivery

Terraform provisions the Docker repository:

```text
metadata-governance
```

The repository is hosted in the configured region.

The intended deployment lifecycle is:

```text
Source Repository
      |
      v
GitHub Actions
      |
      v
Workload Identity Federation
      |
      v
Google Service Account
      |
      v
Container Build / Push
      |
      v
Artifact Registry
      |
      v
Cloud Run Revision
```

Terraform creates the platform service, while CI-CD deploys the real application image.

---

## 15. Workload Identity Federation

GitHub Actions authenticates to Google Cloud using Workload Identity Federation rather than a long-lived service-account key.

The Terraform configuration creates:

```text
Pool:     github-actions-pool
Provider: github-provider
```

The provider trusts GitHub's OIDC issuer:

```text
https://token.actions.githubusercontent.com
```

Access is restricted to the repository:

```text
RouseServices/platform-metadata
```

through both:

- the provider attribute condition
- the service-account principal binding

This prevents arbitrary GitHub repositories from impersonating the deployment identity.

The repository principal receives Workload Identity User access to the governance service account and the token-generation permission required by the current deployment flow.

---

## 16. Service Account and IAM Architecture

The primary runtime identity is:

```text
metadata-governance
```

The same service account currently participates in runtime and event-delivery responsibilities in the development implementation.

### 16.1 Governance-project permissions

The Terraform configuration assigns project-level permissions required for platform functions including:

- BigQuery data access
- BigQuery job execution
- Cloud Tasks enqueue
- registry object administration
- Pub/Sub access
- logging visibility
- Secret Manager access
- Artifact Registry operations
- Cloud Run deployment/runtime operations
- service-account impersonation/token operations
- Eventarc event receipt

### 16.2 Organisation-level permissions

Organisation-level permissions provide:

- project/resource discovery
- Cloud Asset Inventory visibility
- metadata remediation capabilities across governed projects

A custom organisation role is used for resource-specific metadata mutation.

### 16.3 Production IAM principle

The production custom role must be aligned with resource types that are actually enabled.

Do not grant every possible resource mutation permission merely because corresponding adapter code exists.

---

## 17. Resource Capability Architecture

The application contains resource-specific clients/adapters for multiple GCP services.

However:

```text
Adapter exists != Resource enabled
```

The capability configuration is authoritative.

A resource type should only be promoted to production support after:

- metadata support is confirmed
- Brownfield discovery is validated
- live read behaviour is validated
- mutation behaviour is validated
- least-privilege IAM is identified
- error handling is tested
- retry/idempotency is tested
- BigQuery evidence is validated
- Greenfield creation-event routing is validated where Greenfield is supported

This protects the platform from accidentally exposing partially implemented resource integrations.

---

## 18. Security Architecture

The security model uses several layers.

### 18.1 Dedicated control plane

Governance infrastructure is isolated in dedicated projects.

### 18.2 IAM-authenticated Cloud Run

Cloud Run invocation is controlled using IAM.

### 18.3 Keyless CI-CD

GitHub Actions uses Workload Identity Federation rather than stored Google Cloud service-account keys.

### 18.4 Repository restriction

The WIF provider is restricted to the approved GitHub repository.

### 18.5 Registry bucket controls

Uniform bucket-level access is enabled.

The registry bucket is not configured for force destruction.

### 18.6 Environment separation

Development and production must use separate:

- projects
- service accounts
- registry data
- BigQuery data
- event infrastructure
- queues
- deployment identities/access
- authorised users

### 18.7 Least-privilege remediation

Resource mutation permissions should follow enabled capabilities.

---

## 19. Availability and Scalability

The platform uses managed Google Cloud services.

### Cloud Run

- scales from zero
- currently capped at 10 instances in development
- removes the need to manage servers

### Cloud Tasks

- decouples large Brownfield sweeps from request lifetime
- supports controlled asynchronous execution
- provides retry behaviour

### Pub/Sub/Eventarc

- decouples organisation audit-event production from application processing
- supports event-driven Greenfield governance

### Cloud Asset Inventory

- provides enterprise-scale resource discovery without maintaining a custom inventory crawler

### BigQuery

- provides scalable governance history and reporting storage

---

## 20. Cost Architecture

The architecture is consumption-based.

Primary variable-cost components are:

- Cloud Run execution
- Cloud Tasks operations
- Pub/Sub/Eventarc event processing
- BigQuery storage and queries
- Cloud Logging/log routing volume
- Cloud Storage registry operations

The design avoids permanently running VM-based remediation workers.

Greenfield processing cost is primarily driven by relevant event volume.

Brownfield cost is primarily driven by discovery frequency, resources evaluated, remediation workload, runtime duration and reporting/query activity.

Production cost estimates should be based on measured development telemetry rather than fixed per-resource assumptions.

---

## 21. Operational Boundaries

Ownership is intentionally divided.

| Component | Primary Ownership |
| --- | --- |
| GCP project/infrastructure | Terraform |
| APIs | Terraform |
| Cloud Run base service | Terraform |
| Cloud Run application image | CI-CD |
| Runtime application environment | CI-CD / deployment configuration |
| BigQuery dataset/tables | Terraform |
| Pub/Sub | Terraform |
| Eventarc | Terraform |
| Cloud Tasks | Terraform |
| WIF | Terraform |
| Application Registry content | Registry governance process |
| Resource capability enablement | Application/platform release process |
| Application logic | Source repository |
| Reporting/dashboard logic | Source repository |

This ownership model should be preserved to avoid configuration drift between Terraform and application deployment pipelines.

---

## 22. Production Architecture Requirements

Before promotion to `platform-metadata-prod`, validate:

- production Terraform backend/state
- dedicated production governance service account
- production registry bucket
- production BigQuery dataset/tables
- production Artifact Registry
- production Cloud Tasks queue
- production Pub/Sub/Eventarc path
- organisation log sink routing
- dashboard authorisation
- internal endpoint authentication
- WIF production deployment trust
- enabled capability list
- custom remediation IAM role
- project and resource exclusions
- Brownfield representative-scale test
- Greenfield event tests for every enabled type
- duplicate-event/idempotency behaviour
- retry behaviour
- BigQuery audit evidence
- monitoring and alerts
- budget controls
- rollback procedure
- operational runbook

---

## 23. Architecture Summary

The Enterprise Metadata Governance Platform provides a centralised Google Cloud governance control plane using managed and serverless services.

The architecture combines:

```text
Cloud Asset Inventory
Cloud Audit Logs
Cloud Logging
Pub/Sub
Eventarc
Cloud Run
Cloud Tasks
Cloud Storage
BigQuery
Artifact Registry
IAM
Workload Identity Federation
Terraform
GitHub Actions
```

Brownfield governance provides scalable discovery and asynchronous remediation for existing resources.

Greenfield governance provides event-driven detection and remediation for newly created resources.

A central Application Registry supplies governance metadata, while capability controls determine which resource types are allowed to execute.

The architecture is designed to provide:

- centralised governance
- near-real-time Greenfield compliance
- scalable Brownfield processing
- zero-idle serverless runtime
- auditable remediation
- controlled resource enablement
- keyless CI-CD
- development/production isolation
- enterprise-scale extensibility

---

## 24. Related Documentation

The following documents form the remaining documentation set:

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

`ARCHITECTURE.md` is the parent architecture document. The remaining documents provide implementation and operational detail for each platform area.
