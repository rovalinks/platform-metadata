# Enterprise Metadata Governance Platform

## Overview

The Enterprise Metadata Governance Platform is a cloud-native governance solution built on Google Cloud Platform (GCP) to automatically discover, evaluate, remediate, and report on metadata compliance across an organization's cloud resources.

The platform supports both:

- Brownfield governance for existing cloud resources.
- Greenfield governance for newly created cloud resources in near real time.

Rather than relying on manual audits or custom scripts, the platform provides centralized governance through policy-driven automation, standardized metadata, enterprise reporting, and Infrastructure as Code.

---

## Business Problem

Large enterprises typically manage thousands of cloud resources across multiple projects and environments. As cloud estates grow, maintaining consistent metadata becomes increasingly difficult.

Missing or inconsistent metadata impacts:

- Cost allocation
- Ownership tracking
- Operational support
- Security investigations
- Regulatory compliance
- FinOps reporting
- Resource lifecycle management

Manual governance approaches are difficult to scale and often lead to inconsistent outcomes.

---

## Solution

The Enterprise Metadata Governance Platform provides an automated governance framework that continuously enforces standardized metadata across supported Google Cloud resources.

The platform delivers:

- Automated discovery of cloud resources
- Metadata compliance evaluation
- Automated remediation
- Organization and project level reporting
- Executive governance dashboards
- Near real-time governance for new resources
- Infrastructure as Code deployment using Terraform

---

# Key Features

## Brownfield Governance

- Project-wide resource discovery
- Compliance evaluation
- Remediation planning
- Automated execution
- Execution tracking
- Audit reporting

---

## Greenfield Governance

- Event-driven governance
- Eventarc integration
- Cloud Logging integration
- Pub/Sub messaging
- Cloud Run processing
- Automatic metadata enforcement

---

## Executive Dashboard

- Organization view
- Project view
- Compliance reporting
- Resource inventory
- Remediation tracking
- Brownfield metrics
- Greenfield metrics
- Executive KPIs

---

## Governance Registry

Application metadata is defined within a centralized registry.

Each application specifies:

- Product
- Team
- Owner
- Budget owner
- Organization
- Department
- Cost center
- Environment
- Business criticality

The registry acts as the single source of truth for governance.

---

# Supported Resources

Current supported resources include:

| Service | Labels | Tags |
|---------|--------|------|
| Compute Engine Instances | ✓ | |
| Compute Engine Disks | ✓ | |
| Cloud Storage Buckets | ✓ | |
| BigQuery Datasets | ✓ | |
| Pub/Sub Topics | | ✓ |
| Artifact Registry | ✓ | |
| Cloud SQL | ✓ | |
| Secret Manager | ✓ | |
| Cloud KMS | ✓ | |

The platform is designed to support additional Google Cloud services through a modular adapter architecture.

---

# High-Level Architecture

The platform consists of the following major components:

- Governance Registry
- Discovery Engine
- Compliance Engine
- Governance Engine
- Remediation Planner
- Execution Engine
- Reporting Engine
- Executive Dashboard

Supporting Google Cloud services include:

- Cloud Run
- Eventarc
- Cloud Logging
- Pub/Sub
- Cloud Asset Inventory
- BigQuery
- Artifact Registry
- Terraform


                                    Enterprise Metadata Governance Platform

                                              +-----------------------+
                                              | Governance Registry   |
                                              | (Application Metadata)|
                                              +-----------+-----------+
                                                          |
                                                          |
                                              Expected Labels / Tags
                                                          |
                                                          v
+-----------------------------------------------------------------------------------------------+
|                                      Cloud Run Platform                                        |
|                                                                                               |
| +------------------+     +------------------+      +------------------+                       |
| | Brownfield       | --> | Compliance       | -->  | Remediation      |                       |
| | Discovery        |     | Evaluation       |      | Planner          |                       |
| +------------------+     +------------------+      +------------------+                       |
|          |                        |                          |                                 |
|          |                        |                          v                                 |
|          |                        |               +----------------------+                     |
|          |                        +-------------> | Remediation Engine   |                     |
|          |                                        +----------+-----------+                     |
|          |                                                   |                                 |
|          +---------------------------------------------------+                                 |
|                                                              |                                 |
+--------------------------------------------------------------|---------------------------------+
                                                               |
                                                               v
                                              Google Cloud Resources

   Compute  Storage  BigQuery  Pub/Sub  Cloud SQL  Secret Manager  Artifact Registry  KMS

                                                               |
                                                               v

                                            +-------------------------------+
                                            | Reporting Repository          |
                                            | BigQuery                      |
                                            | resource_snapshot             |
                                            | compliance_snapshot           |
                                            | remediation_plan             |
                                            | remediation_execution        |
                                            +---------------+---------------+
                                                            |
                                                            |
                                                            v
                                             Executive Governance Dashboard

---


# Brownfield Workflow

1. Discover resources
2. Evaluate compliance
3. Generate remediation plan
4. Execute remediation
5. Persist execution results
6. Publish governance reports


User

   |

POST /brownfield

   |

Cloud Run

   |

Cloud Asset Inventory

   |

Discover Resources

   |

Classification

   |

Compliance Evaluation

   |

Remediation Planning

   |

Remediation Execution

   |

BigQuery Reporting

   |

Dashboard

---

# Greenfield Workflow

1. Resource created
2. Audit Log generated
3. Eventarc trigger activated
4. Pub/Sub message published
5. Cloud Run receives event
6. Resource classified
7. Compliance evaluated
8. Metadata automatically applied
9. Results persisted


Resource Created

        |

Cloud Audit Logs

        |

Logging Sink

        |

Pub/Sub

        |

Eventarc

        |

Cloud Run

        |

Classification

        |

Compliance

        |

Automatic Labels / Tags

        |

BigQuery

        |

Dashboard

---

# Executive Dashboard

The Executive Dashboard provides a real-time governance overview including:

- Executive Summary
- Brownfield status
- Greenfield status
- Project compliance
- Resource type compliance
- Remediation history
- Top non-compliant resources

Dashboard supports:

- Organization scope
- Project scope


Brownfield
                \
                 \
                  \
                   --> resource_snapshot
                   --> compliance_snapshot
                   --> remediation_plan
                   --> remediation_execution
                               |
                               |
                               v
                    Report Repository
                               |
                               |
                     Reporting Service
                               |
                               |
                      REST API (/reports/*)
                               |
                               |
                     Executive Dashboard

---

# Technology Stack

## Infrastructure

- Google Cloud Platform
- Terraform

## Compute

- Cloud Run

## Event Processing

- Eventarc
- Pub/Sub
- Cloud Logging

## Data

- BigQuery

## Programming Language

- Python

## Web Framework

- Flask

---

# Repository Structure

```
cloudrun/
terraform/
registry/
docs/
```

---

# Deployment

Infrastructure is provisioned using Terraform.

Deployment includes:

- Google Cloud APIs
- IAM
- BigQuery
- Cloud Run
- Artifact Registry
- Eventarc
- Pub/Sub
- Logging
- Governance Registry

Detailed deployment instructions are available in:

```
docs/deployment.md
```

---

# Documentation

Additional documentation is available under the `docs` directory.

- Architecture
- Deployment
- Brownfield Governance
- Greenfield Governance
- Dashboard
- Demonstration Guide

---

# Future Enhancements

The platform architecture supports future expansion including:

- Additional Google Cloud resource types
- Multi-organization governance
- Policy-as-Code integration
- Advanced analytics
- Trend reporting
- Compliance forecasting
- FinOps insights
- Executive scorecards

---

# License

Internal Enterprise Platform


# 1. Enterprise Solution Architecture (Main Diagram)

                                    Enterprise Metadata Governance Platform

                                              +-----------------------+
                                              | Governance Registry   |
                                              | (Application Metadata)|
                                              +-----------+-----------+
                                                          |
                                                          |
                                              Expected Labels / Tags
                                                          |
                                                          v
+-----------------------------------------------------------------------------------------------+
|                                      Cloud Run Platform                                        |
|                                                                                               |
| +------------------+     +------------------+      +------------------+                       |
| | Brownfield       | --> | Compliance       | -->  | Remediation      |                       |
| | Discovery        |     | Evaluation       |      | Planner          |                       |
| +------------------+     +------------------+      +------------------+                       |
|          |                        |                          |                                 |
|          |                        |                          v                                 |
|          |                        |               +----------------------+                     |
|          |                        +-------------> | Remediation Engine   |                     |
|          |                                        +----------+-----------+                     |
|          |                                                   |                                 |
|          +---------------------------------------------------+                                 |
|                                                              |                                 |
+--------------------------------------------------------------|---------------------------------+
                                                               |
                                                               v
                                              Google Cloud Resources

   Compute  Storage  BigQuery  Pub/Sub  Cloud SQL  Secret Manager  Artifact Registry  KMS

                                                               |
                                                               v

                                            +-------------------------------+
                                            | Reporting Repository          |
                                            | BigQuery                      |
                                            | resource_snapshot             |
                                            | compliance_snapshot           |
                                            | remediation_plan             |
                                            | remediation_execution        |
                                            +---------------+---------------+
                                                            |
                                                            |
                                                            v
                                             Executive Governance Dashboard


# 2. Brownfield Workflow
User

   |

POST /brownfield

   |

Cloud Run

   |

Cloud Asset Inventory

   |

Discover Resources

   |

Classification

   |

Compliance Evaluation

   |

Remediation Planning

   |

Remediation Execution

   |

BigQuery Reporting

   |

Dashboard

# 3. Greenfield Workflow
Resource Created

        |

Cloud Audit Logs

        |

Logging Sink

        |

Pub/Sub

        |

Eventarc

        |

Cloud Run

        |

Classification

        |

Compliance

        |

Automatic Labels / Tags

        |

BigQuery

        |

Dashboard

# 4. Reporting Architecture

Brownfield
                \
                 \
                  \
                   --> resource_snapshot
                   --> compliance_snapshot
                   --> remediation_plan
                   --> remediation_execution
                               |
                               |
                               v
                    Report Repository
                               |
                               |
                     Reporting Service
                               |
                               |
                      REST API (/reports/*)
                               |
                               |
                     Executive Dashboard
