# Enterprise Metadata Governance Platform - Cost Model

## 1. Purpose

This document defines the cost model for the Enterprise Metadata Governance Platform on Google Cloud.

It provides a framework for estimating, measuring and controlling the cost of:

- Brownfield discovery and remediation
- Greenfield event-driven governance
- Cloud Run execution
- Cloud Tasks orchestration
- Pub/Sub and Eventarc delivery
- Cloud Logging export
- BigQuery operational evidence and dashboard queries
- Cloud Asset Inventory usage where applicable
- target Google Cloud administrative APIs

The platform uses two dedicated governance projects:

```text
DEV  -> platform-metadata-dev
PROD -> platform-metadata-prod
```

This document deliberately separates architecture assumptions from current Google Cloud pricing. Pricing can change and must be validated against the official Google Cloud pricing pages and actual client billing data before financial approval.

---

## 2. Cost Architecture

The platform is designed around consumption-based managed services.

```text
GREENFIELD

Resource Creation
      |
      v
Cloud Audit Logs
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
Native GCP API
      |
      v
BigQuery Evidence


BROWNFIELD

Cloud Asset Inventory
      |
      v
Discovery / Evaluation
      |
      v
Cloud Tasks
      |
      v
Cloud Run Worker
      |
      v
Native GCP API
      |
      v
BigQuery Evidence
```

There are no dedicated always-on VM or Kubernetes worker fleets in the core architecture.

---

## 3. Cost Principles

The production cost model follows these principles:

```text
Measure actual consumption
Use current official pricing
Separate DEV and PROD
Separate Greenfield and Brownfield
Separate discovery from remediation
Distinguish resources evaluated from resources mutated
Account for retries
Account for logging volume
Account for dashboard query volume
Do not assume every discovered resource creates a mutation
Do not present POC estimates as guaranteed production cost
```

---

## 4. Primary Cost Drivers

The main cost drivers are:

| Component | Primary Consumption Driver |
| --- | --- |
| Cloud Asset Inventory | Discovery/search/export behaviour used by implementation |
| Cloud Run | vCPU, memory, request/execution duration and instance behaviour |
| Cloud Tasks | Task operations and retry volume |
| Pub/Sub | Message/data volume |
| Eventarc | Event delivery according to applicable pricing model |
| Cloud Logging | Log ingestion/storage/routing characteristics |
| BigQuery | Storage, ingestion and query bytes processed/compute model |
| Artifact Registry | Image storage and related transfer where applicable |
| Target APIs | Service-specific API pricing or quotas where applicable |

Administrative metadata update APIs must be validated service-by-service rather than globally assumed to be chargeable or free.

---

## 5. Cost Variables

For modelling, define:

```text
R = resources discovered
E = resources evaluated
N = non-compliant resources
P = remediation plans generated
T = Cloud Tasks created
M = resource mutations attempted
S = successful mutations
F = failed mutations
G = Greenfield events processed
D = duplicate/retried event deliveries
B = BigQuery bytes stored
Q = BigQuery query bytes processed
L = logging bytes generated/exported
```

Normally:

```text
M <= N <= E <= R
```

but retries can cause execution attempts to exceed unique resource counts.

---

## 6. Brownfield Cost Formula

Conceptually:

```text
Brownfield Cost =
    Discovery Cost
  + Orchestration Cost
  + Worker Compute Cost
  + Evidence Storage/Ingestion Cost
  + Reporting Query Cost
  + Logging Cost
  + Applicable Target API Cost
  + Applicable Data Transfer Cost
```

Do not calculate Brownfield cost solely as:

```text
resource count x fixed price
```

because compliance rate, batching, execution duration and retries materially affect consumption.

---

## 7. Greenfield Cost Formula

Conceptually:

```text
Greenfield Cost =
    Audit/Logging Pipeline Cost
  + Pub/Sub Cost
  + Eventarc Cost
  + Cloud Run Processing Cost
  + Evidence Storage/Ingestion Cost
  + Reporting Query Cost
  + Applicable Target API Cost
```

Greenfield consumption scales primarily with relevant resource-creation event volume rather than total organisation resource inventory.

---

## 8. Cloud Asset Inventory

Cloud Asset Inventory is used for Brownfield discovery.

Cost modelling must reflect the exact API/method used by the deployed implementation.

Before assigning a cost:

```text
1. Identify the actual CAI API/method
2. Check current official pricing
3. Check quotas
4. Measure calls/operations for representative runs
5. Extrapolate from measured behaviour
```

Do not assume that one discovered resource equals one separately billable CAI API request.

---

## 9. Cloud Run

Cloud Run cost depends on the deployed billing model and actual resource consumption.

Measure:

```text
request count
worker invocation count
vCPU allocation
memory allocation
execution duration
instance reuse
minimum instances
maximum instances
concurrency
idle configuration where applicable
```

The architecture should normally keep minimum instances at zero unless a measured latency requirement justifies otherwise.

---

## 10. Brownfield Cloud Run Consumption

Brownfield Cloud Run has two major execution patterns:

```text
orchestration/discovery
worker remediation
```

Worker cost depends heavily on:

```text
resources per batch
API latency
parallelism
number of mutations
operation polling
retries
```

Therefore:

```text
1,000,000 discovered resources
```

does not necessarily mean:

```text
1,000,000 independent Cloud Run requests
```

when batching is used.

---

## 11. Cloud Tasks

Cloud Tasks is used to decouple Brownfield planning from remediation execution.

Cost drivers include:

```text
tasks created
task dispatches
retries
```

With:

```text
REMEDIATION_BATCH_SIZE = 500
```

a theoretical 1,000,000 planned resources could require approximately:

```text
1,000,000 / 500 = 2,000 batches
```

if every resource required remediation and every batch contained 500 resources.

Actual task count must come from the deployed batching implementation and remediation population.

---

## 12. Pub/Sub

Pub/Sub is part of the Greenfield event pipeline.

Cost is driven primarily by message/data volume and the applicable delivery model.

Measure:

```text
events published
message size
duplicate deliveries
retention configuration
subscription/delivery behaviour
```

The organisation sink should avoid exporting irrelevant events because unnecessary event volume increases both processing noise and potential cost.

---

## 13. Eventarc

Eventarc routes Greenfield events from the central Pub/Sub integration to Cloud Run.

Production estimates must use the current pricing applicable to the trigger/event transport configuration.

Measure real event volume in DEV or a controlled production period before extrapolating enterprise monthly cost.

---

## 14. Cloud Logging

Logging cost can become material in large estates.

Cost controls include:

```text
export only required Greenfield events
avoid unnecessary DEBUG logging in PROD
use structured concise logs
avoid logging complete large payloads repeatedly
review retention
review exclusion/routing configuration
```

The platform should retain enough information for diagnosis without duplicating entire event payloads unnecessarily.

---

## 15. BigQuery

BigQuery stores operational governance evidence.

Core tables:

```text
resource_snapshot
compliance_snapshot
remediation_plan
remediation_execution
```

Cost drivers include:

```text
rows written
bytes stored
retention
partitioning
query bytes processed
dashboard refresh frequency
historical analysis
```

---

## 16. BigQuery Query Cost Control

Dashboard and operational queries should use:

```text
partition filters
bounded time ranges
selected columns
run_id filters
execution_mode filters
aggregation
latest-state semantics
```

Avoid repeatedly scanning full historical tables for every dashboard refresh.

---

## 17. BigQuery Storage Growth

Storage growth is driven by historical evidence retention.

Approximate model:

```text
Monthly Storage Growth =
    Snapshot Bytes
  + Compliance Bytes
  + Plan Bytes
  + Execution Bytes
```

For production forecasting, measure average bytes per row from representative data rather than assuming a fixed row size.

---

## 18. Dashboard Cost

The dashboard itself should not require dedicated always-on compute beyond the existing serverless application architecture.

Its primary incremental costs are:

```text
Cloud Run requests
BigQuery queries
logging
```

Dashboard polling frequency should be reasonable.

Do not refresh expensive organisation-wide queries every few seconds.

---

## 19. Target Resource APIs

The platform invokes native Google Cloud administrative APIs to read and update metadata.

Examples include:

```text
Compute setLabels
Storage bucket update
BigQuery dataset/table update
Cloud SQL instance update
GKE cluster update
Pub/Sub update
Cloud Run service update
```

For each enabled resource type:

```text
[ ] Verify current API pricing
[ ] Verify quota
[ ] Verify rate limits
[ ] Verify long-running operation behaviour
```

Do not make a blanket financial assumption covering every Google Cloud service.

---

## 20. DEV Cost

`platform-metadata-dev` should remain intentionally low volume.

Cost controls include:

```text
small test projects
small Brownfield scopes
temporary test resources
limited dashboard traffic
controlled Greenfield events
no unnecessary minimum instances
cleanup of temporary resources
```

DEV should provide representative behaviour without replicating full production volume.

---

## 21. PROD Cost

`platform-metadata-prod` carries:

```text
organisation event processing
production Brownfield runs
production operational evidence
production dashboard traffic
```

Cost monitoring should therefore be separated from DEV.

Use project-level billing reporting and labels/tags on platform infrastructure where appropriate.

---

## 22. One-Million-Resource Scenario

A one-million-resource Brownfield scenario must be modelled using measured values.

Input assumptions should include:

```text
Resources discovered:            1,000,000
Compliance percentage:           measured/assumed
Non-compliant percentage:        measured/assumed
Average worker duration:         measured
Batch size:                      configured
Parallelism:                     configured
Average API calls/resource:      measured
Retry percentage:                measured
Evidence bytes/resource:         measured
Dashboard query volume:          measured
```

Example:

```text
R = 1,000,000

If 20% require remediation:

N = 200,000

At batch size 500:

Approximate initial batches = 400
```

This is materially different from assuming one million Cloud Tasks.

---

## 23. Previous POC Estimate

An earlier working estimate discussed approximately:

```text
$30.41
```

for a one-million-resource sweep.

That figure must be treated as a POC assumption only, not an approved production estimate.

Several inputs in that calculation require validation against:

```text
the actual CAI method
current Google Cloud pricing
actual batching
actual Cloud Run execution
actual BigQuery ingestion/storage model
actual logging/event volume
actual remediation percentage
```

The value should not be presented to the client as an exact guaranteed cost.

---

## 24. Production Cost Estimation Method

Use the following method:

```text
Step 1 - Run representative DEV workload
Step 2 - Capture actual resource counts
Step 3 - Capture compliance ratio
Step 4 - Capture tasks/batches
Step 5 - Capture Cloud Run execution metrics
Step 6 - Capture BigQuery bytes
Step 7 - Capture Pub/Sub/Eventarc volume
Step 8 - Capture Logging volume
Step 9 - Review actual billing
Step 10 - Extrapolate to production volume
Step 11 - Add retry/growth contingency
Step 12 - Review against current official pricing
```

---

## 25. Cost per Resource

After representative production measurements, calculate:

```text
Discovery Cost / Resource Discovered

Evaluation Cost / Resource Evaluated

Remediation Cost / Resource Mutated

Greenfield Cost / Event Processed
```

These ratios are useful for forecasting but should be recalculated after major architecture or pricing changes.

---

## 26. Compliance Ratio Impact

The percentage of already-compliant resources has a major cost impact.

Example:

```text
1,000,000 discovered
95% compliant
5% non-compliant
```

means only approximately:

```text
50,000
```

resources require mutation, assuming one mutation per non-compliant resource.

Discovery/evaluation cost still exists, but worker/API consumption is significantly lower than a 100% remediation scenario.

---

## 27. Retry Cost

Retries increase:

```text
Cloud Run execution
Cloud Tasks operations
API calls
logging
BigQuery execution evidence
```

Track:

```text
retry rate
failure type
service
resource type
```

A high retry rate should be treated as both an operational and cost defect.

---

## 28. Cost of Failed Remediation

Failed operations still consume platform resources.

Therefore:

```text
Failed != Free
```

Repeated permission errors or unsupported operations can create avoidable cost and noise.

Capability gates should prevent known unsupported operations from entering the worker path.

---

## 29. Brownfield Scheduling Strategy

Large Brownfield sweeps need not run continuously.

Potential strategy:

```text
initial baseline sweep
        |
        v
targeted periodic Brownfield reconciliation
        +
continuous Greenfield governance
```

The appropriate schedule depends on the client's compliance requirements.

Greenfield reduces, but does not necessarily eliminate, the need for Brownfield reconciliation.

---

## 30. Cost Optimisation Controls

Primary controls:

```text
[ ] Serverless compute
[ ] Minimum instances zero unless justified
[ ] Cloud Tasks batching
[ ] Controlled worker parallelism
[ ] Capability filtering before mutation
[ ] Registry filtering
[ ] Explicit exclusions
[ ] Narrow Greenfield sink filters
[ ] BigQuery partition-aware queries
[ ] Appropriate evidence retention
[ ] Controlled dashboard refresh
[ ] Production log-level discipline
[ ] Retry monitoring
```

---

## 31. Cost Anomaly Indicators

Investigate:

```text
unexpected Cloud Run request spike
unexpected Pub/Sub event spike
Cloud Tasks retry growth
BigQuery query bytes spike
Logging ingestion spike
unexpected Brownfield frequency
unexpected remediation volume
duplicate event increase
```

These can indicate either workload growth or platform defects.

---

## 32. Budgeting and Alerts

For both governance projects, configure client-approved billing controls such as:

```text
budgets
budget notifications
billing export
project-level cost reporting
```

Budget thresholds should be based on measured baseline consumption.

Budget alerts are financial notifications and should not be treated as hard service shutdown controls.

---

## 33. Billing Export

Where available in the client organisation, use Cloud Billing export to BigQuery for actual cost analysis.

This allows the platform team to compare:

```text
governance activity
```

against:

```text
actual billed consumption
```

for the same period.

---

## 34. Monthly Cost Review

Recommended monthly review:

```text
Brownfield runs performed
Greenfield events processed
resources remediated
retry rate
Cloud Run cost
Cloud Tasks cost
Pub/Sub/Eventarc cost
Logging cost
BigQuery cost
unexpected cost anomalies
forecast for next period
```

---

## 35. Architecture Cost Benefit

The serverless architecture provides several structural cost benefits:

### Zero dedicated idle worker fleet

No permanently running VM remediation servers are required.

### Elastic Brownfield execution

Compute is consumed when discovery/remediation runs.

### Event-driven Greenfield

The platform reacts to relevant creation events rather than continuously polling the entire estate.

### Managed orchestration

Cloud Tasks provides controlled asynchronous execution without a custom queue cluster.

### Shared central governance

One central governance platform can serve many workload projects rather than deploying governance compute into every project.

---

## 36. Cost Trade-Offs

Serverless does not mean zero cost.

Trade-offs include:

```text
event/logging volume
historical evidence retention
high-frequency dashboard queries
large Brownfield sweeps
high retry rates
API quota management
```

The architecture optimises for consumption-based cost and low operational overhead rather than claiming that all governance activity is free.

---

## 37. Financial Approval Checklist

Before providing a client production estimate:

```text
[ ] Current Google Cloud pricing verified
[ ] Actual architecture confirmed
[ ] Actual CAI method confirmed
[ ] Resource volume confirmed
[ ] Compliance ratio estimated
[ ] Batch configuration confirmed
[ ] Worker timing measured
[ ] Retry rate measured
[ ] BigQuery volume measured
[ ] Logging volume measured
[ ] Greenfield monthly event rate estimated
[ ] Dashboard query rate estimated
[ ] Billing export reviewed where available
[ ] Contingency documented
```

---

## 38. Cost Model Ownership

The cost model should be jointly maintained by:

```text
Platform Engineering
FinOps / Cloud Economics
Application Governance
Client Cloud Operations
```

Pricing assumptions should be reviewed when:

```text
Google Cloud pricing changes
architecture changes
resource volume materially changes
new adapters are enabled
batching/concurrency changes
retention changes
```

---

## 39. Final Cost Position

The platform is intentionally designed to be:

```text
serverless
consumption-based
event-driven
batch-controlled
centrally operated
```

This avoids the cost of dedicated idle governance infrastructure.

However, production financial statements must be based on actual consumption and current Google Cloud pricing.

The correct enterprise message is:

> The architecture is designed for low idle cost and elastic consumption. Exact production cost depends on resource volume, compliance ratio, event volume, execution duration, retries, evidence retention and current Google Cloud pricing.

---

## 40. Related Documentation

```text
README.md
docs/ARCHITECTURE.md
docs/BROWNFIELD.md
docs/GREENFIELD.md
docs/DATA_MODEL.md
docs/OPERATIONS.md
docs/PRODUCTION_READINESS.md
docs/COST_MODEL.md
```
