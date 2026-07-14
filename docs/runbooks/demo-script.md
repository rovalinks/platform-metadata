# Customer Demonstration Script

Estimated duration: 20 minutes

---

## Introduction (2 minutes)

Today I'll demonstrate a registry-driven metadata governance platform built on Google Cloud.

The platform discovers cloud resources, validates metadata against a central application registry, reports compliance, and automatically applies governance metadata to supported resources.

---

## Platform Architecture (3 minutes)

Explain:

Application Registry

↓

Governance Engine

↓

Cloud Asset Inventory

↓

Compliance Engine

↓

Enforcement Engine

↓

Verification

↓

Reporting

Everything is driven from the registry.

---

## Show Registry (2 minutes)

Open

registry/applications/

Show:

APP000001.yaml

Explain:

Every application has its own YAML.

No code changes.

---

## Show Governance APIs (5 minutes)

Open:

/health

/discover

/compliance

/report

Explain each response.

---

## Demonstrate Enforcement (3 minutes)

Remove labels from a Compute VM.

Run:

GET /enforce

Show labels applied.

Run:

GET /verify

Show resource is compliant.

Repeat for the BigQuery dataset.

---

## Demonstrate Governance Process (3 minutes)

Create:

APP000002.yaml

Create feature branch.

Push.

Show GitHub Actions validation.

Open Pull Request.

Show approval required.

Merge.

Deployment starts automatically.

Explain that new applications are now governed without changing Python code.

---

## Future Roadmap (2 minutes)

Explain that adding support for new Google Cloud services only requires implementing a new adapter.

The governance engine itself does not change.

This demonstrates an extensible architecture suitable for enterprise adoption.