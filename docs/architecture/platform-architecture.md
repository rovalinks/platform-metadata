# Metadata Governance Platform Architecture

## Overview

The Metadata Governance Platform is built using Google Cloud native services and Infrastructure as Code.

## Core Components

* GitHub
* GitHub Actions
* Workload Identity Federation
* Cloud Build
* Artifact Registry
* Cloud Run
* Cloud Asset Inventory
* Eventarc

## Runtime Flow

Customer Registry

↓

Validation

↓

Cloud Run Governance Engine

↓

Cloud Asset Inventory

↓

Compliance Evaluation

↓

Report Generation

## Deployment Flow

Git Push

↓

GitHub Actions

↓

OIDC Authentication

↓

Cloud Build

↓

Artifact Registry

↓

Cloud Run
