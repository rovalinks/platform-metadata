# Enterprise Metadata Governance Platform - Application Registry

## 1. Purpose

This document defines the Application Registry design and operating model for the Enterprise Metadata Governance Platform on Google Cloud.

The Application Registry is the central source of truth used by the governance platform to resolve workload projects to application ownership and required governance metadata.

The registry keeps application-specific values outside the Cloud Run governance code and resource adapters.

It is used by both:

- Brownfield governance
- Greenfield governance

The registry must remain environment-aware, schema-validated, auditable and independent from runtime business logic.

---

## 2. Registry Objective

The registry answers a fundamental governance question:

```text
Given this GCP project/resource,
which application does it belong to,
and what governance metadata should it have?
```

The platform should not infer ownership from resource names or embed customer application mappings inside Python code.

Instead:

```text
GCP Resource
     |
     v
Project ID
     |
     v
Application Registry
     |
     v
Application / Ownership / Governance Metadata
```

---

## 3. Registry Role in the Architecture

```text
                        Application Registry
                               |
              +----------------+----------------+
              |                                 |
              v                                 v
         Brownfield                         Greenfield
              |                                 |
       CAI Discovery                      Audit Event
              |                                 |
              +---------------+-----------------+
                              |
                              v
                       Project Resolution
                              |
                              v
                       Registry Binding
                              |
                              v
                     Required Metadata
                              |
                              v
                     Compliance Engine
                              |
                              v
                     Resource Adapter
```

Brownfield and Greenfield must resolve metadata from the same registry model.

---

## 4. Storage Architecture

The registry is stored in Google Cloud Storage.

The deployed development bucket is:

```text
rouse-platform-metadata-registry-dev
```

The production environment must use its own production registry storage associated with:

```text
platform-metadata-prod
```

DEV and PROD registry content must not share the same runtime storage dependency.

---

## 5. Cloud Storage Controls

The registry bucket is configured with:

```text
uniform_bucket_level_access = true
force_destroy = false
```

Uniform bucket-level access keeps access management IAM-based rather than relying on per-object ACLs.

`force_destroy = false` protects registry content from automatic destructive bucket removal through normal Terraform destruction.

---

## 6. Registry Format

The registry uses YAML definitions.

YAML provides a human-readable representation suitable for:

- source control
- peer review
- schema validation
- CI validation
- environment promotion
- application onboarding

Application records should remain declarative.

They should describe governance metadata rather than application execution logic.

---

## 7. Registry Data Model

The exact schema is controlled by the repository's registry validation implementation.

The registry represents application metadata and GCP bindings.

Typical application-level metadata includes:

```text
product
team
owner
budget_owner
organisation
department
cost_centre
```

Typical GCP binding information includes:

```text
project_id
environment
region
business_criticality
```

The authoritative accepted field names and allowed values are the repository schema and validation code.

Documentation examples must not override the actual schema.

---

## 8. Conceptual Registry Example

The following is conceptual only and must be adapted to the repository's actual schema before use:

```yaml
application:
  product: payments
  team: payments-platform
  owner: application-owner
  budget_owner: budget-owner
  organisation: example-org
  department: technology
  cost_centre: cc-example

gcp:
  bindings:
    - project_id: payments-dev-1
      environment: dev
      region: europe-west2
      business_criticality: high
```

Do not copy a documentation example into production unless it passes the repository's actual registry validation.

---

## 9. Project-to-Application Binding

Project binding is central to the governance model.

A workload project should resolve deterministically to its registered application.

Conceptually:

```text
payments-dev-1
      |
      v
Registry Lookup
      |
      v
Payments Application
      |
      v
Required Governance Metadata
```

The platform must not guess the application based on:

- project-name prefixes
- resource names
- labels already present
- folder names
- free-form naming assumptions

unless such behaviour is explicitly part of the approved registry design.

---

## 10. Unique Project Binding

A project should not ambiguously map to multiple applications.

Registry validation should reject duplicate or conflicting project bindings.

For example, this must not be allowed:

```text
Application A -> payments-dev-1
Application B -> payments-dev-1
```

because the governance engine would not have an authoritative application owner.

Unique project binding is therefore a precondition for deterministic remediation.

---

## 11. Environment Values

Environment values must follow the values allowed by the repository schema.

Do not introduce alternative names such as:

```text
development
production
```

if the schema expects values such as:

```text
dev
prod
test
uat
```

The validation pipeline is authoritative.

Invalid environment values must fail registry validation before deployment.

---

## 12. Registry Validation

Registry changes must be validated before promotion.

Validation should cover:

```text
[ ] YAML syntax
[ ] Schema compliance
[ ] Required fields
[ ] Allowed enum values
[ ] Project binding uniqueness
[ ] Required GCP binding fields
[ ] File structure
[ ] Data types
[ ] Any repository-specific business rules
```

Invalid registry content must not be promoted into the runtime bucket.

---

## 13. CI Validation

Registry validation should execute automatically in CI when registry files change.

The intended flow is:

```text
Registry Change
      |
      v
Pull Request
      |
      v
Validation Workflow
      |
      +-- YAML parse
      +-- schema validation
      +-- business-rule validation
      +-- duplicate binding validation
      |
      v
Pass / Fail
```

A failed validation must block promotion until corrected.

---

## 14. Registry Promotion

Registry content should be promoted independently from application container releases.

Recommended process:

```text
1. Update registry YAML
2. Run local validation
3. Commit change
4. Open pull request
5. CI validation
6. Peer/application-owner review
7. Merge approved change
8. Publish to DEV registry
9. Validate DEV runtime resolution
10. Review expected governance impact
11. Approve production promotion
12. Publish to PROD registry
13. Validate production registry load
```

This allows metadata ownership changes without rebuilding the Cloud Run application.

---

## 15. Runtime Registry Reader

The Cloud Run application contains a registry-reading layer.

The registry reader is responsible for:

- locating registry objects
- reading YAML
- parsing definitions
- building project/application mappings
- supplying required metadata to governance processing

Resource adapters should not independently read YAML files.

Registry access should remain centralised.

---

## 16. Runtime Cache

The application uses registry caching to avoid reading and parsing the registry for every resource operation.

The application includes a configurable cache control:

```text
REGISTRY_CACHE_TTL
```

The value should come from runtime configuration.

It must not be duplicated as an unrelated hardcoded value across handlers.

---

## 17. Cache Behaviour

The conceptual runtime behaviour is:

```text
Governance Request
      |
      v
Registry Cache Valid?
      |
   +--+--+
   |     |
  Yes    No
   |     |
   v     v
Use     Read GCS
Cache      |
           v
        Parse Registry
           |
           v
        Refresh Cache
```

Caching reduces:

- Cloud Storage reads
- YAML parsing
- request latency

while still allowing registry changes to become visible after the configured cache period.

---

## 18. Cache Consistency

Registry caching means a newly published registry change may not become visible to every warm Cloud Run instance instantaneously.

Operational procedures must account for the configured TTL.

Do not assume:

```text
Registry object uploaded
=
Every active instance immediately refreshed
```

Where immediate validation is required, use the application's supported cache refresh/restart behaviour rather than introducing undocumented runtime hacks.

---

## 19. Brownfield Registry Usage

During Brownfield processing:

```text
Discovered Resource
      |
      v
Project ID
      |
      v
Registry Lookup
      |
      +-- Binding exists -> evaluate resource
      |
      +-- No binding -> follow unbound-project policy
```

The registry determines the metadata expected for the resource.

A Brownfield run should not invent missing ownership values.

---

## 20. Greenfield Registry Usage

During Greenfield processing:

```text
Creation Event
      |
      v
Classifier
      |
      v
Project ID
      |
      v
Registry Lookup
      |
      v
Required Metadata
      |
      v
Compliance / Remediation
```

This ensures newly created resources receive the same metadata standard as existing Brownfield resources.

---

## 21. Unbound Projects

A workload project may exist in the organisation without a valid registry binding.

The platform must handle this explicitly.

Possible operational behaviour includes:

- skip remediation
- log the unbound project
- report it through governance reporting
- require registry onboarding

The platform must not guess ownership or apply another application's metadata.

---

## 22. Registry as Governance Control

The registry is more than a lookup file.

A registry change can alter the required metadata for many resources.

For example, changing an application's:

```text
owner
cost_centre
department
team
```

can cause existing resources to become non-compliant on the next Brownfield evaluation.

Registry changes therefore require governance review appropriate to their impact.

---

## 23. Registry and Brownfield Impact

Before promoting a large production registry change, assess:

```text
How many projects are affected?
How many resources may become non-compliant?
Which managed keys change?
Will Brownfield remediation update existing resources?
Is the change intentional?
```

Registry promotion and organisation-wide Brownfield execution should not be treated as unrelated operational activities.

---

## 24. Registry and Greenfield Impact

Greenfield processing uses the current registry view available to the runtime.

After a registry change becomes visible to the application cache, newly processed resource events will use the updated required metadata.

This makes registry release management important for near-real-time governance behaviour.

---

## 25. Managed Metadata

The registry defines values used by the governance engine for managed metadata.

The compliance engine determines which keys are governed.

The registry should not be treated as an instruction to replace every label already present on a resource.

Existing non-managed metadata should be preserved according to platform policy and adapter behaviour.

---

## 26. No Hardcoding

Application-specific values must not be embedded in:

```text
app.py
dispatcher
classifiers
resource adapters
resource clients
dashboard JavaScript
Terraform resource logic
```

when those values belong to the Application Registry.

Examples of values that should remain registry-driven include:

- application ownership
- cost centre
- team
- business criticality
- environment binding
- project-to-application relationship

Environment infrastructure values belong to deployment configuration/Terraform rather than the Application Registry where appropriate.

---

## 27. Registry vs Capability Configuration

The Application Registry and supported-resource capability configuration solve different problems.

### Application Registry

Answers:

```text
Who owns this project/application?
What metadata values are required?
```

### Capability Configuration

Answers:

```text
Can this asset type be discovered?
Can it be evaluated?
Can it be remediated?
Is Brownfield enabled?
Is Greenfield enabled?
```

Do not mix these concerns.

---

## 28. Registry vs Terraform

Terraform provisions registry infrastructure such as the bucket and IAM.

Terraform should not be used as the primary mechanism for embedding every application registry record into infrastructure code unless that becomes an explicit future design decision.

Current separation:

```text
Terraform
    -> Registry infrastructure

Registry process
    -> Registry content
```

This keeps application onboarding independent from infrastructure provisioning.

---

## 29. Registry vs BigQuery

The registry is the source of required application metadata.

BigQuery is the source of operational governance evidence.

Do not use BigQuery compliance snapshots as the authoritative application ownership registry.

Conceptually:

```text
Application Registry
    -> desired governance state

BigQuery
    -> observed governance state and execution history
```

---

## 30. Registry IAM

The runtime requires only the Cloud Storage access necessary to load approved registry content.

Production should follow least privilege.

Logical separation:

```text
Runtime service account
    -> registry read

Registry publisher/deployment process
    -> registry write
```

If DEV currently uses broader permissions for engineering convenience, PROD should review and reduce them where possible.

---

## 31. Registry Security

Production registry controls should include:

```text
[ ] Uniform bucket-level access
[ ] No public access
[ ] Dedicated PROD bucket
[ ] Runtime read access restricted
[ ] Registry write access restricted
[ ] CI validation before promotion
[ ] Change review
[ ] Audit logging
[ ] force_destroy disabled
```

Registry content should not contain credentials, secrets or private keys.

Secrets belong in an approved secrets-management system.

---

## 32. Registry Availability

The runtime cache reduces direct dependency on Cloud Storage for every resource operation.

However, registry availability remains a platform dependency.

If the application has no valid registry data available, it should fail safely rather than applying guessed metadata.

---

## 33. Registry Error Categories

Useful operational categories include:

```text
REGISTRY_OBJECT_NOT_FOUND
REGISTRY_PARSE_ERROR
REGISTRY_SCHEMA_ERROR
DUPLICATE_PROJECT_BINDING
PROJECT_NOT_BOUND
INVALID_ENVIRONMENT
INVALID_REGISTRY_ENTRY
REGISTRY_ACCESS_DENIED
REGISTRY_LOAD_FAILURE
```

The exact implementation terminology may differ.

Logs should provide enough context to identify the affected registry object/project without exposing sensitive information unnecessarily.

---

## 34. Adding a New Application

Recommended onboarding process:

```text
1. Collect approved application ownership metadata
2. Identify GCP project bindings
3. Confirm environment values
4. Create/update YAML
5. Run registry validation
6. Check duplicate project binding
7. Peer/application-owner review
8. Merge approved change
9. Publish to DEV
10. Validate registry resolution
11. Run controlled Brownfield evaluation
12. Test Greenfield if required
13. Approve production promotion
14. Publish to PROD
15. Verify reporting
```

---

## 35. Adding a New Project to an Existing Application

When an application receives a new GCP project:

```text
1. Confirm project ID
2. Confirm application ownership
3. Confirm environment
4. Confirm region/business metadata
5. Add project binding
6. Validate registry
7. Check uniqueness
8. Publish to DEV
9. Validate project resolution
10. Promote to PROD
```

No application code change should be required solely to add a new project binding.

---

## 36. Changing Ownership Metadata

Changes to fields such as:

```text
owner
team
cost_centre
department
budget_owner
```

may affect existing resource compliance.

Before production promotion:

```text
[ ] Confirm change with application owner
[ ] Assess affected projects
[ ] Assess potential Brownfield remediation volume
[ ] Validate in DEV
[ ] Approve production change
```

---

## 37. Removing a Project Binding

Project-binding removal is a governance-sensitive change.

Before removal, determine:

- whether the project still exists
- whether resources remain
- whether Greenfield events may still arrive
- whether Brownfield should continue reporting it
- whether another application will own the project

Do not silently reassign the project to another application without explicit approved registry change.

---

## 38. Renaming an Application

If application identity is represented by file names, keys or IDs in the repository schema, renaming must be handled carefully.

Assess:

- project bindings
- dashboard/reporting references
- historical BigQuery data
- automation
- registry cache behaviour

Historical execution evidence should remain interpretable after the rename.

---

## 39. Registry Validation Failure

When CI reports a validation failure:

1. read the exact validation message
2. identify the affected YAML file
3. correct the schema/value
4. rerun validation
5. do not bypass the validator merely to publish the registry

For example, if an environment value is rejected, use the schema-approved value rather than modifying the validator to accept an unapproved synonym without design review.

---

## 40. Runtime Registry Troubleshooting

If governance processing reports that a project cannot be resolved:

```text
Project ID
   |
   v
Is registry object present?
   |
   v
Does YAML parse?
   |
   v
Does schema validate?
   |
   v
Is project binding present?
   |
   v
Is binding unique?
   |
   v
Has runtime cache refreshed?
   |
   v
Does runtime SA have bucket read access?
```

This sequence separates data problems from IAM/cache problems.

---

## 41. Registry Observability

Operational monitoring should identify:

- registry load success/failure
- cache refresh failures
- parse errors
- unbound projects
- duplicate binding validation failures
- registry access denied
- invalid application records

Registry errors should be visible before large Brownfield executions.

---

## 42. DEV/PROD Promotion Model

```text
Source-Controlled Registry
          |
          v
       Validation
          |
          v
platform-metadata-dev Registry
          |
          v
 DEV Governance Validation
          |
          v
       Approval
          |
          v
platform-metadata-prod Registry
```

Production should receive only registry definitions that passed the same schema and business-rule validation used in DEV.

---

## 43. Versioning and Auditability

Registry changes should be traceable to source control.

For every production change, it should be possible to identify:

- commit
- changed application
- changed project binding
- changed metadata
- approver
- deployment/promotion time

This is preferable to direct unmanaged editing of production bucket objects.

---

## 44. Backup and Recovery

The production registry is a critical governance configuration source.

Recovery planning should include:

- source-controlled copy of approved registry definitions
- ability to republish a known-good version
- Cloud Storage protection appropriate to client requirements
- documented rollback procedure

A registry rollback must consider the compliance impact of reverting metadata values.

---

## 45. Registry Rollback

If a registry release is incorrect:

```text
1. Stop/avoid broad remediation where necessary
2. Identify last known-good registry commit
3. Revalidate the known-good registry
4. Republish to the affected environment
5. Account for runtime cache TTL
6. Verify project resolution
7. Assess resources changed under the incorrect version
8. Run controlled reconciliation if required
9. Record incident/change evidence
```

Simply restoring YAML does not automatically reverse resource changes already applied.

Brownfield reconciliation may be required.

---

## 46. Application Registry Anti-Patterns

Do not:

- hardcode application metadata in Python
- infer ownership from resource-name patterns without approved design
- permit duplicate project bindings
- bypass schema validation
- publish directly to PROD without validation
- use unsupported environment aliases
- store secrets in registry YAML
- share DEV and PROD registry buckets
- allow broad anonymous/public bucket access
- use stale repository snapshots as runtime registry data
- use BigQuery compliance tables as the ownership source of truth
- replace the registry with scattered environment variables
- manually edit PROD objects without source-control reconciliation

---

## 47. Registry Acceptance Checklist

### Schema

```text
[ ] YAML syntax valid
[ ] Schema validation passes
[ ] Required fields present
[ ] Allowed environment values used
[ ] Data types valid
```

### Binding

```text
[ ] Project IDs correct
[ ] Project binding unique
[ ] Application ownership approved
[ ] Environment correct
[ ] Required business metadata present
```

### DEV

```text
[ ] Registry published to DEV
[ ] Runtime can read registry
[ ] Cache loads successfully
[ ] Project resolves correctly
[ ] Brownfield evaluation uses expected metadata
[ ] Greenfield evaluation uses expected metadata
```

### PROD

```text
[ ] Change approved
[ ] Expected remediation impact reviewed
[ ] Registry published to PROD
[ ] PROD runtime loads registry
[ ] No duplicate/unbound regression
[ ] Reporting reflects expected application mapping
```

---

## 48. Architecture Summary

The Application Registry is the central metadata source of truth for the Enterprise Metadata Governance Platform.

Its core responsibility is:

```text
Project
   |
   v
Application Binding
   |
   v
Required Governance Metadata
```

The registry is:

- YAML-based
- stored in Cloud Storage
- schema-validated
- source-controlled
- cached by the runtime
- shared by Brownfield and Greenfield governance
- separated from resource capability configuration
- separated from BigQuery operational evidence
- promoted independently from application container releases

This design allows applications and projects to be onboarded without modifying resource-adapter code and prevents application ownership metadata from becoming hardcoded throughout the platform.

---

## 49. Related Documentation

```text
docs/
├── ARCHITECTURE.md
├── DEPLOYMENT.md
├── IAM.md
├── GREENFIELD.md
├── BROWNFIELD.md
├── APPLICATION_REGISTRY.md
├── SUPPORTED_RESOURCES.md
├── API.md
├── DATA_MODEL.md
├── OPERATIONS.md
├── SECURITY.md
├── TESTING.md
└── PRODUCTION_READINESS.md
```

See:

- `ARCHITECTURE.md` for the overall governance architecture.
- `BROWNFIELD.md` for registry use during existing-resource evaluation.
- `GREENFIELD.md` for registry use during event-driven processing.
- `IAM.md` for registry access controls.
- `SUPPORTED_RESOURCES.md` for the capability model that determines which resources may be governed.
