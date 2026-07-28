# Client Demonstration Guide

# Objective

Demonstrate a registry-driven metadata governance platform for Google Cloud.

---

# Step 1 - Application Registry

Open:

```
registry/applications/APP000001.yaml
```

Show the application metadata:

- Product
- Team
- Owner
- Cost Centre
- Environment
- Business Criticality

Explain that governance is driven entirely from the registry.

---

# Step 2 - Validate Registry

Run:

```bash
python validation/validate_registry.py
```

Expected:

```
Registry validation successful.
```

---

# Step 3 - Discover Resources

Call:

```
GET /discover
```

Explain that Cloud Asset Inventory discovers supported Google Cloud resources.

---

# Step 4 - Compliance

Call:

```
GET /compliance
```

Show:

- compliant resources
- non-compliant resources
- missing labels
- compliance percentage

---

# Step 5 - Enforcement

Call:

```
GET /enforce
```

Explain that supported resources are automatically updated using the registry metadata.

Current supported resource types:

- Compute Engine Instance
- BigQuery Dataset

---

# Step 6 - Verification

Call:

```
GET /verify
```

Demonstrate that labels have been successfully applied.

---

# Step 7 - Governance Report

Call:

```
GET /report
```

Review:

- Total resources
- Supported resources
- Compliant resources
- Enforcement candidates
- Compliance percentage

---

# Key Capabilities

- Registry-driven governance
- Cloud Asset Inventory discovery
- Compliance evaluation
- Metadata enforcement
- Metadata verification
- Governance reporting
- Compute Engine support
- BigQuery Dataset support

---

# Current Scope

The current POC supports:

- Single Google Cloud project per deployment
- Multiple application registry files
- Compute Engine Instance enforcement
- BigQuery Dataset enforcement

The architecture is designed to be extended to additional resource types and broader multi-project scenarios in future iterations.