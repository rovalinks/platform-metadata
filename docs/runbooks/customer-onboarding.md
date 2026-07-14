# Customer Onboarding Guide

# Overview

Applications are onboarded by adding registry files.

No Python code changes are required.

---

# Create a Registry File

Example:

APP000002.yaml

Place the file under

registry/applications/

---

# Create Feature Branch

git checkout -b feature/add-payments

---

# Commit

git add .

git commit -m "Add Payments application"

git push origin feature/add-payments

---

# Pull Request

Open a Pull Request.

GitHub automatically validates:

- Schema
- Required fields
- Registry structure

If validation fails:

Merge is blocked.

---

# Approval

A platform administrator reviews the Pull Request.

After approval:

Merge to main.

---

# Automatic Deployment

GitHub Actions automatically:

- Builds Docker image
- Pushes Artifact Registry
- Deploys Cloud Run

No manual deployment is required.

---

# Automatic Governance

The Governance Engine automatically:

- Reads every YAML file
- Discovers resources
- Evaluates compliance
- Enforces labels
- Verifies metadata
- Generates reports

No code changes are required for new applications.