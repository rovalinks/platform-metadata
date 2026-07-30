# Enterprise Metadata Governance Platform - Operations Runbook

## 1. Purpose

This is the operator-facing runbook for day-to-day operation of the Enterprise Metadata Governance Platform. It complements `OPERATIONS.md` and focuses on commands, checks, troubleshooting, Brownfield/Greenfield operation, emergency procedures and DEV/PROD access.

## 2. Environment Reference

### DEV

```text
Project: platform-metadata-dev-001add
Region: us-central1
Cloud Run service: metadata-governance
Proxy port: 8080
```

### PROD

```text
Project: platform-metadata-prod-92e02c
Region: us-central1
Cloud Run service: metadata-governance
Proxy port: 8080
```

Always verify the environment before performing any change.

## 3. DEV Dashboard Access

Run:

```bash
gcloud run services proxy metadata-governance   --project=platform-metadata-dev-001add   --region=us-central1   --port=8080
```

Then:

1. Keep the terminal running.
2. Click/open Web Preview for port `8080` in the development environment.
3. If running from a normal local terminal, use the local proxy address displayed by `gcloud`.
4. Confirm that the DEV dashboard loads.
5. Confirm that the data being displayed belongs to DEV.

Stop the proxy with:

```text
Ctrl+C
```

The proxy provides authenticated local access without requiring the Cloud Run service to be made publicly accessible.

## 4. PROD Dashboard Access

Run:

```bash
gcloud run services proxy metadata-governance   --project=platform-metadata-prod-92e02c   --region=us-central1   --port=8080
```

Then:

1. Keep the terminal running.
2. Click/open Web Preview for port `8080`.
3. Confirm that the PROD dashboard loads.
4. Verify the environment before interpreting data or performing an approved production operation.

Stop the proxy with:

```text
Ctrl+C
```

## 5. DEV/PROD Safety Check

Before operational work:

```bash
gcloud auth list
gcloud config list
gcloud config get-value project
```

Prefer commands containing an explicit `--project` rather than relying on the current gcloud default project.

## 6. Verify Cloud Run

### DEV

```bash
gcloud run services describe metadata-governance   --project=platform-metadata-dev-001add   --region=us-central1
```

### PROD

```bash
gcloud run services describe metadata-governance   --project=platform-metadata-prod-92e02c   --region=us-central1
```

Check:

```text
service is ready
expected revision is deployed
traffic points to the intended revision
runtime service account is correct
region is correct
environment configuration is correct
```

## 7. Cloud Run Logs

### DEV

```bash
gcloud run services logs read metadata-governance   --project=platform-metadata-dev-001add   --region=us-central1   --limit=100
```

### PROD

```bash
gcloud run services logs read metadata-governance   --project=platform-metadata-prod-92e02c   --region=us-central1   --limit=100
```

During troubleshooting capture, where available:

```text
timestamp
run_id
execution_mode
project_id
asset_type
resource_name
operation
status
error
```

## 8. Brownfield Run Flow

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
Resource Adapter
        |
        v
Native GCP API
        |
        v
remediation_execution
```

Always capture the `run_id`.

## 9. Brownfield Pre-Run Checklist

```text
[ ] Correct environment
[ ] Correct scope/project
[ ] Registry validated
[ ] Target projects registered
[ ] Exclusions reviewed
[ ] Supported capabilities reviewed
[ ] Runtime IAM confirmed
[ ] Cloud Tasks healthy
[ ] Cloud Run healthy
[ ] BigQuery available
[ ] Monitoring active
[ ] Production approval obtained where required
[ ] Emergency-stop procedure understood
```

Do not make an organisation-wide remediation the first production test.

## 10. Brownfield Monitoring

After starting a run:

```text
1. Capture run_id
2. Verify resource_snapshot
3. Verify compliance_snapshot
4. Verify remediation_plan
5. Verify task creation
6. Verify /worker processing
7. Verify remediation_execution
8. Verify final resource metadata
9. Verify dashboard
```

The orchestration response does not mean all asynchronous remediation has finished.

Completion requires reconciliation of:

```text
planned
queued
executed
successful
failed
remaining
```

## 11. Cloud Tasks

Queue:

```text
metadata-remediation
```

List queues:

```bash
gcloud tasks queues list   --project=<PROJECT_ID>   --location=us-central1
```

Describe the remediation queue:

```bash
gcloud tasks queues describe metadata-remediation   --project=<PROJECT_ID>   --location=us-central1
```

Replace `<PROJECT_ID>` explicitly with DEV or PROD.

If plans exist but execution does not:

```text
remediation_plan
 -> task creation
 -> queue
 -> target URL
 -> OIDC identity
 -> Cloud Run Invoker
 -> /worker
 -> adapter
 -> IAM/API
 -> remediation_execution
```

## 12. Greenfield Flow

```text
Resource Creation
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
Application Registry
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
```

## 13. Greenfield Validation

For each Greenfield-enabled resource type:

```text
1. Confirm capability is enabled
2. Confirm workload project is registered
3. Create a real supported resource
4. Capture its real Audit Log
5. Validate serviceName
6. Validate methodName
7. Validate organisation sink
8. Validate Pub/Sub
9. Validate Eventarc
10. Validate Cloud Run receipt
11. Validate classifier
12. Validate registry resolution
13. Validate adapter
14. Validate final metadata
15. Validate GREENFIELD BigQuery evidence
```

A fabricated HTTP event is not sufficient for production certification.

## 14. Greenfield Troubleshooting

Use this exact order:

```text
Audit Log
 -> Organisation Sink
 -> Pub/Sub
 -> Eventarc
 -> Cloud Run
 -> Classifier
 -> Registry
 -> Capability
 -> Adapter
 -> IAM / Native API
 -> BigQuery
```

Find the first failing stage before changing code.

## 15. Application Registry Issues

If ownership/metadata cannot be resolved, verify:

```text
project exists in registry
project is bound to correct application
application metadata is valid
environment is valid
registry schema is valid
runtime can read registry
correct DEV/PROD registry is configured
```

Never hardcode an application into an adapter to bypass incorrect registry data.

For an unbound project:

```text
do not guess ownership
do not copy another project's metadata
do not silently assign defaults
```

Escalate it to the Application Registry owner.

## 16. IAM Failure

For `PERMISSION_DENIED` or HTTP `403`:

```text
1. Identify calling service account
2. Identify target resource/project
3. Capture exact denied permission
4. Confirm the capability requires that permission
5. Confirm intended IAM scope
6. Validate in DEV
7. Update approved IAM/custom role only if justified
8. Re-test
9. Promote through normal production change control
```

Never use `roles/owner` or `roles/editor` as an adapter troubleshooting shortcut.

## 17. Metadata Preservation

Expected remediation:

```text
Existing unrelated metadata
          +
Required governance metadata
          =
Final metadata
```

If unrelated metadata disappears, stop broad use of that capability and investigate the adapter.

## 18. Duplicate Events

Greenfield processing must be idempotent:

```text
duplicate event
     |
     v
read current state
     |
     v
already compliant
     |
     v
no unnecessary mutation
```

## 19. Temporary Failures

### Temporary 404

Where appropriate and implemented, use bounded retries because a newly created resource may not immediately be readable through the downstream API.

### API 429

Check:

```text
worker concurrency
Cloud Tasks dispatch rate
batch size
target API quota
retry behaviour
```

Reduce throughput if required rather than automatically increasing quota.

### API 5xx

Check whether the issue is isolated or systemic. Use bounded retry behaviour and avoid increasing remediation volume while a downstream service is unstable.

## 20. Dashboard Troubleshooting

If dashboard values appear incorrect:

```text
1. Confirm DEV vs PROD
2. Confirm Cloud Run health
3. Confirm backend API response
4. Confirm BigQuery connectivity
5. Check source BigQuery rows
6. Check time/range filters
7. Check latest-state logic
8. Then inspect browser console/UI
```

Do not hardcode dashboard numbers to hide missing backend data.

Remember:

```text
historical remediation success != current compliance
```

## 21. Deployment Verification - DEV

```bash
gcloud run services describe metadata-governance   --project=platform-metadata-dev-001add   --region=us-central1
```

Then:

```bash
gcloud run services proxy metadata-governance   --project=platform-metadata-dev-001add   --region=us-central1   --port=8080
```

Open Web Preview for port `8080` and verify:

```text
dashboard
health
registry
BigQuery reads
controlled Brownfield
controlled Greenfield where applicable
```

## 22. Deployment Verification - PROD

```bash
gcloud run services describe metadata-governance   --project=platform-metadata-prod-92e02c   --region=us-central1
```

Then:

```bash
gcloud run services proxy metadata-governance   --project=platform-metadata-prod-92e02c   --region=us-central1   --port=8080
```

Open Web Preview for port `8080`.

Perform only approved production smoke tests.

## 23. PROD Smoke Test

```text
[ ] Cloud Run ready
[ ] Correct revision
[ ] Correct runtime identity
[ ] Dashboard accessible
[ ] Registry loads
[ ] BigQuery reads work
[ ] No unexpected 5xx spike
[ ] Cloud Tasks healthy
[ ] Pub/Sub/Eventarc healthy
[ ] No unexpected remediation activity
```

## 24. Emergency Stop - Brownfield

If incorrect Brownfield remediation is occurring:

```text
1. Stop starting new runs
2. Capture affected run_id
3. Determine queued/in-flight work
4. Pause/stop additional dispatch using the approved control if required
5. Preserve BigQuery evidence and logs
6. Identify affected projects/capability
7. Correct in DEV
8. Validate
9. Obtain production approval
10. Resume with controlled scope
```

Do not delete operational evidence.

## 25. Emergency Stop - Greenfield

If incorrect Greenfield remediation is occurring:

```text
1. Identify affected capability
2. Stop/disable the affected processing path using the approved control
3. Preserve event/execution evidence
4. Identify affected resources
5. Correct in DEV
6. Validate with a real event
7. Approve production change
8. Re-enable in controlled scope
```

Avoid disabling unrelated capabilities unnecessarily.

## 26. Rollback

For a defective Cloud Run deployment:

```text
identify previous known-good revision
redirect traffic using approved rollback procedure
verify health
verify dashboard
verify task/event processing
record the incident/change
```

A code rollback does not reverse metadata already written to workload resources.

For incorrect registry data:

```text
stop affected broad remediation if required
identify bad registry change
restore approved registry data
validate schema and mappings
assess resources already modified
```

Restoring registry data does not automatically reverse prior resource changes.

## 27. Monitoring

Monitor:

```text
Cloud Run availability
Cloud Run 5xx
Cloud Run latency
Cloud Tasks backlog
Cloud Tasks retries
Greenfield failures
Brownfield failures
BigQuery write failures
registry load failures
IAM denial spikes
unexpected remediation volume
cost anomalies
```

## 28. Daily Check

```text
[ ] Dashboard loads
[ ] Cloud Run healthy
[ ] No significant 5xx spike
[ ] Cloud Tasks backlog normal
[ ] No unexpected Greenfield failures
[ ] No BigQuery write failures
[ ] No registry failures
[ ] No unusual IAM-denied spike
[ ] No unexpected remediation volume
```

## 29. Before Large PROD Brownfield Run

```text
[ ] Approval confirmed
[ ] PROD environment confirmed
[ ] Registry coverage reviewed
[ ] Unbound projects understood
[ ] Scope approved
[ ] Exclusions approved
[ ] Supported capabilities confirmed
[ ] API quotas reviewed
[ ] Cloud Tasks healthy
[ ] Cloud Run healthy
[ ] Monitoring active
[ ] Operators available
[ ] Emergency stop understood
[ ] run_id will be captured
```

## 30. Post-Run Review

```text
[ ] Discovery count
[ ] Compliance count
[ ] Planned count
[ ] Execution count
[ ] Success count
[ ] Failure count
[ ] Remaining work
[ ] Top failure causes
[ ] API quota behaviour
[ ] Cost
[ ] Dashboard
[ ] Unexpected metadata changes
```

## 31. Cost Anomaly

If cost unexpectedly rises:

```text
1. Identify DEV or PROD
2. Identify service causing increase
3. Check Brownfield frequency
4. Check Cloud Run volume/duration
5. Check Cloud Tasks retries
6. Check Pub/Sub/Eventarc volume
7. Check Logging ingestion
8. Check BigQuery query bytes
9. Check dashboard refresh frequency
10. Check duplicate/failing operations
```

## 32. New Resource Capability

Before enabling a new resource type:

```text
1. Verify official GCP metadata support
2. Verify CAI asset type
3. Verify native read API
4. Verify native update API
5. Verify IAM
6. Implement adapter
7. Add capability mapping
8. Test Brownfield in DEV
9. Verify metadata preservation
10. Create a real resource
11. Capture real Audit Log
12. Add Greenfield mapping where supported
13. Test complete Greenfield path
14. Verify BigQuery evidence
15. Update SUPPORTED_RESOURCES.md
16. Promote capability status
17. Obtain PROD approval
```

## 33. Incident Escalation Data

Collect:

```text
environment
timestamp
run_id if Brownfield
execution_mode
project_id
resource type
resource name
Cloud Run revision
error code
exact denied permission if applicable
relevant Cloud Run logs
relevant BigQuery evidence
whether reproducible in DEV
```

## 34. Quick Command Reference

### DEV Dashboard

```bash
gcloud run services proxy metadata-governance   --project=platform-metadata-dev-001add   --region=us-central1   --port=8080
```

Open Web Preview / forwarded port `8080`.

### PROD Dashboard

```bash
gcloud run services proxy metadata-governance   --project=platform-metadata-prod-92e02c   --region=us-central1   --port=8080
```

Open Web Preview / forwarded port `8080`.

### Authentication

```bash
gcloud auth list
gcloud config list
```

## 35. Operational Rules

Always:

```text
use explicit project IDs
verify DEV vs PROD
capture run_id
preserve evidence
validate changes in DEV first
use least privilege
use controlled production scope
find the first failing stage
```

Never:

```text
hardcode around a registry issue
grant Owner/Editor as a shortcut
assume implemented means production-supported
make the first test organisation-wide
delete incident evidence
assume orchestration completion means worker completion
make Cloud Run public merely for dashboard convenience
```

## 36. Related Documentation

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
├── CLIENT_HANDOVER.md
└── RUNBOOK.md
```

`OPERATIONS.md` contains the detailed operational design.

`RUNBOOK.md` is the practical operator-facing execution and troubleshooting guide.

## 37. Runbook Principle

```text
Do not guess.
Do not bypass governance.
Do not broaden IAM unnecessarily.
Do not hardcode around the problem.

Find the first failing stage.
Capture evidence.
Correct the underlying cause.
Validate in DEV.
Promote through controlled change.
```
