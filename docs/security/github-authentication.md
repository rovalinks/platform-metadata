# GitHub Authentication

## Authentication Method

GitHub Actions authenticates using OpenID Connect (OIDC).

Google Cloud exchanges the OIDC token using Workload Identity Federation.

The authenticated workflow impersonates the GitHub Actions service account.

## Security Benefits

- No JSON service account keys
- Short-lived credentials
- Repository-level trust
- Least privilege

## Required IAM Roles

The GitHub Actions service account requires:

- Cloud Build Editor
- Artifact Registry Writer
- Storage Object Admin
- Cloud Run Developer
- Service Usage Consumer

These permissions are granted at the project level and are used only during CI/CD execution.