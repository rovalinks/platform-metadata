# IAM Roles and Permissions

# Purpose

This document describes the Identity and Access Management (IAM) roles required to deploy, operate, and maintain the Enterprise Metadata Governance Platform.

The platform follows the principle of least privilege while providing sufficient permissions to discover, evaluate, remediate, and report on supported Google Cloud resources.

---

# Service Accounts

The platform uses the following service accounts.

| Service Account | Purpose |
|-----------------|---------|
| metadata-governance | Cloud Run application |
| Eventarc Service Agent | Event delivery |
| Pub/Sub Service Agent | Event transport |
| Cloud Build Service Account | Container builds |
| Artifact Registry Service Agent | Image storage |

---

# Cloud Run Service Account

The Cloud Run service executes:

- Brownfield discovery
- Greenfield remediation
- Reporting APIs
- Dashboard APIs

---

## Cloud Asset Inventory

Role

```
roles/cloudasset.viewer
```

Purpose

- Discover supported resources
- Read asset metadata
- Brownfield inventory

---

## BigQuery Job User

Role

```
roles/bigquery.jobUser
```

Purpose

- Execute reporting queries

---

## BigQuery Data Editor

Role

```
roles/bigquery.dataEditor
```

Purpose

- Insert snapshots
- Store remediation plans
- Store execution history

---

## BigQuery Data Viewer

Role

```
roles/bigquery.dataViewer
```

Purpose

- Read reporting data
- Dashboard queries

---

## Resource Manager Tag User

Role

```
roles/resourcemanager.tagUser
```

Purpose

- Create TagBindings
- Apply Resource Manager Tags

---

## Resource Manager Tag Viewer

Role

```
roles/resourcemanager.tagViewer
```

Purpose

- Read TagKeys
- Read TagValues
- Read TagBindings

---

## Logging Viewer

Role

```
roles/logging.viewer
```

Purpose

- Read Audit Logs
- Troubleshooting

---

## Pub/Sub Subscriber

Role

```
roles/pubsub.subscriber
```

Purpose

- Receive Eventarc events

---

## Pub/Sub Viewer

Role

```
roles/pubsub.viewer
```

Purpose

- Read Pub/Sub configuration

---

## Storage Admin

Role

```
roles/storage.admin
```

Purpose

- Update Cloud Storage bucket labels

---

## Compute Admin

Role

```
roles/compute.admin
```

Purpose

- Update Compute Engine labels

Where possible, replace with narrower custom roles in production.

---

## Cloud SQL Admin

Role

```
roles/cloudsql.admin
```

Purpose

- Update Cloud SQL labels

---

## Artifact Registry Administrator

Role

```
roles/artifactregistry.admin
```

Purpose

- Update repository labels

---

## Secret Manager Admin

Role

```
roles/secretmanager.admin
```

Purpose

- Update Secret labels

---

## Cloud KMS Admin

Role

```
roles/cloudkms.admin
```

Purpose

- Update CryptoKey labels

---

# Eventarc

Required permissions

```
roles/eventarc.eventReceiver
```

Purpose

Receive Audit Log events.

---

# Cloud Build

Required permissions

```
roles/cloudbuild.builds.editor
```

Purpose

Container image builds.

---

# Artifact Registry

Required permissions

```
roles/artifactregistry.writer
```

Purpose

Push Cloud Run images.

---

# Organization Roles

For organization-wide governance the Cloud Run service account should be granted read access at the organization level where appropriate.

Typical organization-level roles include:

- Cloud Asset Viewer
- Tag Viewer

Project-specific update permissions should remain at the project level unless organization-wide remediation is explicitly required.

---

# Production Recommendations

For production deployments:

- Use dedicated service accounts.
- Avoid using Owner or Editor roles.
- Prefer predefined or custom least-privilege roles.
- Separate deployment permissions from runtime permissions.
- Audit IAM bindings regularly.

---

# Permission Summary

| Capability | Required Role |
|------------|---------------|
| Discover resources | Cloud Asset Viewer |
| Read tags | Resource Manager Tag Viewer |
| Apply tags | Resource Manager Tag User |
| Read reports | BigQuery Data Viewer |
| Write reports | BigQuery Data Editor |
| Execute queries | BigQuery Job User |
| Receive events | Pub/Sub Subscriber |
| Read logs | Logging Viewer |
| Update Compute resources | Compute Admin |
| Update Storage resources | Storage Admin |
| Update Cloud SQL | Cloud SQL Admin |
| Update Artifact Registry | Artifact Registry Administrator |
| Update Secret Manager | Secret Manager Admin |
| Update Cloud KMS | Cloud KMS Admin |

---

# Security Considerations

The platform is designed around the following security principles:

- Least privilege
- Dedicated service accounts
- No embedded credentials
- Cloud Audit Logging
- IAM separation of duties
- Infrastructure as Code
- Workload Identity Federation (where supported)

---

# Summary

The Enterprise Metadata Governance Platform requires a combination of discovery, reporting, event processing, and resource update permissions. Production deployments should periodically review IAM assignments and replace broad administrative roles with custom roles wherever possible.