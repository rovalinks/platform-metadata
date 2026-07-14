# Metadata Governance Engine

## Runtime

- Cloud Run
- Flask
- Python 3.13

---

## Purpose

The Cloud Run service provides the runtime for the Metadata Governance Platform.

Responsibilities include:

- Reading registry metadata
- Discovering Google Cloud resources
- Evaluating metadata compliance
- Applying metadata to supported resources
- Verifying metadata
- Producing governance reports

---

## Runtime Components

## Clients

- Cloud Asset Inventory
- Compute Engine
- BigQuery

## Services

- Governance Service
- Discovery Service
- Capability Service
- Compliance Service
- Enforcement Service
- Executor Service
- Verification Service
- Report Service

---

## Handlers

- Health
- Discovery
- Compliance
- Verification
- Enforcement
- Reporting

---

## Models

- Resource
- ComplianceResult
- ComplianceSummary
- VerificationResult
- GovernanceReport

---

## Execution Flow

Registry
      │
      ▼
Governance Service
      │
      ▼
Discovery Service
      │
      ▼
Compliance Service
      │
      ▼
Enforcement Service
      │
      ▼
Executor Service
      │
      ▼
Resource Adapter
      ├── Compute Engine
      └── BigQuery

---

## Error Handling

All Google Cloud API exceptions are handled centrally.

Resource execution continues even if an individual resource update fails.

---

## Testing

The repository uses a root-level `pytest.ini` to configure the Python module search path.

This allows test files to import application modules exactly as the application does.

Unit tests cover:

- Governance
- Compliance
- Capability
- Adapter
- Executor
- Reporting

Google Cloud SDK calls are mocked to ensure deterministic tests.

---

## Endpoints

### GET /

Returns service health.

### GET /health

Returns service status and registered applications.

### GET /discover

Returns resources discovered using Google Cloud Asset Inventory.

### GET /compliance

Returns governance results by comparing discovered resources against the Metadata Registry.

### GET /enforce

Executes remediation actions based on defined governance policies.

### GET /verify

Validates current resource states against the Metadata Registry.

### GET /report

Generates and returns comprehensive governance and discovery reports.

---

## Response Serialization

All response models implement a `to_dict()` method, ensuring a consistent JSON contract for every REST endpoint.

---

## Logging

The following services emit operational logs:

- Discovery
- Governance
- Compliance
- Enforcement
- Executor
- Verification
- Reporting

Logs are written to stdout and collected automatically by Cloud Run and Cloud Logging.

---

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| /health | Health endpoint |
| /discover | Resource discovery |
| /compliance | Compliance evaluation |
| /verify | Metadata verification |
| /enforce | Metadata enforcement |
| /report | Governance reporting |