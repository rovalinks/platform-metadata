# Enterprise Metadata Governance Platform

Enterprise serverless metadata governance platform for Google Cloud. It supports Brownfield discovery/remediation, Greenfield event-driven governance, registry-driven metadata, BigQuery audit/reporting, and an operational dashboard.

> **Source-of-truth rule:** A client/adaptor existing in the repository does not by itself mean that a resource is enabled. Runtime enablement is controlled by `cloudrun/utils/supported_resources.py`.

## 1. Objectives

- Centralised metadata governance across GCP projects
- Brownfield governance for existing resources
- Greenfield near-real-time governance for newly created resources
- Registry-driven metadata with no application-specific metadata hardcoded into runtime logic
- Separate GCP Labels and Resource Manager Tags capability handling
- Batched asynchronous remediation using Cloud Tasks
- BigQuery-backed compliance, execution and reporting history
- Organisation and project-level dashboard views
- Serverless execution with minimal idle infrastructure
- Strict development and production isolation

## 2. Dedicated Governance Projects

| Project | Purpose |
| --- | --- |
| `platform-metadata-dev` | Development, integration testing, registry validation, adapter validation, Greenfield/Brownfield testing and dashboard development |
| `platform-metadata-prod` | Production organisation-wide governance, remediation, production registry, BigQuery audit/reporting, event processing and dashboard |

Client workload projects are governed targets - they do not host the shared governance platform. Development and production must use separate runtime service accounts, BigQuery data, queues, event infrastructure, registry configuration and access boundaries.

## 3. High-Level Architecture

```text
                         GCP ORGANISATION
                                |
              +-----------------+-----------------+
              |                                   |
       Existing Resources                  New Resources
         BROWNFIELD                         GREENFIELD
              |                                   |
     Cloud Asset Inventory                 Cloud Audit Logs
              |                                   |
              |                           Log Router / Pub/Sub
              |                                   |
              |                                Eventarc
              |                                   |
              +------------------+----------------+
                                 |
                         Cloud Run Platform
                                 |
          +----------------------+----------------------+
          |                      |                      |
    Governance Registry     Compliance Engine      Dispatcher
       Cloud Storage                                 Services
          |                                             |
          +----------------------+----------------------+
                                 |
                         Resource Adapters
                                 |
                         Remediation Planner
                                 |
                            Cloud Tasks
                                 |
                         /worker endpoint
                                 |
                       GCP Metadata APIs
                                 |
                             BigQuery
                                 |
                     Dashboard / Reporting
```

The runtime follows a dispatcher/service/adapter pattern so HTTP routing, orchestration and resource-specific API behaviour remain separated.

## 4. Brownfield Processing

```text
Project Scope -> Cloud Asset Inventory -> Discovery -> Live Metadata Enrichment
-> Registry Resolution -> Compliance -> Remediation Plan -> Cloud Tasks
-> Worker -> Resource Adapter -> Metadata Update -> BigQuery Evidence
```

A Brownfield run creates a common `run_id`, discovers resources across target projects, evaluates supported resources, creates remediation plans for non-compliant resources and queues remediation work.

Default configuration:

```text
REMEDIATION_BATCH_SIZE=500
```

Therefore 1,000,000 planned remediation actions represent approximately 2,000 remediation batches before retries - not 1,000,000 Cloud Tasks.

### Current project-scope logic

The organisation helper searches ACTIVE projects visible to the runtime identity and derives the environment from the governance host project:

- `platform-metadata-dev` -> DEV target selection
- `platform-metadata-prod` -> PROD target selection

The governance host project is excluded. The current implementation uses project-name environment filtering. If the client uses another taxonomy, replace this with an authoritative organisation/folder/registry-driven scope mechanism rather than application-specific hardcoding.

## 5. Greenfield Processing

```text
Resource Creation -> Cloud Audit Logs -> Organisation Log Routing -> Pub/Sub
-> Eventarc -> Cloud Run -> Audit Event Parsing -> Classification
-> Capability Check -> Compliance -> Resource Adapter -> Remediation
-> remediation_execution
```

A resource should be declared Greenfield-supported only when the creation event is routed correctly, a classifier recognises it, the asset type is enabled, a tested adapter can update it, IAM is present, and retry/idempotency behaviour is validated. Adapter code alone does not prove Greenfield support.

## 6. Governance Registry

Application metadata is maintained as YAML and read dynamically from Cloud Storage. An in-memory cache reduces repeated downloads.

```yaml
schemaVersion: v1
product: <product>
team: <team>
owner: <owner-email>
budgetOwner: <budget-owner-email>
organization: <organization>
department: <department>
costCenter: <cost-centre>
bindings:
  - cloud: gcp
    projectId: <gcp-project-id>
    region: <region>
    environment: <environment>
    businessCriticality: <criticality>
```

Required application metadata includes `schemaVersion`, `product`, `team`, `owner`, `budgetOwner`, `organization`, `department`, `costCenter` and `bindings`. Each GCP binding contains `cloud`, `projectId`, `region`, `environment` and `businessCriticality`.

Registry validation uses JSON Schema Draft 2020-12 and checks duplicate GCP project IDs across registry files.

## 7. Resource Capability Model

Runtime capability is centrally controlled by:

```text
cloudrun/utils/supported_resources.py
```

using `SUPPORTED_LABEL_RESOURCES` and `SUPPORTED_TAG_RESOURCES`.

### Current uploaded snapshot

In the supplied source snapshot, the only active uncommented label resource is:

```text
cloudresourcemanager.googleapis.com/Project
```

Other entries are currently commented out and `SUPPORTED_TAG_RESOURCES` is empty. The repository contains many adapters, but they must not be described as currently production-enabled until activated and validated.

### Adapter implementations present

- Compute Engine
- BigQuery
- Cloud Storage
- Resource Manager / Projects
- Cloud KMS
- Pub/Sub
- GKE
- Cloud Run
- Cloud SQL
- Artifact Registry
- Cloud Functions
- Vertex AI
- Dataplex
- App Engine
- Memorystore for Redis
- Secret Manager
- Cloud Monitoring
- Dataform
- Cloud DNS
- AlloyDB
- API Keys

Some are disabled, incomplete or unsuitable for labels. API Keys explicitly does not support label application in the current adapter.

## 8. Main Runtime Components

- `cloudrun/app.py` - Flask entry point for dashboard, APIs, Brownfield, Pub/Sub ingress and worker processing.
- `cloudrun/dispatcher.py` - routes logical operations to handlers.
- `cloudrun/services/` - governance orchestration: Brownfield, Greenfield, discovery, compliance, capability, planner, executor, adapter, ownership, verification and reporting.
- `cloudrun/clients/` - resource-specific API clients.
- `cloudrun/classifiers/` - Greenfield Audit Log classifiers.
- `cloudrun/repositories/` - BigQuery persistence/reporting.
- `cloudrun/registry/` - runtime registry reader/cache.
- `registry/` - application YAML and schema.
- `validation/` - registry validation.
- `cloudrun/templates/` and `cloudrun/static/` - dashboard UI.

## 9. BigQuery Governance Data

The implementation uses governance tables/data including:

- `resource_snapshot`
- `compliance_snapshot`
- `remediation_plan`
- `remediation_execution`

`remediation_execution` records execution evidence and distinguishes `BROWNFIELD` and `GREENFIELD`. Reporting calculates estate size, supported/compliant/non-compliant resources, compliance percentage, remediation progress/failures/success rate, Greenfield event totals and recent activity.

## 10. Dashboard

The dashboard is served from `/` and includes Executive Summary, Brownfield and Greenfield summaries, project/resource-type views, recent activity, non-compliant resources, scope selection and Brownfield execution. Reporting is BigQuery-backed rather than static UI data.

## 11. API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/` | Dashboard |
| POST | `/` | Greenfield dispatch |
| POST | `/events/pubsub` | Pub/Sub ingress |
| GET | `/brownfield` | Brownfield execution |
| GET | `/health` | Health |
| GET | `/discover` | Discovery |
| GET | `/compliance` | Compliance |
| GET | `/plan` | Planning |
| GET | `/execute` | Execute work |
| GET | `/runs/<run_id>` | Run status |
| GET | `/enforce` | Enforcement |
| GET | `/verify` | Verification |
| GET | `/report` | Governance report |
| GET | `/reports/dashboard` | Dashboard data |
| GET | `/reports/compliance` | Compliance report |
| GET | `/reports/runs` | Runs |
| GET | `/reports/run/<run_id>` | Run detail |
| GET | `/reports/history` | History |
| GET | `/reports/metrics` | Metrics |
| GET | `/reports/resources` | Resources |
| GET | `/reports/non-compliant` | Non-compliant resources |
| POST | `/worker` | Cloud Tasks worker |
| GET | `/projects_list` | Project dropdown data |

## 12. Runtime Configuration

Mandatory variables:

| Variable | Purpose |
| --- | --- |
| `PROJECT_ID` | Dedicated governance project |
| `REGION` | Runtime region |
| `TAG_PARENT` | Resource Manager Tag parent |
| `TASK_QUEUE` | Cloud Tasks queue |
| `CLOUD_RUN_URL` | Runtime service URL |
| `SERVICE_ACCOUNT_EMAIL` | Runtime service account |
| `REGISTRY_BUCKET` | Registry bucket |
| `REGISTRY_PREFIX` | Registry prefix |
| `BIGQUERY_DATASET` | Governance BigQuery dataset |

Tuning/defaults:

| Variable | Default |
| --- | --- |
| `REGISTRY_CACHE_TTL` | `60` |
| `DISCOVERY_RETENTION_DAYS` | `30` |
| `MAX_PARALLEL_WORKERS` | `10` |
| `REMEDIATION_BATCH_SIZE` | `500` |
| `LOG_LEVEL` | `WARNING` |
| `DRY_RUN` | `false` |
| `PRESERVE_EXISTING_LABELS` | `true` |

`EXCLUDED_PROJECTS` and `EXCLUDED_BUCKETS` provide exceptions. The host project and registry bucket are automatically excluded.

## 13. Runtime and Container

The application uses Flask/Gunicorn and Google Cloud client libraries. The supplied container currently uses `python:3.12-slim` and starts:

```bash
gunicorn --bind :${PORT} --workers 1 --threads 8 app:app
```

The registry is intentionally not copied into the image - runtime loads it from Cloud Storage.

## 14. Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r cloudrun/requirements.txt
```

Windows Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r cloudrun/requirements.txt
```

Set mandatory environment variables and run:

```bash
cd cloudrun
python app.py
```

or:

```bash
gunicorn --bind :8080 --workers 1 --threads 8 app:app
```

Application Default Credentials are required for real GCP API access.

## 15. Registry Validation

```bash
pip install -r validation/requirements.txt
python validation/validate_registry.py
```

Validation covers JSON Schema and duplicate GCP project bindings. Failure exits non-zero and should block promotion.

## 16. IAM Model

Use dedicated service accounts and least privilege. Separate runtime, Eventarc trigger, transport, CI/CD deployment and human dashboard access responsibilities.

The runtime requires only the permissions needed for registry reads, BigQuery, Asset/Resource Manager visibility, Cloud Tasks, enabled resource metadata mutations and Resource Manager Tags if tag governance is enabled.

Prefer a custom remediation role based on **enabled** capabilities. Development and production identities must remain separate.

## 17. Security

- Production control plane: `platform-metadata-prod`
- Development control plane: `platform-metadata-dev`
- Restrict dashboard to authorised organisation users
- Protect worker/internal endpoints with authenticated service-to-service invocation
- Never commit credentials
- Validate registry changes before promotion
- Exclude governance infrastructure from unintended self-remediation
- Use `DRY_RUN=true` for controlled onboarding/testing where appropriate

## 18. Cost and Scale

The architecture is serverless and consumption-based. Cloud Asset Inventory should not be modelled as a per-resource discovery fee.

With batch size 500:

```text
1,000,000 planned actions / 500 = ~2,000 remediation tasks
```

before retries/ancillary operations. Cloud Run cost depends on measured CPU, memory, concurrency and runtime. BigQuery depends on storage/ingestion/query volume. Greenfield cost follows creation-event volume.

Benchmark representative runs in `platform-metadata-dev` before client production cost approval.

## 19. Observability

Monitor Brownfield duration, discovered/evaluated resources, compliance percentage, plans, task batches/retries, worker failures, mutation failures, Greenfield events, unsupported events, processing duration, BigQuery failures, registry failures and API quota/rate-limit errors.

Avoid unnecessary per-resource INFO logging at enterprise scale.

## 20. Adding a Resource Type

1. Confirm GCP metadata support.
2. Confirm Cloud Asset Inventory asset type.
3. Implement/test read behaviour.
4. Implement/test safe mutation.
5. Add least-privilege IAM.
6. Add asset type to the appropriate capability set.
7. Add Brownfield tests.
8. For Greenfield, validate the exact creation audit event.
9. Implement/update classifier.
10. Validate event routing.
11. Validate retry/idempotency.
12. Validate BigQuery reporting.
13. Test in `platform-metadata-dev`.
14. Promote to `platform-metadata-prod` after approval.

Do not enable a resource by adding only an IAM permission.

## 21. Repository Structure

```text
.
├── cloudrun/
│   ├── app.py
│   ├── config.py
│   ├── dispatcher.py
│   ├── classifiers/
│   ├── clients/
│   ├── handlers/
│   ├── ingress/
│   ├── models/
│   ├── registry/
│   ├── repositories/
│   ├── routes/
│   ├── services/
│   ├── static/
│   ├── templates/
│   ├── utils/
│   └── requirements.txt
├── registry/
│   ├── applications/
│   └── schemas/
├── validation/
├── cloudbuild.yaml
└── Dockerfile
```

## 22. Production Readiness Checklist

- [ ] `platform-metadata-dev` validated
- [ ] `platform-metadata-prod` independently deployed
- [ ] Registry/schema validated
- [ ] BigQuery tables validated
- [ ] Runtime IAM least privilege reviewed
- [ ] Dev identity cannot unintentionally remediate production
- [ ] Enabled capability list reviewed
- [ ] Every enabled adapter tested
- [ ] Brownfield batching scale-tested
- [ ] Greenfield creation events validated per enabled type
- [ ] Event routing tested end-to-end
- [ ] Worker authentication tested
- [ ] Retry/idempotency tested
- [ ] Dashboard restricted to authorised users
- [ ] Internal endpoints protected
- [ ] Exclusions reviewed
- [ ] Logging volume reviewed
- [ ] Budgets/alerts configured
- [ ] Rollback/runbook documented
- [ ] Production dry-run completed

## 23. Engineering Principles

1. No application-specific hardcoding.
2. Environment values come from deployment configuration.
3. Capability is checked before execution.
4. Brownfield and Greenfield share one governance/compliance/adapter model.
5. IAM follows enabled capability.
6. Remediation is batched for enterprise scale.
7. Mutations produce audit evidence.
8. One resource failure must not stop independent work.
9. Code presence does not equal production support.
10. Validate in `platform-metadata-dev` before `platform-metadata-prod`.

## 24. Current Snapshot Notes

The current source contains active implementation plus commented historical/candidate code. Treat active configuration and capability sets as authoritative. Do not infer support from commented entries. Keep environment-specific project IDs, URLs, buckets and service-account addresses outside application code.

---

**Platform:** Enterprise Metadata Governance Platform  
**Cloud:** Google Cloud  
**Runtime:** Cloud Run + Flask + Gunicorn  
**Modes:** Brownfield + Greenfield  
**Control planes:** `platform-metadata-dev` + `platform-metadata-prod`
