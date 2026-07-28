# Enterprise Metadata Governance Platform - Deployment Guide

## 1. Purpose

This document defines the deployment model for the Enterprise Metadata Governance Platform on Google Cloud.

It covers the separation between infrastructure provisioning and application delivery, the development-to-production promotion model, Terraform state, required platform components, CI-CD authentication, deployment validation and rollback considerations.

The deployment model uses two dedicated governance control-plane projects:

| Environment | Governance Project | Purpose |
| --- | --- | --- |
| Development | `platform-metadata-dev` | Development, integration, Greenfield event testing, Brownfield testing, adapter validation, dashboard testing and controlled scale validation |
| Production | `platform-metadata-prod` | Production organisation-wide metadata governance, remediation, audit and reporting |

Development and production must remain independently deployable and must not share runtime identities, queues, event infrastructure, registry data or BigQuery governance data.

---

## 2. Deployment Ownership Model

The platform deliberately separates infrastructure deployment from application deployment.

| Layer | Deployment Mechanism | Responsibility |
| --- | --- | --- |
| Governance project | Terraform / upstream project provisioning | Dedicated control-plane project |
| Enabled Google APIs | Terraform | Required service APIs |
| Artifact Registry | Terraform | Container repository |
| Cloud Run base service | Terraform | Runtime infrastructure |
| Cloud Run application image | GitHub Actions / CI-CD | Application release |
| Cloud Run runtime environment | CI-CD / deployment configuration | Application-specific runtime values |
| Cloud Tasks | Terraform | Brownfield remediation queue |
| Pub/Sub | Terraform | Greenfield event transport |
| Eventarc | Terraform | Event delivery to Cloud Run |
| Organisation log sink | Terraform | Cross-project Greenfield audit-event routing |
| BigQuery | Terraform | Governance dataset and tables |
| Registry bucket | Terraform | Registry storage infrastructure |
| Registry YAML | Registry release process | Application metadata |
| IAM | Terraform | Runtime, deployment and organisation access |
| Workload Identity Federation | Terraform | Keyless GitHub authentication |
| Dashboard/application code | GitHub Actions / CI-CD | Cloud Run revision |

### Important Cloud Run ownership boundary

Terraform creates the Cloud Run service with a bootstrap/placeholder image.

The Terraform lifecycle configuration intentionally ignores changes to:

```text
container image
container environment variables
```

The deployed application image and application runtime configuration are therefore owned by the CI-CD deployment process.

Do not remove this lifecycle boundary without redesigning deployment ownership. Otherwise, a later Terraform apply could overwrite a CI-CD application release.

---

## 3. Terraform Provider and State

The supplied Terraform dependency lock uses:

```text
hashicorp/google      7.41.0
hashicorp/google-beta 7.41.0
```

Terraform should be executed using the provider versions locked by `.terraform.lock.hcl` unless an explicit provider upgrade is being performed and tested.

### 3.1 Development backend

The current development backend uses Google Cloud Storage:

```hcl
bucket = "terraform-admin-state-bucket"
prefix = "infrastructure/platform-metadata-dev"
```

The state location must be protected because Terraform state can contain sensitive infrastructure metadata.

### 3.2 Production backend

Production must use a separate state prefix, for example:

```text
infrastructure/platform-metadata-prod
```

Do not use the development Terraform state for production.

### 3.3 Remote state dependencies

The Terraform configuration consumes remote state for shared project/administrative information.

Before deployment, confirm that:

- the backend bucket exists
- the deployment identity can read/write the appropriate state
- referenced remote-state outputs exist
- the resolved governance project is the intended environment
- development state cannot accidentally target production resources

---

## 4. Deployment Prerequisites

Before deploying an environment, confirm the following.

### 4.1 Google Cloud prerequisites

- Dedicated governance project exists.
- Billing is enabled.
- Terraform state backend exists.
- Organisation ID is available.
- Required parent/folder/project structure exists.
- Terraform deployment identity has the required infrastructure-management permissions.
- GitHub repository and branch strategy are approved.
- Organisation-level log-routing permissions are available for Greenfield deployment.

### 4.2 Repository prerequisites

The deployment repository should contain, at minimum:

```text
Terraform
├── backend.tf
├── project.tf
├── apis.tf
├── data.tf
├── iam.tf
├── messaging.tf
├── log_sink.tf
├── dashboard.tf
├── wif.tf
└── .terraform.lock.hcl

Application
├── cloudrun/
├── registry/
├── validation/
├── Dockerfile
├── cloudbuild.yaml
└── README.md

Documentation
└── docs/
```

File organisation may evolve, but infrastructure ownership boundaries should remain clear.

---

## 5. Required Google Cloud APIs

Terraform enables the platform APIs required by the deployed architecture.

The deployment includes APIs for:

- Cloud Run
- Eventarc
- Cloud Tasks
- Pub/Sub
- Artifact Registry
- BigQuery
- Cloud Asset Inventory
- IAM Credentials

The Terraform API resources use:

```text
disable_on_destroy = false
```

This prevents a Terraform destroy from automatically disabling APIs that may have dependencies outside the individual Terraform resource.

Before troubleshooting a failed deployment, verify that the relevant API has reached the enabled state.

---

## 6. Infrastructure Deployment Sequence

The recommended deployment sequence is:

```text
1. Resolve governance project
2. Initialise Terraform backend
3. Validate Terraform
4. Review Terraform plan
5. Enable required APIs
6. Create platform service account
7. Create Artifact Registry
8. Create registry bucket
9. Create BigQuery dataset/tables
10. Create Cloud Tasks queue
11. Create Pub/Sub infrastructure
12. Create organisation log routing
13. Create Cloud Run base service
14. Create Eventarc trigger
15. Configure project/organisation IAM
16. Configure Workload Identity Federation
17. Deploy application image through CI-CD
18. Deploy/validate registry
19. Validate Brownfield
20. Validate Greenfield
21. Validate dashboard/reporting
```

Terraform dependency relationships may execute some resources in parallel. The sequence above describes the logical deployment order and validation checkpoints.

---

## 7. Terraform Initialisation and Validation

Run Terraform from the environment-specific infrastructure directory.

### 7.1 Initialise

```bash
terraform init
```

For a new backend or changed backend configuration:

```bash
terraform init -reconfigure
```

### 7.2 Format validation

```bash
terraform fmt -check -recursive
```

To correct formatting:

```bash
terraform fmt -recursive
```

### 7.3 Configuration validation

```bash
terraform validate
```

Do not continue to production planning if validation fails.

---

## 8. Terraform Plan

Generate and review a plan before applying changes.

```bash
terraform plan -out=tfplan
```

Review the plan for:

- governance project
- organisation ID
- region
- service accounts
- IAM changes
- Cloud Run changes
- Pub/Sub/Eventarc changes
- organisation log sink
- BigQuery schema changes
- Cloud Tasks changes
- registry bucket changes
- WIF trust configuration

For production, the plan should be retained as deployment evidence according to the client's change-management process.

### Critical checks

Confirm that the plan does not:

- target the wrong governance project
- delete the registry bucket
- delete governance history unexpectedly
- broaden WIF trust beyond the approved repository
- grant unapproved organisation-level permissions
- replace Cloud Run unexpectedly
- remove Greenfield event routing
- alter Terraform backend/state

---

## 9. Terraform Apply

After review and approval:

```bash
terraform apply tfplan
```

For controlled environments, avoid routine use of:

```bash
terraform apply -auto-approve
```

Production changes should follow the client's approval/change process.

After apply, retain:

- Terraform plan
- Terraform apply result
- commit SHA
- deployment identity
- deployment timestamp
- environment
- relevant change/request reference

---

## 10. Artifact Registry

Terraform creates the governance Docker repository:

```text
metadata-governance
```

The application image should be versioned using an immutable release identifier such as:

```text
commit SHA
release version
```

Avoid relying only on mutable tags such as `latest` for production traceability.

Recommended pattern:

```text
<region>-docker.pkg.dev/<project>/metadata-governance/metadata-governance:<commit-sha>
```

The exact project and region must come from environment deployment configuration rather than application hardcoding.

---

## 11. Cloud Run Base Deployment

The Cloud Run service is:

```text
metadata-governance
```

The current development infrastructure is deployed in:

```text
us-central1
```

Terraform configures the base runtime and scaling boundary.

Current development scaling:

```text
min instances = 0
max instances = 10
```

`min instances = 0` allows scale-to-zero behaviour.

The actual application image is subsequently deployed by CI-CD.

---

## 12. GitHub Actions Authentication

GitHub Actions uses Google Cloud Workload Identity Federation.

Terraform creates:

```text
Workload Identity Pool:
github-actions-pool

Provider:
github-provider
```

The provider uses GitHub's OIDC issuer:

```text
https://token.actions.githubusercontent.com
```

Trust is restricted to:

```text
RouseServices/platform-metadata
```

The restriction exists at the provider condition and service-account principal binding.

### Security requirement

Do not replace WIF with a long-lived downloaded service-account JSON key.

Do not broaden the WIF principal to all GitHub repositories.

Production should use an explicitly reviewed trust configuration and deployment workflow.

---

## 13. Application CI-CD Deployment

After Terraform has created the base infrastructure, the application pipeline should:

```text
Checkout source
      |
      v
Authenticate through GitHub OIDC/WIF
      |
      v
Build container
      |
      v
Push immutable image
      |
      v
Deploy Cloud Run revision
      |
      v
Set environment-specific runtime configuration
      |
      v
Wait for revision readiness
      |
      v
Run smoke tests
```

### Application deployment must not create infrastructure drift

CI-CD may update the Cloud Run application image and runtime environment because Terraform intentionally ignores those fields.

CI-CD should not independently recreate Terraform-owned:

- Pub/Sub topics
- Eventarc triggers
- Cloud Tasks queues
- BigQuery datasets/tables
- IAM roles/bindings
- WIF resources
- registry bucket
- organisation log sink

unless deployment ownership is intentionally redesigned.

---

## 14. Runtime Configuration

The application requires environment-specific configuration.

Mandatory application configuration includes:

| Variable | Purpose |
| --- | --- |
| `PROJECT_ID` | Governance control-plane project |
| `REGION` | Platform runtime region |
| `TAG_PARENT` | Resource Manager Tag parent when tag capability is used |
| `TASK_QUEUE` | Brownfield remediation queue |
| `CLOUD_RUN_URL` | Deployed governance service URL |
| `SERVICE_ACCOUNT_EMAIL` | Runtime service-account identity |
| `REGISTRY_BUCKET` | Application Registry bucket |
| `REGISTRY_PREFIX` | Registry object prefix |
| `BIGQUERY_DATASET` | Governance BigQuery dataset |

Application tuning includes values such as:

```text
REGISTRY_CACHE_TTL
DISCOVERY_RETENTION_DAYS
MAX_PARALLEL_WORKERS
REMEDIATION_BATCH_SIZE
LOG_LEVEL
DRY_RUN
PRESERVE_EXISTING_LABELS
EXCLUDED_PROJECTS
EXCLUDED_BUCKETS
```

Environment-specific values must be supplied by deployment configuration.

Do not embed development or production project IDs, URLs, bucket names or service-account addresses inside application business logic.

---

## 15. Application Registry Deployment

The registry is stored in the governance Cloud Storage bucket.

Development currently uses:

```text
rouse-platform-metadata-registry-dev
```

The registry deployment process should be independent from container deployment.

Recommended flow:

```text
Registry change
      |
      v
Schema validation
      |
      v
Duplicate binding validation
      |
      v
Peer/change review
      |
      v
Upload to DEV registry
      |
      v
Functional validation
      |
      v
Production approval
      |
      v
Upload to PROD registry
```

Do not promote invalid registry YAML.

Registry validation should fail the pipeline when:

- required fields are missing
- environment values are invalid
- project bindings are duplicated
- schema validation fails

---

## 16. BigQuery Deployment

Terraform provisions the governance dataset:

```text
metadata_governance
```

and the core tables:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

Before application deployment, verify that all required tables exist and their schemas match the application repository.

### Schema change rule

Application code and BigQuery schema changes must be coordinated.

Do not deploy application code that writes a new required field before the target BigQuery schema supports it.

For destructive schema changes:

1. assess existing data
2. create a migration plan
3. test in DEV
4. back up/export where required
5. deploy schema change
6. deploy compatible application revision
7. validate reporting

---

## 17. Cloud Tasks Deployment

The remediation queue is:

```text
metadata-remediation
```

The queue must exist before Brownfield remediation execution.

After deployment, verify:

- queue exists
- queue region is correct
- runtime can enqueue tasks
- worker authentication succeeds
- Cloud Run can receive worker requests
- retries behave as expected

Brownfield should initially be validated using a small project scope before organisation-wide execution.

---

## 18. Pub/Sub and Eventarc Deployment

Terraform creates:

```text
Topic:
metadata-governance-events

Subscription:
metadata-governance-sub

Eventarc trigger:
metadata-governance-trigger
```

The Eventarc trigger listens for:

```text
google.cloud.pubsub.topic.v1.messagePublished
```

and delivers events to:

```text
metadata-governance
```

After deployment, validate the complete path rather than checking only whether the resources exist.

A healthy Eventarc trigger does not prove organisation Greenfield routing is working.

---

## 19. Organisation Log Sink Deployment

Greenfield governance depends on organisation-level Cloud Audit Log routing.

The log sink must route the intended creation events from governed workload projects to the central Pub/Sub topic.

The sink's writer identity must have permission to publish to:

```text
metadata-governance-events
```

### Required validation

After sink deployment:

1. create a supported test resource in a workload project
2. confirm its Admin Activity audit event exists
3. confirm the event matches the sink filter
4. confirm Pub/Sub receives the routed event
5. confirm Eventarc delivers it
6. confirm Cloud Run logs show event processing
7. confirm classifier output
8. confirm remediation result
9. confirm `remediation_execution` contains the Greenfield evidence

Do not validate Greenfield only by creating a resource inside the governance project.

The purpose of organisation routing is to capture events from governed workload projects.

---

## 20. IAM Deployment

IAM is provisioned through Terraform.

The platform includes:

- governance-project IAM
- organisation-level discovery IAM
- custom organisation remediation permissions
- Eventarc receiver/invoker access
- Pub/Sub publishing/access
- Cloud Tasks access
- BigQuery access
- registry access
- Artifact Registry access
- WIF impersonation/token access
- authorised human Cloud Run invocation

### Production rule

The production remediation role must be based on the active supported-resource capability list.

Do not automatically grant all mutation permissions represented anywhere in the code repository.

IAM changes require security review because organisation-level remediation permissions can affect workload projects.

Detailed permissions are maintained in:

```text
docs/IAM.md
```

---

## 21. Development Deployment Validation

Before promoting any change, validate it in:

```text
platform-metadata-dev
```

Minimum checks:

### Infrastructure

```text
[ ] Terraform apply successful
[ ] Required APIs enabled
[ ] Cloud Run service healthy
[ ] Artifact Registry available
[ ] Registry bucket available
[ ] BigQuery tables available
[ ] Cloud Tasks queue available
[ ] Pub/Sub available
[ ] Eventarc trigger active
[ ] Organisation sink configured
[ ] IAM bindings present
[ ] WIF authentication works
```

### Application

```text
[ ] New Cloud Run revision healthy
[ ] /health succeeds
[ ] Registry loads successfully
[ ] Dashboard loads for authorised user
[ ] Reporting APIs return valid responses
[ ] No unexpected startup errors
```

### Brownfield

```text
[ ] Small project discovery succeeds
[ ] Registry binding resolves
[ ] Compliance evaluation succeeds
[ ] Remediation plan is created
[ ] Cloud Task is created
[ ] Worker executes
[ ] Target metadata is updated
[ ] BigQuery execution evidence is written
```

### Greenfield

```text
[ ] Supported resource created in workload DEV project
[ ] Audit event exists
[ ] Organisation sink matches event
[ ] Pub/Sub receives event
[ ] Eventarc delivers event
[ ] Classifier recognises resource
[ ] Capability gate permits resource
[ ] Remediation executes
[ ] BigQuery records GREENFIELD execution
```

---

## 22. Production Promotion

Production deployment should occur only after DEV validation.

Recommended promotion sequence:

```text
1. Merge approved application/infrastructure changes
2. Record release commit SHA
3. Generate production Terraform plan
4. Review organisation/IAM changes
5. Approve change
6. Apply production Terraform
7. Validate production infrastructure
8. Build immutable application image
9. Deploy production Cloud Run revision
10. Validate health
11. Promote approved registry
12. Run read-only/small-scope validation
13. Validate Greenfield event path
14. Validate BigQuery/reporting
15. Enable broader Brownfield scope
16. Monitor
17. Close change after evidence review
```

Do not promote untested resource capabilities directly into production.

---

## 23. Brownfield Deployment Safety

For a newly deployed production environment:

1. confirm exclusions
2. confirm registry bindings
3. confirm active supported resources
4. start with a single project
5. use dry-run where appropriate
6. review planned remediation
7. execute a limited batch
8. verify target metadata
9. verify BigQuery evidence
10. increase scope gradually
11. perform organisation-wide execution only after validation

Large Brownfield execution should not be the first production test.

---

## 24. Greenfield Deployment Safety

For each resource type:

1. identify exact creation audit event
2. test organisation sink filter
3. verify Pub/Sub delivery
4. verify Eventarc delivery
5. verify classifier
6. verify capability enablement
7. verify registry resolution
8. verify adapter mutation
9. verify duplicate-event safety
10. verify BigQuery evidence
11. enable in production

Do not use a generic assumption that all `*.insert` or `*.create` methods have identical Audit Log structures.

---

## 25. Smoke Tests

Immediately after application deployment, perform smoke checks.

Example:

```bash
gcloud run services describe metadata-governance \
  --region=<REGION> \
  --project=<GOVERNANCE_PROJECT>
```

Confirm the deployed revision and service health.

Where authenticated invocation is permitted:

```bash
curl -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  "<CLOUD_RUN_URL>/health"
```

Expected result:

```text
HTTP 200
```

Additional smoke tests should verify:

- registry connectivity
- BigQuery connectivity
- dashboard/reporting
- Cloud Tasks enqueue
- event processing

Use environment variables or deployment outputs for real project, region and service URL values rather than copying fixed DEV values into scripts.

---

## 26. Rollback - Application

Application rollback is performed at the Cloud Run revision level.

If a newly deployed revision fails:

1. stop further promotion
2. identify last known-good revision/image
3. route traffic back to the known-good revision
4. verify `/health`
5. verify dashboard/reporting
6. verify worker execution
7. investigate failed release
8. retain logs and release evidence

Because application images should use immutable tags, the exact prior image can be identified from deployment history.

---

## 27. Rollback - Terraform

Infrastructure rollback requires more care than application rollback.

Do not blindly revert Terraform and apply without reviewing resource lifecycle impact.

For an infrastructure failure:

1. preserve current state
2. inspect failed apply
3. review Terraform state
4. identify affected resources
5. generate a corrective plan
6. review destructive actions
7. apply only after approval

Special care is required for:

- BigQuery tables
- registry bucket
- organisation log sink
- IAM
- WIF
- Pub/Sub
- Eventarc
- Cloud Run service

State manipulation commands such as `terraform state rm`, `terraform import` or manual state recovery should be performed only by authorised platform engineers with a documented recovery plan.

---

## 28. Post-Deployment Monitoring

After deployment, monitor:

- Cloud Run startup/runtime errors
- revision health
- request failures
- worker failures
- Cloud Tasks retries
- Pub/Sub/Eventarc delivery errors
- Greenfield unsupported events
- registry failures
- BigQuery write/query failures
- API quota/rate-limit failures
- remediation failures
- compliance trends

A deployment should not be considered complete solely because Terraform and CI-CD returned success.

Functional governance evidence must also be verified.

---

## 29. Deployment Evidence

For client production deployments, retain:

```text
Environment
Change reference
Git commit SHA
Terraform plan
Terraform apply result
Container image digest/tag
Cloud Run revision
Registry version/change
Deployment timestamp
Deployment identity
Validation results
Brownfield test evidence
Greenfield test evidence
Rollback revision
Approver
```

This provides traceability between infrastructure, source code, runtime revision and governance behaviour.

---

## 30. Deployment Anti-Patterns

Do not:

- deploy production from a developer workstation without the approved process
- share DEV and PROD Terraform state
- reuse the DEV runtime service account in PROD
- store Google service-account JSON keys in GitHub
- broaden WIF to arbitrary repositories
- manually create Terraform-owned resources without reconciling state
- hardcode environment project IDs in application logic
- let Terraform overwrite CI-CD-owned Cloud Run image changes
- enable a resource capability only because an adapter exists
- run organisation-wide Brownfield as the first production test
- assume an Eventarc trigger alone provides organisation-wide Greenfield detection
- change BigQuery schemas without checking application compatibility
- grant all candidate remediation permissions by default

---

## 31. Deployment Checklist

### Pre-deployment

```text
[ ] Correct environment selected
[ ] Correct Terraform backend selected
[ ] Correct governance project resolved
[ ] Correct organisation ID resolved
[ ] terraform fmt passes
[ ] terraform validate passes
[ ] Terraform plan reviewed
[ ] IAM changes reviewed
[ ] WIF trust reviewed
[ ] BigQuery schema changes reviewed
[ ] Capability changes reviewed
[ ] Registry changes validated
[ ] Rollback target identified
```

### Infrastructure deployment

```text
[ ] Terraform apply successful
[ ] APIs enabled
[ ] IAM applied
[ ] Artifact Registry available
[ ] Registry bucket available
[ ] BigQuery available
[ ] Cloud Tasks available
[ ] Pub/Sub available
[ ] Eventarc available
[ ] Organisation sink available
[ ] Cloud Run base service healthy
[ ] WIF available
```

### Application deployment

```text
[ ] WIF authentication successful
[ ] Image built successfully
[ ] Immutable image pushed
[ ] Cloud Run revision deployed
[ ] Runtime environment correct
[ ] Health check successful
[ ] Logs reviewed
```

### Functional validation

```text
[ ] Registry read successful
[ ] Dashboard accessible to authorised user
[ ] Reporting APIs operational
[ ] Brownfield small-scope test successful
[ ] Cloud Tasks worker successful
[ ] Greenfield workload-project test successful
[ ] BigQuery evidence confirmed
[ ] No critical errors
```

### Production completion

```text
[ ] Monitoring reviewed
[ ] Deployment evidence retained
[ ] Release documented
[ ] Rollback revision recorded
[ ] Change record updated
```

---

## 32. Related Documentation

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

See `ARCHITECTURE.md` for the parent architecture and component interaction model.

`IAM.md` should be treated as the next detailed deployment dependency because organisation-level discovery, remediation, Eventarc, Cloud Tasks, CI-CD and dashboard access all depend on the platform identity model.
