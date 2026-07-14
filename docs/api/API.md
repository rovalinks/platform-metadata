# Platform Metadata Governance API

## Base URL

```
http://<cloud-run-url>
```

---

# Health

## GET /health

Returns service health.

### Response

```json
{
  "status": "healthy"
}
```

---

# Discovery

## GET /discover

Discovers supported Google Cloud resources using Cloud Asset Inventory.

### Response

```json
[
  {
    "asset_type": "compute.googleapis.com/Instance",
    "name": "...",
    "project": "...",
    "labels": {}
  }
]
```

---

# Compliance

## GET /compliance

Evaluates discovered resources against registry metadata.

### Response

```json
{
  "results": [],
  "summary": {
    "total_resources": 2,
    "compliant_resources": 2,
    "non_compliant_resources": 0,
    "compliance_percentage": 100
  }
}
```

---

# Verification

## GET /verify

Verifies that expected labels are present on supported resources.

---

# Enforcement

## GET /enforce

Applies missing labels to supported resources.

Current supported resources:

- Compute Engine VM
- BigQuery Dataset

---

# Report

## GET /report

Returns governance summary.

### Response

```json
{
  "project": "...",
  "total_resources": 176,
  "supported_resources": 2,
  "compliant_resources": 2,
  "non_compliant_resources": 0,
  "enforcement_candidates": 0,
  "compliance_percentage": 100
}
```