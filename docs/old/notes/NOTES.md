# Customer Demonstration Guide

# Part 1 - Executive Introduction & Solution Overview

**Duration:** 5-7 Minutes

---

# Introduction

Good morning everyone.

Thank you for taking the time to attend today's demonstration.

Today I'd like to walk you through the Platform Metadata Governance Proof of Concept that we've developed on Google Cloud.

Rather than focusing on the governance problem itself, I'll focus on how this platform has been designed to solve that problem in a scalable, secure and operationally maintainable way.

The objective of this Proof of Concept was to build a cloud-native governance platform that allows platform engineering teams to centrally manage application metadata, continuously evaluate compliance across Google Cloud resources, and automatically remediate supported resources using native Google Cloud services.

The design deliberately avoids hardcoding business rules inside infrastructure or application code.

Instead, governance is driven from a central registry that can evolve independently from the platform itself.

This means that onboarding new applications or updating business ownership does not require modifying Python code or Terraform modules.

Everything is controlled through a governed registry.

---

# Business Objective

The platform addresses four key governance capabilities.

First, it provides a central source of truth for application ownership and business metadata.

Second, it continuously discovers resources deployed within Google Cloud.

Third, it compares discovered resources against the expected metadata defined by the business.

Finally, it automatically remediates supported resources where mandatory metadata is missing.

The overall objective is to reduce manual governance activities while improving consistency, auditability and operational visibility.

---

# Design Principles

Before looking at the implementation, I'd like to briefly explain the design principles that guided the solution.

The platform was designed around six principles.

### 1. Registry-Driven Governance

All governance metadata is stored in registry files rather than embedded into infrastructure code.

This allows business metadata to change independently from application deployments.

Platform teams only need to update registry files.

They do not need to modify Python code.

---

### 2. Cloud-Native Services

Wherever possible, the solution uses managed Google Cloud services rather than custom-built components.

Examples include:

- Cloud Asset Inventory
- Cloud Run
- Artifact Registry
- Workload Identity Federation
- Cloud Logging

Using managed services reduces operational overhead and aligns with Google Cloud best practices.

---

### 3. Infrastructure as Code

All infrastructure is deployed through Terraform.

This includes:

- Service Accounts
- IAM
- Artifact Registry
- Cloud Run
- Workload Identity Federation

This allows environments to be deployed consistently and repeatedly.

---

### 4. Secure Deployment

The deployment pipeline follows Google's recommended authentication model.

GitHub Actions authenticates using Workload Identity Federation.

No service account keys are stored inside GitHub.

Authentication is short-lived and based on OpenID Connect tokens.

This significantly reduces credential management risk.

---

### 5. Modular Architecture

The Governance Engine has been implemented using modular services rather than a single application file.

Each responsibility has been separated.

For example:

- Discovery
- Governance
- Compliance
- Enforcement
- Verification
- Reporting

This improves maintainability and allows additional resource types to be introduced without redesigning the application.

---

### 6. Extensibility

The platform has been designed so that new Google Cloud services can be supported by implementing additional adapters.

The Governance Engine itself remains unchanged.

For example, today the platform supports:

- Compute Engine
- BigQuery Datasets

In the future, additional adapters could be added for services such as:

- Cloud SQL
- Pub/Sub
- GKE
- Cloud Storage
- Secret Manager

without changing the overall architecture.

---

# High-Level Architecture

At a high level, the platform consists of five layers.

The first layer is the Application Registry.

This acts as the single source of truth for business metadata.

Each application is represented by an individual YAML file.

The registry defines information such as:

- Product
- Team
- Owner
- Budget Owner
- Department
- Cost Centre
- Environment
- Business Criticality

Because each application is stored independently, onboarding new applications becomes a metadata exercise rather than a software development activity.

---

The second layer is the Governance Engine running on Cloud Run.

This is the core of the platform.

It is responsible for:

- Reading registry files
- Discovering Google Cloud resources
- Comparing metadata
- Producing compliance reports
- Planning remediation
- Executing supported updates
- Verifying remediation

The Governance Engine itself contains no application-specific business logic.

Everything is driven from the registry.

---

The third layer is Google Cloud.

Discovery is performed using Cloud Asset Inventory.

Rather than calling each individual Google Cloud API separately, Cloud Asset Inventory provides a central inventory of resources across the project.

This significantly simplifies discovery while reducing API complexity.

---

The fourth layer is the Adapter Layer.

Different Google Cloud services expose different APIs for managing labels.

Rather than embedding those API differences into the Governance Engine, each supported service has its own adapter.

Currently the platform includes adapters for:

- Compute Engine
- BigQuery Dataset

This makes the platform straightforward to extend.

---

The fifth layer is the Deployment Pipeline.

Infrastructure is provisioned using Terraform.

Application deployments are performed through GitHub Actions.

Authentication uses Workload Identity Federation.

No long-lived credentials are required.

---

# End-to-End Platform Flow

At a high level, the platform operates as follows.

A platform engineer creates or updates an application registry file.

The registry is validated automatically through GitHub Actions.

After approval, the Governance Engine is deployed automatically.

The Governance Engine discovers resources using Cloud Asset Inventory.

It compares those resources against registry metadata.

Compliance reports are generated.

Where supported, missing labels can be automatically applied.

Finally, verification confirms that remediation completed successfully.

This creates a complete governance lifecycle from application onboarding through to operational compliance.

---

# What Will Be Demonstrated

During today's demonstration I'll walk through the complete platform lifecycle.

We'll start by looking at the repository structure and how governance metadata is organised.

Next we'll examine how a new application is onboarded without writing code.

We'll then deploy the platform and look at the runtime architecture.

After that we'll demonstrate each API, including discovery, compliance evaluation, reporting, enforcement and verification.

Finally, we'll look at the deployment pipeline, security model and discuss how the platform can be extended to support additional Google Cloud services.

The goal is to demonstrate not only that the platform works, but that it has been designed in a way that is maintainable, scalable and suitable for enterprise adoption.

---

# Transition

Now that we've covered the overall architecture and design principles, let's move into the repository itself and see how the platform has been organised, starting with the application registry and governance model.

# Part 2 - Repository Walkthrough & Platform Design

**Duration:** 8-10 Minutes

---

# Repository Overview

Now that we've looked at the overall architecture, let's walk through the repository.

The repository has been organised so that each area of responsibility is isolated from the others.

Rather than having a single application that performs every task, the solution separates infrastructure, governance logic, metadata, validation and testing into dedicated components.

This makes the platform easier to maintain, extend and support.

At the root of the repository we have the following main folders.

```
cloudrun/

terraform/

registry/

validation/

tests/

docs/
```

Each of these serves a specific purpose.

---

# Terraform

I'll begin with the Terraform folder.

Terraform is responsible for provisioning the platform infrastructure.

Everything required to run the Governance Platform is deployed using Infrastructure as Code.

This includes:

- Service Accounts
- IAM
- Artifact Registry
- Cloud Run
- Workload Identity Federation

One important design decision was ensuring that no infrastructure configuration is performed manually after deployment.

Every infrastructure component is version controlled.

This provides repeatable deployments across development, testing and production environments.

---

# Cloud Run Application

Next we have the Cloud Run application.

This is the Governance Engine.

The Governance Engine is intentionally modular.

Instead of placing every responsibility inside a single application file, responsibilities have been separated into dedicated services.

```
clients/

handlers/

models/

registry/

services/

utils/
```

Each folder has a single responsibility.

This reduces complexity and allows each component to evolve independently.

---

# Clients

The Clients folder contains the Google Cloud integrations.

Each client communicates with one Google Cloud service.

Examples include:

Cloud Asset Inventory

Compute Engine

BigQuery

Cloud Storage

Rather than allowing business logic to directly call Google Cloud APIs, all API interactions are isolated within these clients.

If Google changes an API in the future, only the client needs updating.

The Governance Engine remains unchanged.

---

# Services

The Services folder contains the business logic.

This is where the platform makes governance decisions.

Each service has one clearly defined responsibility.

Discovery Service

Responsible for discovering resources.

---

Governance Service

Responsible for reading registry metadata.

---

Compliance Service

Responsible for comparing actual metadata with expected metadata.

---

Enforcement Service

Responsible for determining which resources require remediation.

---

Executor Service

Responsible for executing remediation plans.

---

Verification Service

Responsible for confirming remediation.

---

Report Service

Responsible for producing governance summaries.

This separation follows the Single Responsibility Principle and makes unit testing much simpler.

---

# Adapter Layer

One of the most important architectural decisions is the Adapter Layer.

Every Google Cloud service exposes a different API.

Updating labels on a Compute Engine instance is different from updating labels on a BigQuery dataset.

Rather than embedding these differences into the Governance Engine, each supported resource type has its own adapter.

The Enforcement Engine simply says

"I need labels applied."

The Adapter decides

"How do I apply those labels?"

This means that adding support for another Google Cloud service only requires implementing another adapter.

The rest of the platform remains unchanged.

---

# Capability Service

Another important service is the Capability Service.

Not every Google Cloud resource supports labels.

Rather than attempting remediation on unsupported resources, the Capability Service maintains a catalogue of supported resource types.

During compliance evaluation the platform checks whether a resource supports labels.

If not, it is excluded automatically.

This prevents unnecessary API calls and avoids unsupported operations.

---

# Models

The Models folder contains all shared data structures used throughout the application.

Examples include

Resource

ComplianceResult

ComplianceSummary

GovernanceReport

VerificationResult

ExecutionResult

Using dedicated models ensures that every service communicates using well-defined objects rather than raw dictionaries.

Each model also provides consistent JSON serialization for the REST APIs.

---

# Utilities

The Utilities folder contains reusable functionality shared across the platform.

Examples include

Label normalisation

Structured logging

Exception handling

Supported resource catalogue

Rather than duplicating logic across multiple services, common functionality is centralised.

---

# Application Registry

Now let's move to the Registry.

This is the most important component from a governance perspective.

Rather than hardcoding ownership information inside Terraform or application code, each application is represented by its own YAML file.

For example

```
APP000001.yaml
```

Inside this file we define business metadata such as

Product

Owner

Team

Budget Owner

Department

Cost Centre

Environment

Business Criticality

Project Bindings

This file becomes the single source of truth for the application.

---

# Why Registry-Driven Governance?

This is one of the biggest advantages of the platform.

Imagine another application needs onboarding.

Traditional approaches often require

Terraform changes

Python changes

Database changes

Configuration updates

In this platform none of those are required.

A platform engineer simply creates

```
APP000002.yaml
```

The Governance Engine automatically discovers it.

No code changes.

No recompilation.

No redeployment of business logic.

The platform scales naturally as more applications are added.

---

# Registry Validation

Every registry file is validated automatically.

Validation includes

YAML syntax

JSON Schema validation

Mandatory fields

Project bindings

Metadata consistency

This prevents invalid governance metadata from reaching production.

If validation fails

The Pull Request cannot be merged.

This provides governance before deployment.

---

# Unit Testing

The repository also contains a comprehensive unit testing framework.

Business services are tested independently.

Examples include

Capability Service

Governance Service

Compliance Service

Adapter Service

Executor Service

Report Service

Google Cloud SDK calls are mocked.

This ensures tests are deterministic and do not require live Google Cloud resources.

As a result, business logic can be validated quickly during development and CI/CD.

---

# Documentation

The repository also includes operational documentation.

Deployment Guide

Architecture

API Documentation

Roadmap

Customer Onboarding Guide

Troubleshooting Guide

This allows another engineer to deploy and operate the platform without relying on tribal knowledge.

---

# Security Model

Before moving into the live demonstration, I'd like to briefly touch on security.

Authentication between GitHub and Google Cloud uses Workload Identity Federation.

There are no long-lived service account keys.

Service Accounts follow the principle of least privilege.

Infrastructure is deployed using Terraform.

Registry changes require Pull Request approval.

Registry validation runs before merge.

Every deployment is traceable through GitHub Actions.

This provides a secure deployment pipeline aligned with Google Cloud recommendations.

---

# Transition

Now that we've explored how the repository is structured and why the platform has been designed this way, let's move into the live demonstration.

We'll begin by onboarding an application through the registry and then walk through the complete governance lifecycle, from resource discovery to automated metadata enforcement and verification.

# Part 3 - Live Demonstration

**Duration:** 15-20 Minutes

---

# Introduction to the Live Demonstration

Now that we've discussed the architecture and repository structure, I'd like to demonstrate how the platform behaves in practice.

Rather than simply showing code, I'll demonstrate the complete governance lifecycle.

The objective is to show how an application is onboarded, how resources are discovered, how compliance is evaluated, how supported resources are remediated, and finally how governance information is reported.

Everything demonstrated today is driven from the application registry.

There are no resource-specific rules hardcoded into the Governance Engine.

---

# Step 1 - Application Registry

The first thing I'd like to show is the application registry.

I'll open the following folder.

```
registry/applications
```

Currently the repository contains

```
APP000001.yaml
```

This file represents a single business application.

Instead of storing ownership information inside Terraform or inside application code, everything is defined here.

I'll briefly scroll through the file.

Here we can see information such as

- Product
- Team
- Owner
- Budget Owner
- Department
- Cost Centre
- Environment
- Business Criticality
- Google Cloud Project Binding

This file becomes the single source of truth for governance.

Whenever the Governance Engine evaluates a project, it first reads this registry.

From this metadata it generates the labels that should exist on every supported resource belonging to this application.

One important design decision is that onboarding a new application only requires adding another YAML file.

No Python code changes.

No infrastructure changes.

No database updates.

The platform automatically discovers every application stored inside this folder.

---

# Step 2 - Deployment Pipeline

Next I'd like to briefly show the deployment pipeline.

I'll open GitHub.

The platform follows a GitOps deployment model.

Every change begins with a feature branch.

For example,

```
feature/new-application
```

A platform engineer commits a new registry file.

The code is pushed to GitHub.

GitHub Actions immediately validates the registry.

Validation checks include

- YAML syntax

- JSON schema validation

- Mandatory fields

- Project bindings

If validation fails, the Pull Request cannot be merged.

If validation succeeds, the Pull Request requires approval before merging into the main branch.

Only after approval does deployment occur.

This provides governance before governance.

---

# Step 3 - Terraform Infrastructure

Now let's look at the infrastructure.

The platform infrastructure is entirely deployed using Terraform.

Terraform provisions

- Service Accounts

- IAM

- Artifact Registry

- Workload Identity Federation

- Cloud Run

Every environment is therefore reproducible.

There are no manual deployment steps once the project has been configured.

---

# Step 4 - Cloud Run

Now let's move to the running platform.

I'll open the Cloud Run service.

This is the Governance Engine.

The Governance Engine exposes a small REST API.

Each endpoint performs one clearly defined responsibility.

```
/health

/discover

/compliance

/verify

/enforce

/report
```

We'll now walk through each endpoint.

---

# Step 5 - Health Endpoint

I'll begin with

```
GET /health
```

The purpose of this endpoint is simply to verify that the platform is operational.

It confirms that Cloud Run is healthy and that the Governance Engine is available.

This endpoint is typically used by monitoring systems or load balancers.

---

# Step 6 - Resource Discovery

Next I'll call

```
GET /discover
```

This endpoint performs resource discovery using Cloud Asset Inventory.

Rather than calling each Google Cloud service individually, Cloud Asset Inventory provides a single inventory of supported resources across the project.

For this demonstration we can see that the platform has discovered approximately

```
176 resources
```

Examples include

- Compute Engine

- BigQuery

- Storage

- Artifact Registry

and many other Google Cloud services.

At this stage the platform has simply built an inventory.

No governance decisions have been made yet.

---

# Step 7 - Compliance Evaluation

Next I'll call

```
GET /compliance
```

This is where governance begins.

The Compliance Engine performs three activities.

First,

it retrieves the expected metadata from the registry.

Second,

it compares every supported resource against those expected values.

Finally,

it generates a compliance result.

For every supported resource we determine

- Is the resource compliant?

- Which labels are missing?

- Which labels are incorrect?

Notice that unsupported resources are automatically excluded through the Capability Service.

This avoids unnecessary API calls.

The output also contains a compliance summary.

This allows platform teams to understand the current compliance position without manually inspecting hundreds of resources.

---

# Step 8 - Governance Report

Now I'll open

```
GET /report
```

This endpoint aggregates governance information into a management summary.

Instead of reviewing individual resources, management can immediately see

Total resources

Supported resources

Compliant resources

Non-compliant resources

Potential remediation candidates

Compliance percentage

This information could easily be integrated into dashboards such as Looker Studio or Grafana.

---

# Step 9 - Demonstrating Non-Compliant Resources

For this demonstration I have deliberately created resources that are missing metadata.

Examples include

A Compute Engine Virtual Machine

A BigQuery Dataset

These resources were created without the mandatory governance labels.

The Compliance Engine correctly identifies them as non-compliant.

No manual inspection was required.

---

# Step 10 - Metadata Enforcement

Now I'll demonstrate remediation.

I'll call

```
GET /enforce
```

The Enforcement Engine performs several activities.

First,

it reviews the compliance results.

Second,

it creates an execution plan.

Third,

the Executor Service processes each remediation action.

Finally,

the Adapter Layer selects the correct Google Cloud client.

For example

Compute Engine resources use the Compute Adapter.

BigQuery Datasets use the BigQuery Adapter.

One important architectural decision here is that the Enforcement Engine does not know how Google Cloud APIs work.

It simply requests

"Apply these labels."

The Adapter handles the implementation details.

This keeps the Governance Engine completely independent from resource-specific APIs.

---

# Step 11 - Metadata Verification

After remediation completes, I'll call

```
GET /verify
```

The Verification Service rediscoveries the resources and confirms that expected metadata now exists.

Verification provides confidence that remediation completed successfully.

This is particularly valuable when automation is introduced because it confirms that platform actions produced the expected result.

---

# Step 12 - Logging

Next I'd like to briefly show Cloud Logging.

Every major service emits structured operational logs.

Examples include

Resource discovery

Compliance evaluation

Registry loading

Enforcement execution

Verification

Reporting

Because the platform runs on Cloud Run, logs automatically appear inside Cloud Logging.

This provides operational visibility without implementing custom logging infrastructure.

---

# Step 13 - Security

The deployment pipeline also follows modern security practices.

GitHub authenticates using Workload Identity Federation.

No service account keys are stored anywhere inside GitHub.

Service Accounts follow least privilege.

Every deployment is traceable through GitHub Actions.

Registry updates require Pull Request approval.

This significantly reduces operational risk.

---

# Step 14 - Demonstrating Extensibility

One of the strengths of this architecture is that it has been designed to evolve.

Today the platform demonstrates automated metadata enforcement for

- Compute Engine

- BigQuery Datasets

Supporting another Google Cloud service does not require redesigning the Governance Engine.

We simply implement another adapter.

Everything else remains unchanged.

This keeps future development predictable and maintainable.

---

# Step 15 - Live Demonstration Summary

To summarise what we've just seen

We started with a centrally managed application registry.

The platform discovered Google Cloud resources.

Those resources were evaluated against business metadata.

Non-compliant resources were identified.

Supported resources were automatically remediated.

Verification confirmed successful remediation.

Finally, governance reporting provided an operational summary.

This entire workflow is registry-driven.

No business rules are embedded into infrastructure code.

No application-specific logic is hardcoded into the Governance Engine.

The platform has been designed to scale by adding new registry files and additional Google Cloud resource adapters rather than redesigning the application itself.

---

# Transition

That completes the live demonstration.

For the final section I'd like to briefly discuss operational considerations, production readiness, future enhancements and answer any technical questions you may have.

# Part 4 - Production Readiness, Future Roadmap & Questions

**Duration:** 10-15 Minutes

---

# Production Readiness

Before concluding the demonstration, I'd like to briefly discuss where the platform currently stands from a production perspective.

This Proof of Concept has been designed as an enterprise-ready foundation rather than simply demonstrating individual Google Cloud APIs.

The objective was to ensure that the platform architecture could scale as organisational governance requirements increase.

Throughout the implementation we focused on maintainability, extensibility, security and operational support.

Although this is a Proof of Concept, many of the engineering practices used are the same practices we would expect within a production platform.

---

# Current Capabilities

Today the platform delivers the following capabilities.

Application onboarding through a governed registry.

Infrastructure deployment using Terraform.

Cloud-native runtime using Cloud Run.

Secure CI/CD using GitHub Actions and Workload Identity Federation.

Enterprise metadata discovery using Cloud Asset Inventory.

Metadata compliance evaluation.

Metadata enforcement for supported resources.

Metadata verification.

Governance reporting.

Operational logging.

Unit testing.

Registry validation.

Pull Request approval workflow.

These capabilities together provide a complete governance lifecycle.

---

# Engineering Decisions

Throughout development several engineering decisions were made intentionally.

One important decision was avoiding hardcoded metadata.

Instead of embedding ownership information inside Python code or Terraform modules, everything is stored inside registry files.

This means business users can update ownership information without changing application logic.

Another important decision was separating business logic into services.

Rather than creating one large application file, each service has a single responsibility.

Discovery.

Governance.

Compliance.

Enforcement.

Verification.

Reporting.

This makes the platform significantly easier to maintain over time.

---

# Security

Security has been an important consideration throughout the implementation.

Authentication between GitHub and Google Cloud uses Workload Identity Federation.

No long-lived credentials exist inside GitHub.

Every deployment uses short-lived OpenID Connect tokens.

Service Accounts follow least privilege.

Registry updates require Pull Request approval.

Infrastructure is fully version controlled.

These decisions reduce operational risk while aligning with Google Cloud security recommendations.

---

# Operational Support

Operationally the platform has been designed so that engineers can understand what happened without manually investigating the application.

Every service emits structured logs.

Examples include

Discovery starting.

Discovery completed.

Compliance evaluation.

Governance loading.

Enforcement execution.

Verification.

Reporting.

Cloud Run automatically forwards these logs into Cloud Logging.

From an operational perspective this means support engineers can troubleshoot platform behaviour directly through Cloud Logging.

---

# Testing Strategy

The platform includes automated testing.

Business services are tested independently.

Examples include

Capability Service.

Governance Service.

Compliance Service.

Executor Service.

Report Service.

Adapter Service.

Google Cloud APIs are mocked during unit testing.

This allows business logic to be tested without requiring live Google Cloud resources.

Testing therefore becomes both faster and more reliable.

---

# CI/CD Process

Every platform change follows the same controlled process.

A feature branch is created.

Changes are committed.

A Pull Request is opened.

Registry validation executes automatically.

Reviewers approve the Pull Request.

The Pull Request is merged into the main branch.

GitHub Actions automatically deploys the latest version of the platform.

This ensures that deployments remain consistent and auditable.

---

# Current Supported Resources

At the moment the platform supports automated metadata enforcement for

Compute Engine Virtual Machines

BigQuery Datasets

The architecture has deliberately been designed so that adding another Google Cloud service only requires implementing another adapter.

Examples could include

Cloud SQL

Cloud Storage

Pub/Sub

Secret Manager

Cloud Functions

GKE

No redesign of the Governance Engine would be required.

---

# Current Limitation

There is one important limitation I'd like to mention.

Currently metadata remediation is initiated through the Enforcement API.

This means an engineer explicitly invokes

```
GET /enforce
```

to remediate non-compliant resources.

The platform already contains the discovery, compliance, execution and verification capabilities required for automatic governance.

The remaining enhancement would be introducing an event-driven trigger.

For example

Cloud Audit Logs

↓

Eventarc

↓

Cloud Run

↓

Governance Engine

↓

Automatic Metadata Enforcement

Once implemented, newly created resources could be remediated automatically without requiring manual API invocation.

The current architecture has already been designed to support this enhancement.

---

# Scalability

One common question is

"How many applications can this platform support?"

Because governance is registry-driven there is no dependency on application-specific code.

Each application simply contributes another registry file.

For example

```
APP000001.yaml

APP000002.yaml

APP000003.yaml

...

APP005000.yaml
```

The Governance Engine automatically discovers every application during execution.

This allows governance to scale naturally as additional applications are onboarded.

---

# Greenfield & Brownfield Support

The platform supports both deployment scenarios.

Greenfield.

Resources deployed into new projects can be governed immediately once they exist.

Brownfield.

Existing Google Cloud resources are discovered through Cloud Asset Inventory.

Compliance is evaluated.

Supported resources can then be remediated without rebuilding infrastructure.

This allows organisations to introduce governance without redeploying existing workloads.

---

# Why Cloud Asset Inventory?

Another common question is why Cloud Asset Inventory was selected.

Cloud Asset Inventory provides a central inventory across Google Cloud services.

Instead of writing custom discovery logic for every individual service, the platform performs discovery through a single Google Cloud API.

This significantly reduces implementation complexity while providing a consistent inventory model.

---

# Future Roadmap

The architecture has been designed with future expansion in mind.

Potential enhancements include

Automatic Eventarc enforcement.

Cloud Scheduler compliance scans.

Cloud Monitoring dashboards.

Compliance alerting.

Support for additional Google Cloud services.

Organisation-level governance.

Multi-project governance.

Historical compliance reporting.

Policy integration.

Because the platform is modular, these enhancements can be introduced incrementally.

---

# Business Benefits

From an operational perspective this platform provides several benefits.

Central ownership of governance metadata.

Reduced manual governance effort.

Consistent metadata across supported resources.

Improved auditability.

Secure deployments.

Infrastructure as Code.

Reduced operational overhead.

Improved visibility into compliance.

Scalable application onboarding.

Extensible architecture.

---

# Summary

To summarise today's demonstration.

We started with a central application registry.

Infrastructure was deployed using Terraform.

Authentication used Workload Identity Federation.

Resources were discovered through Cloud Asset Inventory.

Business metadata was loaded from the registry.

Compliance was evaluated automatically.

Supported resources were remediated.

Verification confirmed successful remediation.

Governance reports provided operational visibility.

Everything demonstrated today has been implemented using cloud-native Google Cloud services together with Infrastructure as Code and secure deployment practices.

The platform has been intentionally designed as a reusable governance foundation that can continue to evolve by adding new registry files and additional Google Cloud resource adapters without redesigning the core architecture.

---

# Closing

That concludes the demonstration.

Thank you for your time.

I'd now be happy to answer any questions about the architecture, implementation, deployment approach or future roadmap.

I appreciate your feedback and look forward to discussing how this platform could evolve to support your governance requirements.

---

# Adapter Layer - Why It Is Critical

One of the most important architectural decisions in this platform is the Adapter Layer.

Google Cloud services do not expose a common API for managing metadata. Compute Engine, BigQuery, Cloud Storage, Cloud SQL and other services all use different APIs and request formats.

The Governance Engine therefore never interacts directly with service-specific APIs. Instead, it delegates all resource-specific operations to adapters.

The Governance Engine decides **what** action is required, while the Adapter decides **how** that action is performed.

Current adapters include:

- Compute Adapter
- BigQuery Adapter

Execution flow:

Compliance Service
↓
Enforcement Service
↓
Adapter Service
↓
Resource-specific Adapter
↓
Google Cloud API

Benefits:

- Separation of business logic from Google Cloud implementation.
- Easy support for new Google Cloud services.
- No changes required in Compliance or Enforcement when adding a new resource type.
- Reduced code duplication.
- Easier unit testing.
- Better maintainability.
- Production-ready extensibility.

For example, supporting Cloud Storage only requires implementing a Storage Adapter and registering it with the Adapter Service. The rest of the Governance Engine remains unchanged.
