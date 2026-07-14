# Executive Dashboard

# Purpose

The Executive Dashboard provides a centralized view of metadata governance across the Google Cloud environment.

It is intended for:

- Executives
- Cloud Platform Teams
- Governance Teams
- Operations Teams
- FinOps Teams

The dashboard combines Brownfield and Greenfield governance into a single reporting interface.

---

# Dashboard Overview

The dashboard provides two reporting scopes.

- Organization
- Project

Organization scope provides an enterprise-wide view.

Project scope provides detailed reporting for an individual Google Cloud project.

---

# Dashboard Layout

The dashboard consists of the following sections.

1. Executive Summary
2. Brownfield Summary
3. Greenfield Summary
4. Projects
5. Resource Types
6. Recent Remediation Runs
7. Top Non-Compliant Resources

---

# Executive Summary

The Executive Summary displays high-level governance KPIs.

Metrics include:

- Total Resources
- Supported Resources
- Projects
- Compliance Percentage
- Successful Remediations
- Failed Remediations
- Planned Remediations
- Remaining Remediations

Purpose:

Provides an overall governance health score.

---

# Brownfield Summary

Brownfield metrics include:

- Planned Remediations
- Completed Remediations
- Remaining Remediations
- Failed Remediations
- Success Rate

Purpose:

Tracks bulk remediation progress across the estate.

---

# Greenfield Summary

Greenfield metrics include:

- Total Events
- Automatically Remediated
- Already Compliant
- Failed
- Average Processing Time

Purpose:

Measures real-time governance effectiveness.

---

# Projects

Displays every onboarded project discovered by the governance platform.

Columns include:

- Project ID
- Total Resources
- Compliant Resources
- Non-Compliant Resources
- Compliance Percentage

Purpose:

Provides project-level governance visibility.

---

# Resource Types

Displays compliance grouped by supported resource type.

Examples include:

- Compute Engine Instances
- Compute Engine Disks
- Cloud Storage Buckets
- BigQuery Datasets
- Pub/Sub Topics
- Cloud SQL
- Secret Manager
- Cloud KMS

Purpose:

Highlights services requiring governance improvements.

---

# Recent Remediation Runs

Displays recent Brownfield remediation executions.

Columns include:

- Run ID
- Planned
- Completed
- Failed
- Remaining
- Success Rate
- Start Time

Purpose:

Provides operational visibility into remediation activity.

---

# Top Non-Compliant Resources

Displays resources requiring governance attention.

Columns include:

- Resource Name
- Resource Type
- Missing Metadata
- Incorrect Metadata

Purpose:

Allows rapid identification of governance drift.

---

# Organization Scope

Organization scope aggregates reporting across all onboarded Google Cloud projects.

Typical use cases:

- Executive reporting
- Compliance reviews
- FinOps reporting
- Governance scorecards

---

# Project Scope

Project scope filters reporting to a single Google Cloud project.

Typical use cases:

- Application support
- Project governance
- Platform engineering
- Operational reviews

---

# Refresh

The dashboard can be refreshed at any time.

Refresh updates:

- Brownfield metrics
- Greenfield metrics
- Compliance
- Resource inventory
- Remediation history

---

# Reporting Data

The dashboard reads reporting data from BigQuery.

Primary reporting tables:

- resource_snapshot
- compliance_snapshot
- remediation_plan
- remediation_execution

The dashboard is read-only and never modifies governance data.

---

# Security

Dashboard access is controlled through Cloud Run authentication and Google Cloud IAM.

Only authenticated users with the appropriate permissions can access reporting data.

---

# Future Enhancements

Planned enhancements include:

- Application-level filtering
- Drill-down navigation
- Historical trends
- Compliance forecasting
- Executive scorecards
- FinOps reporting
- Export to CSV
- Export to PDF

---

# Summary

The Executive Dashboard provides a centralized, organization-wide view of metadata governance, enabling operational teams and leadership to monitor compliance, remediation progress, and governance health across supported Google Cloud resources.