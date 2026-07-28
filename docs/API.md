# Enterprise Metadata Governance Platform - API Reference

## 1. Purpose

This document defines the API and endpoint model for the Enterprise Metadata Governance Platform running on Google Cloud Run.

The API surface supports:

- platform health and operational checks
- Brownfield discovery and orchestration
- asynchronous remediation workers
- Greenfield Eventarc/Pub/Sub intake
- dashboard and reporting data
- controlled internal service-to-service execution

The API is part of the central governance control plane hosted in:

```text
platform-metadata-dev
platform-metadata-prod
```

This document describes the architectural API contract. The deployed application code remains authoritative for exact route names, HTTP methods and response fields.

---

## 2. API Design Principles

The API follows these principles:

```text
Authenticated by default
No hardcoded workload projects
No application metadata in request handlers
Thin HTTP layer
Business logic delegated to services
Resource-specific logic delegated to adapters
Asynchronous Brownfield remediation
Idempotent processing where possible
Structured errors
Auditable execution
```

HTTP handlers should coordinate requests, not contain service-specific GCP mutation logic.

---

## 3. Logical API Surface

The Cloud Run service provides four logical endpoint categories:

```text
metadata-governance
    |
    +-- Operational endpoints
    |
    +-- Brownfield orchestration endpoints
    |
    +-- Internal worker endpoints
    |
    +-- Greenfield event intake
    |
    +-- Dashboard/reporting endpoints
```

Not every endpoint should have the same caller or IAM policy.

---

## 4. Base Service

The application is deployed as:

```text
Cloud Run service: metadata-governance
```

The service URL is environment-specific and must be supplied by deployment output/runtime configuration.

Do not hardcode the DEV or PROD Cloud Run URL in application code.

Conceptually:

```text
https://<environment-specific-cloud-run-url>
```

---

## 5. Authentication Model

Production endpoints must not rely on anonymous public access.

Caller categories include:

| Caller | Purpose |
| --- | --- |
| Authorised organisation user | Dashboard/API access where approved |
| Eventarc identity | Greenfield event delivery |
| Cloud Tasks OIDC identity | Brownfield worker invocation |
| Approved CI/CD identity | Deployment, not normal runtime API use |
| Platform operator | Controlled operational execution |

Cloud Run IAM is the first authentication boundary.

Application-level authorisation may provide additional controls where required.

---

## 6. Public vs Internal Access

The governance platform should not expose worker or event-processing interfaces as unrestricted public APIs.

Logical access model:

```text
Dashboard / approved operator API
    -> authenticated authorised user

Greenfield intake
    -> Eventarc identity

/worker
    -> Cloud Tasks OIDC identity

Internal reporting
    -> authorised dashboard/service caller
```

`allUsers` Cloud Run Invoker must not be required in production.

---

## 7. Operational Health Endpoint

A health endpoint should provide a lightweight indication that the application process is available.

Conceptual route:

```text
GET /health
```

or the exact route implemented by the application.

A health response should avoid expensive organisation discovery or remediation.

Example conceptual response:

```json
{
  "status": "ok",
  "service": "metadata-governance"
}
```

The exact deployed response schema is code-defined.

---

## 8. Readiness Considerations

A process-level health response does not necessarily prove all dependencies are healthy.

Operational readiness can additionally consider:

- BigQuery access
- registry availability
- Cloud Tasks configuration
- required environment variables
- capability configuration

Avoid turning every liveness request into an expensive full dependency scan.

---

## 9. Brownfield Orchestration API

Brownfield orchestration starts discovery/evaluation for a requested scope.

The API should support controlled execution patterns such as:

```text
single project
selected scope
organisation scope
```

without embedding client project IDs into source code.

The deployed implementation previously returned Brownfield run information containing fields such as:

```json
{
  "discovered": 430,
  "evaluated": 33,
  "failed": 3,
  "planned": 6,
  "project": "example-project",
  "run_id": "generated-run-id",
  "status": "COMPLETED",
  "successful": 3
}
```

This example illustrates the run-summary model and is not a guarantee that every deployment/version returns exactly these fields.

---

## 10. Brownfield Run Identifier

Each Brownfield execution should generate or use a unique:

```text
run_id
```

The identifier correlates:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

API responses should expose the `run_id` whenever an operator needs to track asynchronous work.

---

## 11. Brownfield Request Validation

Before starting a run, validate:

- requested scope
- project identifier format where applicable
- environment restrictions
- exclusions
- dry-run setting where exposed
- required configuration
- caller authorisation

Do not accept arbitrary client-controlled metadata values that bypass the Application Registry.

---

## 12. Brownfield API Responsibilities

The Brownfield orchestration endpoint should coordinate:

```text
Request
   |
   v
Validate scope
   |
   v
Generate run_id
   |
   v
Discovery
   |
   v
Registry resolution
   |
   v
Capability filtering
   |
   v
Compliance evaluation
   |
   v
Remediation planning
   |
   v
Cloud Tasks batching
   |
   v
Return run summary
```

The original request should not wait synchronously for every enterprise resource mutation to finish.

---

## 13. Asynchronous Completion

A successful Brownfield orchestration response can mean that planning and task creation completed successfully.

It does not necessarily mean all worker batches have finished.

Therefore:

```text
HTTP request completed
        !=
All remediation completed
```

Final execution status must be determined from worker results and `remediation_execution`.

---

## 14. Worker Endpoint

The internal worker endpoint is:

```text
/worker
```

It receives remediation batches from Cloud Tasks.

This endpoint is machine-to-machine.

It must be protected by authenticated Cloud Run invocation.

---

## 15. Worker Request Model

A worker request conceptually contains:

```text
run identifier
batch identifier/context
one or more remediation actions
```

Each remediation action requires enough information to resolve:

- project
- canonical asset type
- resource name
- location where required
- planned managed metadata

The exact payload schema is defined by the current application implementation.

---

## 16. Worker Processing

```text
Cloud Tasks Request
       |
       v
Authenticate
       |
       v
Validate Payload
       |
       v
Iterate Actions
       |
       v
Dispatcher
       |
       v
Resource Adapter
       |
       v
Native GCP API
       |
       v
Execution Evidence
```

The worker should isolate individual resource failures wherever practical.

---

## 17. Worker HTTP Responses

Cloud Tasks uses HTTP response status to determine delivery success/retry behaviour.

The worker must therefore distinguish:

```text
Request accepted/processed
Retryable infrastructure failure
Permanent invalid request
```

Application-level resource failure and HTTP-level task failure are not always the same thing.

For example, one permanently unsupported resource in a safely processed batch should not necessarily force Cloud Tasks to replay every successfully processed action.

---

## 18. Worker Idempotency

Worker operations must be safe under retry.

The preferred behaviour is:

```text
Read current state
      |
      v
Compare required managed metadata
      |
      +-- already correct -> success/no-op
      |
      +-- update required -> reconcile
```

Cloud Tasks delivery must never be treated as exactly-once execution.

---

## 19. Greenfield Intake

Greenfield processing receives Eventarc-delivered Pub/Sub CloudEvents.

The transport path is:

```text
Organisation Audit Log
        |
        v
Logging Sink
        |
        v
Pub/Sub
        |
        v
Eventarc
        |
        v
Cloud Run
```

The Greenfield HTTP handler is not intended as a generic user-facing resource creation API.

---

## 20. Greenfield Event Envelope

The incoming request contains an Eventarc CloudEvent representing a Pub/Sub message.

The Pub/Sub message contains the exported audit-log payload.

The handler must:

```text
Receive CloudEvent
      |
      v
Validate event
      |
      v
Decode Pub/Sub message
      |
      v
Parse Audit Log
      |
      v
Classify service/method
```

The exact event envelope should follow the Eventarc/Pub/Sub contract used by the deployed trigger.

---

## 21. Greenfield Event Validation

The handler must not remediate merely because an HTTP request reached the service.

Validate:

- expected event type
- Pub/Sub envelope
- audit payload
- `protoPayload.serviceName`
- `protoPayload.methodName`
- project identity
- resource identity
- capability status
- registry binding

Unsupported events should fail safely or be acknowledged/skipped according to the application's retry strategy.

---

## 22. Greenfield Classification

The classifier maps the audit event to the canonical platform resource type.

Conceptually:

```text
serviceName + methodName + payload
              |
              v
          Classifier
              |
              v
      Canonical Asset Type
```

Do not put resource mutation logic inside the HTTP event handler.

---

## 23. Greenfield Response Behaviour

Eventarc requires an appropriate successful HTTP response when the event has been accepted/processed according to application semantics.

Retryable processing failures should be surfaced consistently with the selected Eventarc/Pub/Sub retry strategy.

Permanent unsupported events should not create uncontrolled redelivery loops.

---

## 24. Dashboard APIs

The dashboard should obtain operational data from backend APIs rather than query Google Cloud directly from browser JavaScript.

Conceptual flow:

```text
Authenticated Browser
        |
        v
Cloud Run Dashboard/API
        |
        v
BigQuery / Governance Services
```

This keeps:

- credentials out of the browser
- BigQuery access centralised
- query logic server-side
- authorisation controlled

---

## 25. Executive Summary API

The dashboard Executive Summary should be backed by live operational data.

Useful response fields can include:

```text
total_resources
evaluated_resources
compliant_resources
non_compliant_resources
planned_remediations
successful_remediations
failed_remediations
greenfield_events
last_updated
```

The exact API schema should match the dashboard implementation.

Do not populate live counts from repository snapshots.

---

## 26. Compliance Reporting API

A compliance API may provide aggregated results by:

- application
- project
- environment
- asset type
- compliance state

Conceptual response:

```json
{
  "total": 1000,
  "compliant": 820,
  "non_compliant": 180,
  "compliance_percentage": 82.0
}
```

Values shown here are examples only.

---

## 27. Resource-Type Reporting API

The dashboard can expose resource distribution and compliance by canonical asset type.

Example conceptual model:

```json
[
  {
    "asset_type": "example.googleapis.com/Resource",
    "total": 100,
    "compliant": 90,
    "non_compliant": 10
  }
]
```

The API should derive these values from operational evidence.

---

## 28. Project/Application Reporting API

Project/application views should use:

```text
BigQuery operational evidence
        +
Application Registry mapping
```

The browser must not maintain a hardcoded project-to-application map.

---

## 29. Recent Activity API

A recent-activity API can expose remediation evidence such as:

```text
executed_at
execution_mode
project_id
asset_type
resource_name
status
duration_ms
```

This should come from `remediation_execution` or the relevant operational data source.

---

## 30. Brownfield Run Status API

Because Brownfield execution is asynchronous, operators benefit from a run-status API.

Conceptually:

```text
GET /api/runs/<run_id>
```

A useful response can distinguish:

```text
discovered
evaluated
planned
queued
successful
failed
remaining
```

The exact route must follow the implemented application.

---

## 31. API and BigQuery

Backend API queries may read:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

Queries should:

- use parameterised inputs
- avoid SQL string concatenation from untrusted request data
- limit unnecessary scanned data
- filter by `run_id`/time/project where appropriate
- return only fields required by the dashboard

---

## 32. API and Application Registry

Application metadata exposed through reporting APIs should be resolved through the registry layer.

Do not duplicate registry values in:

```text
dashboard.js
HTML
API route constants
resource adapters
```

This prevents UI and runtime ownership data from drifting apart.

---

## 33. API and Capability Model

The API may expose supported-resource information for operational visibility.

That data should come from the capability configuration.

It must distinguish:

```text
Brownfield enabled
Greenfield enabled
Validation status
```

A dashboard should not infer support from the existence of historical execution rows.

---

## 34. Error Response Model

API errors should be structured and useful.

Conceptual model:

```json
{
  "status": "error",
  "code": "PROJECT_NOT_BOUND",
  "message": "Project is not present in the approved Application Registry",
  "run_id": "optional-run-id"
}
```

Do not expose stack traces, credentials, tokens or sensitive request payloads to browser/API callers.

---

## 35. Error Categories

Useful API/application error categories include:

```text
INVALID_REQUEST
UNAUTHENTICATED
UNAUTHORISED
PROJECT_NOT_BOUND
UNSUPPORTED_RESOURCE
UNSUPPORTED_EVENT
REGISTRY_FAILURE
DISCOVERY_FAILURE
COMPLIANCE_FAILURE
TASK_ENQUEUE_FAILURE
RESOURCE_LOOKUP_FAILURE
REMEDIATION_FAILURE
IAM_DENIED
BIGQUERY_FAILURE
INTERNAL_ERROR
```

The exact names should align with the application's existing error model.

---

## 36. HTTP Status Principles

Use HTTP status codes consistently.

Conceptually:

```text
2xx - request successfully accepted/processed
400 - invalid caller input
401 - unauthenticated where applicable
403 - authenticated but not authorised
404 - requested API object/run not found
409 - conflict where applicable
429 - controlled rate/quota condition where exposed
5xx - server/dependency failure
```

For Eventarc and Cloud Tasks endpoints, status-code behaviour must also consider redelivery/retry semantics.

---

## 37. Structured Logging

Every important API execution should produce structured logs with useful context.

Recommended fields include:

```text
request_id
run_id
execution_mode
project_id
asset_type
resource_name
endpoint
status
duration_ms
error_code
```

Do not log:

- access tokens
- ID tokens
- service-account keys
- secret payloads
- unnecessary audit request bodies

---

## 38. Request Correlation

A request identifier should allow operators to correlate:

```text
HTTP request
    |
    v
Application logs
    |
    v
Brownfield run
    |
    v
Cloud Task
    |
    v
Worker
    |
    v
BigQuery execution
```

`run_id` remains the primary Brownfield governance correlation identifier.

---

## 39. API Timeouts

Do not use a long synchronous HTTP request as the scaling mechanism for organisation-wide remediation.

The API should perform orchestration and enqueue asynchronous work.

Long-running native service operations should be handled by adapter/worker logic rather than keeping an operator browser request open.

---

## 40. Pagination

APIs returning large resource/activity datasets should use bounded result sets.

Do not return tens of thousands of raw resources to the dashboard in one response.

Use:

- aggregation
- pagination
- time filters
- project/application filters
- server-side limits

as appropriate to the implemented UI.

---

## 41. Input Filtering

Dashboard/reporting filters can include:

```text
application
project
environment
asset_type
execution_mode
status
time range
run_id
```

Inputs must be validated before being used in BigQuery queries or internal service calls.

---

## 42. No Hardcoding

Do not hardcode:

- Cloud Run service URL
- workload project IDs
- organisation ID
- service-account emails
- Application Registry ownership
- BigQuery dataset/table project names
- Pub/Sub topic project
- DEV/PROD environment-specific values

inside browser JavaScript or API business logic when they belong to deployment/runtime configuration.

---

## 43. CORS

If dashboard assets and APIs are served from the same Cloud Run origin, broad cross-origin access should not be required.

Do not enable unrestricted:

```text
Access-Control-Allow-Origin: *
```

without an explicit requirement.

If cross-origin access is introduced later, restrict allowed origins to approved front ends.

---

## 44. CSRF Considerations

If future browser APIs use cookie-based authenticated state for mutation operations, CSRF protection must be reviewed.

Current service-to-service Eventarc/Cloud Tasks authentication is identity-token based and represents a different threat model.

Do not treat all endpoint authentication mechanisms as interchangeable.

---

## 45. Rate and Abuse Controls

Internal endpoints should be protected primarily through IAM and trusted service identities.

Additional controls can include:

- Cloud Tasks queue rates
- Cloud Run maximum instances
- request validation
- payload size limits
- bounded batch sizes

Do not rely solely on application code to protect an anonymously exposed worker endpoint.

---

## 46. API Versioning

If the API becomes an externally consumed client contract, introduce explicit versioning before incompatible changes.

For example:

```text
/api/v1/...
```

Internal implementation routes do not need artificial versioning unless they are treated as stable contracts.

The current deployed code remains authoritative.

---

## 47. Backward Compatibility

Dashboard and backend API changes should be deployed together when their schemas are tightly coupled.

For independently deployed consumers:

- add fields compatibly
- avoid silently renaming fields
- document deprecations
- version breaking changes

---

## 48. DEV API Validation

Before production promotion:

```text
[ ] Health endpoint works
[ ] Unauthenticated access behaves as designed
[ ] Authorised dashboard access works
[ ] Brownfield request validation works
[ ] Brownfield run returns run_id
[ ] Cloud Tasks are created
[ ] /worker authentication succeeds
[ ] Worker retry behaviour validated
[ ] Greenfield Eventarc request succeeds
[ ] Unsupported event behaviour validated
[ ] Dashboard APIs return BigQuery-backed data
[ ] Errors are structured
[ ] Sensitive data is not logged
```

---

## 49. Production API Validation

After deployment to `platform-metadata-prod`:

```text
[ ] Correct PROD Cloud Run revision active
[ ] No allUsers invocation binding
[ ] Eventarc can invoke service
[ ] Cloud Tasks can invoke /worker
[ ] Approved dashboard users can invoke service
[ ] Unauthorised users cannot invoke service
[ ] PROD registry is used
[ ] PROD BigQuery dataset is used
[ ] PROD queue/topic configuration is used
[ ] Brownfield controlled test succeeds
[ ] Greenfield controlled test succeeds
[ ] Dashboard reports PROD operational evidence
```

---

## 50. API Troubleshooting

### Brownfield request returns no useful work

Check:

```text
request scope
project discovery
registry binding
capability filtering
compliance results
remediation_plan
```

### Tasks created but worker not called

Check:

```text
Cloud Tasks queue
task target URL
OIDC identity
Cloud Run Invoker
/worker route
Cloud Run logs
```

### Greenfield has no API logs

Check upstream first:

```text
Audit Log
 -> organisation sink
 -> Pub/Sub
 -> Eventarc
 -> Cloud Run
```

Do not modify the Greenfield HTTP handler until event delivery is proven.

### Dashboard returns zero/stale values

Check:

```text
BigQuery operational tables
API query filters
environment configuration
run/time filters
cache
dashboard API call
```

Do not replace missing operational data with repository snapshot counts.

---

## 51. API Security Checklist

```text
[ ] Cloud Run authentication enabled
[ ] No unnecessary allUsers access
[ ] /worker machine-authenticated
[ ] Greenfield intake Eventarc-authenticated
[ ] Dashboard restricted to approved organisation identities
[ ] Request inputs validated
[ ] BigQuery queries parameterised
[ ] Secrets/tokens excluded from logs
[ ] Environment configuration not exposed unnecessarily
[ ] Registry data exposed only as required
[ ] Error responses do not leak stack traces
```

---

## 52. API Anti-Patterns

Do not:

- expose `/worker` anonymously
- accept application ownership metadata directly from arbitrary Brownfield callers
- hardcode workload project IDs in routes
- query BigQuery directly from browser JavaScript using privileged credentials
- use repository snapshots as live dashboard API data
- block a Brownfield HTTP request until every resource has been remediated
- assume Cloud Tasks delivers exactly once
- return raw stack traces
- log identity tokens
- use one giant API handler for every resource service
- treat an Eventarc intake endpoint as a generic public webhook
- return unbounded enterprise resource lists to the browser

---

## 53. Logical Endpoint Summary

| Endpoint Category | Primary Caller | Authentication | Purpose |
| --- | --- | --- | --- |
| Health/operational | Platform/operator | Environment policy | Service health |
| Brownfield orchestration | Approved operator/system | Authenticated | Start discovery/compliance/remediation planning |
| `/worker` | Cloud Tasks | OIDC + Cloud Run IAM | Execute remediation batches |
| Greenfield intake | Eventarc | Eventarc identity + Cloud Run IAM | Process resource creation audit events |
| Dashboard APIs | Authorised organisation users | Cloud Run IAM | Operational reporting |
| Run status/reporting | Authorised operator/dashboard | Cloud Run IAM | Track asynchronous execution |

---

## 54. Architecture Summary

The API layer is intentionally thin.

```text
Authenticated Caller
        |
        v
Cloud Run API
        |
        +-- Brownfield -> Discovery / Planning -> Cloud Tasks
        |
        +-- Worker -> Dispatcher -> Adapter -> Native GCP API
        |
        +-- Greenfield -> Parser -> Classifier -> Adapter
        |
        +-- Dashboard -> BigQuery / Registry
```

This design keeps HTTP transport separate from governance logic and service-specific resource operations.

Brownfield remediation is asynchronous, Greenfield processing is event-driven, machine endpoints use authenticated service identities, dashboard data comes from operational evidence, and environment-specific infrastructure values remain configuration-driven rather than hardcoded.

---

## 55. Related Documentation

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

- `ARCHITECTURE.md` for the overall platform design.
- `BROWNFIELD.md` for Brownfield orchestration and worker processing.
- `GREENFIELD.md` for Eventarc/Pub/Sub processing.
- `IAM.md` for endpoint caller identities and Cloud Run access.
- `DATA_MODEL.md` for BigQuery tables consumed by reporting APIs.
- `SECURITY.md` for production API security controls.
