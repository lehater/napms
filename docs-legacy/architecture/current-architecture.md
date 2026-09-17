# Current as-built architecture

Status: `current implemented architecture and compatibility contract`.

## Role

This document describes the architecture that must be reproduced to rebuild the **current implemented NAPMS product**. It is intentionally distinct from the current target Strategic/Tactical model under `docs/domain/`.

When as-built and target differ:

- this document is authoritative for reconstructing the implemented architecture and compatibility boundaries;
- current `docs/domain/`, target requirements and target architecture are authoritative for intended semantic ownership;
- implementation compatibility must not be mistaken for target domain truth.

## Architecture drivers

Priority order:

1. semantic correctness of authoritative domain state, including idempotency/concurrency invariants;
2. coherent logical-time reads and fail-closed handling;
3. end-to-end provenance/explainability;
4. explicit semantic ownership and action-scoped authority;
5. simplest reversible topology consistent with the supported local product.

No accepted workload/SLA requires service-per-context distribution or multi-node runtime topology.

## Structural style

NAPMS is a modular application with explicit semantic modules and ports/adapters:

```text
Domain
  <- Application / consuming ports
      <- Infrastructure / Presentation / Workflows
          <- Platform / composition root
```

Rules:

- Domain depends only on language/runtime primitives and its own semantic code;
- Application depends inward on Domain and consumer-owned ports;
- infrastructure translates persistence and external-source/provider mechanics;
- presentation translates HTTP/CLI/UI transport;
- cross-context workflows orchestrate public owner contracts without owning peer business truth;
- platform/bootstrap wires executable processes without becoming a semantic owner;
- framework/database/transport/config/logging/DI-container types do not enter Domain;
- constructor injection is the default; no service locator/global mutable dependency registry.

Physical package rules are defined by `docs/architecture/code-structure.md` and ADR-014.

## As-built semantic modules and compatibility modules

Implemented authoritative modules include:

- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- Technical Access Evidence;
- Network Enforcement Placement;
- Network Environment Operations where explicitly composed.

The current implementation also contains compatibility-era semantic modules/workflows that remain required to reproduce existing behavior, including Connectivity Requirements, Connectivity Decision, Requirement-to-Policy Alignment, policy export/snapshot normalization, Scoped Connectivity Inventory and Traffic Analysis Checker.

Those compatibility modules are documented because they exist in the current designed system. They are **not** evidence that Connectivity Requirements/Connectivity Decision remain target Bounded Contexts; current target ownership is defined by `docs/domain/strategic-model.md` and `docs/domain/context-map.md`.

The current APR runtime may likewise contain behavior from an older realization design. Its as-built presence is reconstructable implementation truth; current APR target semantics are owned by the target APR requirement/domain/architecture documents.

## Persistence ownership

PostgreSQL is the authoritative local persistence engine for persisted product state.

Each semantic module owns its repository/schema contract. Physical database colocation does not transfer semantic ownership. Cross-module direct table reads/writes are prohibited when they bypass the owning module's accepted application/persistence contract.

Cross-context read composition may combine owner-published projections at an explicit logical time. Coherent snapshot requirements are documented by the relevant workflow/ADR; they are not inferred merely because data shares one database server.

## Current runtime topology

Supported local topology:

```text
browser
  -> loopback-published nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

Only the Web/nginx edge is host-published in the supported Compose topology. API and PostgreSQL remain internal.

Local username/password authentication with server-side sessions is the primary authentication path. No external IdP, directory, CMDB, catalogue provider or MSSQL dependency is required for normal operation.

PostgreSQL host access uses password authentication; fresh supported volumes use SCRAM-SHA-256. Startup credential preparation/rotation, health/readiness probes, migrations, backup/restore and container hardening are outer operational concerns documented under `docs/engineering/`.

## Authority and trust boundaries

Authenticated actor identity originates from the server/session boundary, never from trusted interpretation of request payload fields.

Application use cases evaluate action-specific Authority Management admission. Read authority and mutation authority remain independent. Unknown or ambiguous required authority fails closed.

Authentication identity, Resource responsibility/contact facts, Resource Scope Affiliation, Application owner metadata, Company/Environment metadata and catalogue visibility do not themselves grant business authority.

Catalogue mutation uses server-selected administrative authority contexts:

```text
ACC -> CurateApplicationCatalogue @ application-catalogue
RC  -> CurateResourceCatalogue    @ resource-catalogue
```

The caller cannot substitute a Responsibility Scope to widen those permissions.

## Application Communication Catalogue — implemented authoring model

As-built ACC semantics are specified by:

- `docs/domain/application-communication-catalogue/tactical-model.md`;
- `docs/requirements/application-catalogue-target.md`;
- `docs/architecture/application-catalogue-target-boundary.md`;
- ADR-012 and ADR-013;
- `docs/engineering/application-catalogue-target-http-contract.md`.

The implemented authoring structure is:

```text
Application Definition
  -> Component
  -> Interaction Definition

Application Deployment
  -> Application Definition
  -> Company / Environment / Scope context
  -> selected Deployment Interaction
      -> Source Resource set
      -> Destination Resource set
      -> internal compatibility projection
```

Application Definition reuses stable Application identity. Application Deployment and Deployment Interaction are first-class as-built identities. Company, Environment and Scope are correlation/context values, not identity or authority.

Interaction Definition owns reusable vendor-neutral traffic intent. Deployment Interaction selects one Interaction Definition without deployment-specific traffic override. Resource membership is scoped to one Deployment Interaction side.

### Downstream compatibility projection

Existing downstream modules consume the compatibility identity:

```text
sourceComponentDeploymentId
+ destinationComponentDeploymentId
+ dcsContractRevisionId
```

Each Active Deployment Interaction therefore owns stable internal compatibility Component Deployment identities for Source and Destination plus a current immutable DCS revision.

These compatibility IDs are backend implementation identities and are not normal authoring concepts in the current Applications UI/API.

A permitted Interaction Definition traffic edit creates replacement immutable DCS snapshots for affected Active Deployment Interactions while preserving previous DCS revisions and downstream references. Existing dependency contracts can block unsafe edits/retirements.

### Resource binding and reads

Authoring addresses membership by:

```text
deploymentInteractionId + side + resourceReference
```

ACC validates Resource references through RC-owned contracts. Deployment Resource-set read models may combine ACC membership with RC display/scope facts at one explicit `asOf`; this query composition transfers no mutation/lifecycle ownership.

### Lifecycle

Application Definition, Component, Interaction Definition, Application Deployment and Deployment Interaction use terminal `Active -> Retired` lifecycle in the implemented catalogue model. Retirement is non-cascading and dependency-blocked; normal hard delete is absent.

Pre-current Component Deployment/DCS/Deployment Resource Binding facts that are still referenced remain compatibility truth. They are not silently fabricated into the newer authoring model where required business context cannot be inferred.

## Resource Catalogue — implemented boundary

Resource Catalogue owns stable Resource identity plus the temporal facts used by the implemented product:

```text
Resource
  -> Endpoint / technical realization history
  -> Resource Scope Affiliation
  -> Resource Responsibility / contact
```

Resource responsibility/contact and scope affiliation are independent of mutation authority.

The newer target RC model may describe realization with `AddressSpace`; the as-built Endpoint/realization representation remains documented where needed to reproduce current persistence/API/UI behavior.

## Access Policy and Authority Management

Access Policy owns authoritative Access Rule/Policy Rule persistence and effective-policy selection for the implemented workflows.

Authority Management owns actor/action/scope admission. Catalogue, Decision, Requirement, policy-view and network-operation use cases consume Authority through explicit ports rather than inferring permission from UI state or ownership metadata.

Current target AP/AM semantics are documented in their Tactical models; as-built transport and persistence behavior is documented in engineering/API contracts.

## Technical Access Evidence

TAE owns immutable source-qualified technical evidence. Source-specific parsing/import/collection remains outside its Domain.

TAE evidence is not authorization, desired policy or realization truth. Configured data shown by Checker is stored evidence; Checker does not synchronously read a device and promote the result to business authorization.

As-built TAE behavior is defined by its requirements, Tactical model, architecture boundary and executable persistence/import contracts.

## Network Enforcement Placement / Network Context

The implemented NEP/Network Context surface provides candidate Firewall/policy-locator relevance and related routing/context evidence according to its as-built Tactical/architecture contracts.

Candidate relevance is not proof of authorization or final end-to-end policy realization. Current target NEP semantics are separately documented by `target-tactical-model.md` and current target requirements.

## Access Policy Realization compatibility boundary

Existing APR/Realization runtime code may still exist as part of the current implementation. It must be reconstructable where product/runtime contracts still depend on it, but it is not the source of current target APR meaning.

Target APR semantics are:

```text
TargetRequiredPolicy
        +
ConfiguredEffectivePolicySnapshot
        |
        v
RealizationAssessment
  -> SemanticDelta
  -> verified additive change intent
  -> provider rendering
  -> Network Environment Operations
```

Target selection is upstream; APR compares effective access semantics rather than raw rule identity. Rendering cannot broaden/narrow verified intent. Transport/apply acknowledgement is not proof of final realization.

## Network Environment Operations

NEO is downstream of verified/rendered target policy intent and owns controlled mutation identity, mutation authority, preconditions/concurrency, apply outcome and post-check verification semantics.

Conceptually:

```text
TargetPolicyArtifact
  -> mutation authority
  -> acquire operation-scoped current target state
  -> precondition/concurrency check
  -> conditional apply
  -> post-state verification
  -> Verified | PreconditionFailed | Rejected | Drift | Unknown
```

Provider transport remains an outer adapter. Unknown apply outcome is not blindly retried.

## As-built read/application compositions

### Scoped Connectivity Inventory

Provides the resource-centric connectivity workspace by composing RC, ACC and current governance/policy compatibility contracts without creating a new authoritative aggregate. One explicit `asOf` is used where the contract requires coherent temporal interpretation.

### Traffic Analysis Checker

Combines Resource attribution, ACC/application context, scoped connectivity summaries, Network Context/NEP information, stored TAE evidence and Resource responsibility/contact under explicit owner contracts.

Configured evidence never implies `Allowed`.

### Policy export

Produces the implemented coherent logical-as-of normalized vendor-neutral desired-policy export using the accepted snapshot/normalization contracts. It is an as-built product capability distinct from the newly selected pre-authorization Required Access Matrix MVP.

## HTTP and application boundary

FastAPI is an outer transport adapter. Public transport semantics are specified in:

- `docs/engineering/http-api-contract.md`;
- `docs/engineering/catalogue-curation-http-api-contract.md`;
- `docs/engineering/application-catalogue-target-http-contract.md`;
- `docs/engineering/error-model.md`.

Domain/Application do not import FastAPI/Pydantic types.

Session actor, runtime command time and server-selected authority scope are trusted server values. Client payloads do not manufacture them.

## UI architecture

React is an outer adapter. The current implemented screen model and wireframes are retained under `docs/ui/`; generic visual ownership and component-composition rules are defined by the design-system documents.

Product semantics remain backend/domain owned. Frontend state, navigation visibility or disabled controls never establish business authority.

## Security and integrity guardrails

The as-built architecture must preserve:

- authoritative identity uniqueness/idempotency where specified;
- exact subject correlation across compatibility Requirement/Decision/Rule flows;
- module-owned persistence boundaries;
- explicit logical-time validity where required;
- no caller-selected trusted actor/time/catalogue authority scope;
- catalogue visibility/responsibility/scope affiliation distinct from mutation authority;
- stable Application/Component identities and immutable historical DCS/downstream references;
- compatibility IDs remaining internal where the public target model does not expose them;
- no destructive catalogue maintenance that erases referenced historical truth;
- no silent semantic broadening/narrowing in normalization, comparison or rendering;
- no false `Verified` result from transport acceptance alone;
- explicit degraded/unknown outcomes instead of convenient success;
- no PostgreSQL network trust in the supported local path;
- startup/status probes that do not mutate business state;
- Web dependency lockfile consistency.

## Current target relation

The accepted target model contains the 11 Bounded Contexts documented by `docs/domain/strategic-model.md`. In particular, target Business Connectivity, Access Governance and Application Deployment ownership must not be inferred from as-built compatibility modules such as Connectivity Requirements, Connectivity Decision or ACC compatibility Component Deployments.

The selected next implementation vertical is narrower still:

```text
ACC + AD + RC
    -> Required Access Matrix
    -> table / vendor-neutral export
```

Its S3 architecture is not yet accepted. Nothing in this as-built document pre-decides that new workflow's package/API/consistency/UI design.

## Reconstruction references

Use together:

- `docs/engineering/current-state.md` — implemented capability/runtime inventory;
- `docs/engineering/README.md` — as-built engineering contract map;
- `docs/requirements/README.md` — target and as-built behavior map;
- `docs/domain/strategic-model.md` and `context-map.md` — current target semantic ownership;
- as-built ACC/NEP Tactical models plus target Tactical models where both are retained;
- `docs/decisions/README.md` — current retained architectural decisions;
- `docs/ui/README.md` — as-built UI specs and reusable UI guidance;
- `docs/architecture/code-structure.md` — structural target and dependency taxonomy.
