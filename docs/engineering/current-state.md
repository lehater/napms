# Current implementation state

Status: `I27 Catalogue Curation accepted and implemented for the supported local target`.

Date: 2026-09-10.

Current execution pointer: `docs/plans/active/README.md`; no active implementation plan remains after I27 absorption.

This file is a capability snapshot, not an increment-by-increment changelog. Detailed history lives in Git; roadmap status lives in the corresponding engineering roadmaps.

## Capability snapshot

| Capability | Semantic state | Runtime / persistence | Human-facing surface |
| --- | --- | --- | --- |
| Access Policy | accepted | PostgreSQL-backed Domain/Application implementation with materialization, Active/Inactive, EffectiveWindow and effective-policy selection | Access Rules, Rule Details, Effective Desired Policy |
| Authority Management | accepted through I27 | PostgreSQL-backed scoped action admission including separate catalogue curation actions | consumed by authenticated use cases; no generic IAM admin surface |
| Application Communication Catalogue | accepted through I27 | PostgreSQL-backed first-class Application -> Component -> Component Deployment hierarchy; immutable DCS semantics; temporal Deployment Resource Binding; curation command/idempotency/provenance support | Applications catalogue workspace plus label-first discovery/presentation across product flows |
| Resource Catalogue | accepted through I27 | PostgreSQL-backed Resource lifecycle, Endpoint/realization history, Resource Scope Affiliation, Resource Responsibility/contact, reverse address resolution and curation read/write seams | Resources catalogue workspace, Connectivity and Checker ownership/domain resolution |
| Connectivity Requirements | accepted | PostgreSQL-backed declaration/read/change/retire lifecycle | Needs plus coarse Need state in Connectivity; summarized in Checker policy matches |
| Requirement-to-Policy Alignment | accepted application composition | no independent aggregate/table; derives coverage from authoritative Requirements + Access Policy | Needs and coarse coverage in Connectivity |
| Connectivity Decision | accepted first-class bounded context | PostgreSQL-backed immutable final Decision runtime with exact subject/scope/time selection, supersession and fail-closed persistence semantics | Decisions workspace plus coarse Decision state in Connectivity and Checker |
| Policy export / normalization | accepted | coherent snapshot + vendor-neutral normalized policy JSON | Normalized Policy |
| Scoped Connectivity Inventory | accepted owner-preserving application composition | framework-free read composition with module-owned PostgreSQL adapters; no independent persistence | primary Connectivity workspace and policy/governance input to Checker |
| Technical Access Evidence | accepted through I26 | Domain/Application/Ports + TAE-owned PostgreSQL + strict local JSON import adapter; shared backend technical-predicate matching | consumed by Realization and Checker |
| Network Enforcement Placement | accepted through I26 | proven ForwardingPath remains optional stronger capability; baseline Network Context candidate-set contract is unordered, provenance-bearing and may be incomplete/false-positive | consumed by Realization and Checker Network Context |
| Access Policy Realization | accepted through I21 | owner-preserving AP/RC/ACC/NEP/TAE composition; derived on demand; Cisco ASA renderer outer adapter | Realization read-only operator workspace |
| Network Environment Operations | accepted I22 stub-first Tactical DDD | deterministic in-process target stub + in-memory operation repository; no real Cisco transport or crash-durable audit claim | operation stage in Realization when actual result exists |
| Network Operator Realization View | accepted I25 read composition | authority-first PostgreSQL owner-preserving composition + authenticated HTTP router | Realization workspace with explicit stage availability and Rule navigation |
| Traffic Analysis Checker | accepted I26 read composition | no independent persistence; RC reverse resolution + ACC bindings + Scoped Connectivity summaries + Network Context + stored TAE + Resource Responsibility | Checker workspace |
| Catalogue Curation | accepted I27 product capability | owner-specific RC/ACC application commands, PostgreSQL UoWs, authenticated task-oriented HTTP API, optimistic concurrency and durable idempotency receipts | `CATALOGUES -> Applications / Resources` |
| End-to-end product acceptance | accepted through I27 evidence | I25 Requirement-to-Verified chain plus I27 fresh-catalogue-to-Connectivity/Need journey | explainability and self-service onboarding paths |
| Optional external identity/source extension | accepted I23 dormant seam | source-neutral verified external identity mapping proof; no primary runtime wiring | none |
| Local deployment and operations | accepted I24/I25 local target | password/SCRAM PostgreSQL, repeatable non-mutating startup, logical backup/clean restore, migrations, diagnostics, container hardening and locked Web dependency graph | Make targets, operator runbook and Web UI |

## Current runtime boundary

Supported local topology remains:

```text
browser
  -> loopback-published nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

Local username/password authentication with server-side sessions remains primary. PostgreSQL is the authoritative local persistence. No external IdP, directory, CMDB, application registry, catalogue source, MSSQL dependency or real network lab is required for normal supported operation.

The Compose path keeps PostgreSQL internal and password-authenticated with SCRAM-SHA-256 on fresh volumes. Startup is non-mutating apart from explicit credential preparation/rotation; logical backup/clean restore and forward migrations remain the supported recovery/upgrade mechanisms.

## I27 Catalogue Curation boundary

I27 closes the earlier product gap where RC/ACC truth was consumed by Connectivity but normal users could create it only through seed/direct persistence mechanisms.

The supported self-service path is now:

```text
Resources workspace
  -> create Resource
  -> create/replace technical realization
  -> add/end Resource Scope Affiliation
  -> add/end Resource Responsibility/contact

Applications workspace
  -> create Application
  -> create Component
  -> create Component Deployment
  -> bind/unbind Deployment to existing Resource
  -> author immutable DCS through backend participant discovery

fresh catalogue truth
  -> Scoped Connectivity
  -> existing Connectivity Requirement / Need flow
```

### Semantic ownership

Resource Catalogue owns:
- stable Resource identity and Active/Retired lifecycle;
- Resource Endpoint/realization history;
- temporal Resource Scope Affiliation;
- temporal Resource Responsibility/contact.

Application Communication Catalogue owns:
- Application, Component and Component Deployment identities/lifecycle;
- immutable DCS revision semantics;
- temporal Deployment Resource Binding.

Authority Management owns catalogue mutation admission through separate actions:
- `CurateApplicationCatalogue` at server-selected scope `application-catalogue`;
- `CurateResourceCatalogue` at server-selected scope `resource-catalogue`.

Catalogue visibility, Resource Scope Affiliation, Resource Responsibility and `ReadScopedConnectivity` do not imply either curation authority.

### Persistence and transaction behavior

I27 uses additive PostgreSQL migrations. Existing Component Deployment and DCS identities are preserved; legacy deployments without first-class Application/Component parents receive deterministic compatibility parents during migration.

ACC and RC keep separate owner-specific curation repositories/UoWs. A Deployment Resource Binding command validates Resource state through an RC-owned projection adapter and commits only ACC-owned truth; no cross-context distributed transaction is introduced.

Mutable catalogue identities/facts use optimistic version preconditions where required. Mutations use durable idempotency receipts. Known SQL failure before commit is distinct from an ambiguous commit acknowledgement.

Creation provenance is not overwritten by later retirement/end operations; retirement/end provenance is recorded separately.

### HTTP and Web behavior

Catalogue routes live under `/api/v1/catalogues/**` and are task-oriented, not table CRUD. The authenticated session supplies actor identity, runtime supplies action time, owner adapters select catalogue authority scope, and mutations require `Idempotency-Key`.

Normal NAPMS-owned relationships use backend discovery rather than user-entered UUID combinations. DCS authoring selects only fully Active Application -> Component -> Deployment participants and accepts ACC-owned vendor-neutral communication semantics, not raw projection bytes or ACL syntax.

Responsibility Scope and Person/Team identities remain external correlation references in I27 because NAPMS does not yet own a corresponding registry. ADR-011 permits explicit input of those external references without treating them as generated NAPMS identity or authority.

Resources workspace has a dedicated owner-side read projection for effective Responsibility Scope filtering, current responsibility/contact search and current-fact completeness indicators. Lightweight Resource discovery remains separate for cross-entity forms such as Deployment Resource Binding.

Canonical feature boundaries:
- `docs/architecture/catalogue-curation-boundary.md`;
- `docs/engineering/catalogue-curation-command-contract.md`;
- `docs/engineering/catalogue-curation-http-api-contract.md`;
- `docs/requirements/catalogue-curation.md`.

## I26 Traffic Analysis Checker boundary

Checker continues to answer the inverse operational question from a technical traffic tuple without owning peer business truth:

```text
source/destination technical tuple + asOf
    -> RC address/resource resolution
    -> ACC component/DCS context
    -> existing Requirement / Decision / Rule / Effective Policy summaries
    -> unordered Network Context candidates
    -> stored Configured TAE matching
    -> Resource Responsibility/contact
```

Network Context candidate membership remains unordered and is not proof of traversal. Missing configured evidence remains unknown/missing evidence, not proof of absence. Resource Responsibility remains operational/contact truth, not permission.

## Existing full-chain boundaries

I25 retains the supported deterministic execution acceptance:

```text
Connectivity Requirement
    -> immutable Connectivity Decision
    -> Access Rule
    -> effective desired policy
    -> placement / technical realization
    -> reconciliation
    -> rendering
    -> deterministic controlled execution
    -> post-change verification (`Verified`)
```

This proves orchestration semantics with the existing deterministic NEO target stub; it does not claim real Cisco/device transport compatibility.

I27 adds a complementary fresh-input acceptance:

```text
catalogue curation
    -> fresh Resource/Application/Deployment/Binding/DCS
    -> Scoped Connectivity
    -> Connectivity Requirement declaration
    -> Need = Required
```

The acceptance starts without direct SQL/seed creation of the newly curated business objects. A separate authenticated HTTP/PostgreSQL acceptance proves catalogue read can remain available while mutation without `CurateResourceCatalogue` is backend-denied and persists nothing.

## Critical accepted boundaries

- `Required != Authorized`.
- Connectivity Decision owns final `Allowed | NotAllowed`; Access Policy owns Access Rule identity/state.
- catalogue visibility, Resource Scope Affiliation, Resource Responsibility and catalogue mutation authority are distinct.
- Resource responsibility/contact is not Authority Management truth.
- DCS revision is immutable application communication truth, not a firewall rule row.
- technical realization changes do not redefine Resource or Component Deployment identity.
- technical evidence is not authorization or desired policy.
- Logical Firewall identity remains independent from provider/device realization, Resource and Enforcement Attachment identity.
- Network Context candidate membership is not a proven path/order/traversal fact.
- rendered configuration is derived representation, not evidence of provider/device application.
- transport/apply acceptance is not semantic verification; `Verified` requires matching post-check evidence.
- Unknown apply is fail-closed and is not blindly retried.
- authentication identity does not grant business authority.
- external Responsibility Scope / Person / Team correlation references do not create NAPMS authority.
- cross-context composition consumes owner ports and does not acquire peer persistence ownership.
- Legacy/MSSQL, external catalogue sync and real provider/device transport remain non-current dependencies.
- Web dependency changes must keep package intent and lockfile consistent.

## Validation state

The pre-absorption I27 implementation candidate passed all configured hosted final gates on 2026-09-10:
- core gate;
- PostgreSQL persistence gate;
- Web gate;
- harness gate;
- knowledge gate;
- Docker local runtime gate.

The implementation gate includes focused I27 core/runtime/PostgreSQL evidence, deterministic migration replay/backfill, Resource workspace projection coverage, fresh-data Connectivity/Need acceptance and read-allowed/mutation-denied security acceptance.

## Current execution

I27 Catalogue Curation is absorbed for the supported local target. No further implementation increment is selected by this snapshot.

Future catalogue expansion requires a new accepted requirement. Explicit non-current candidates include bulk import/edit, external catalogue/CMDB synchronization, organization/company hierarchy management, fine-grained foreign catalogue visibility, generic custom fields, catalogue approval workflow and real provider/device discovery.

I26 Traffic Analysis Checker, I25 Product Completion, I24 Local Deployment and Operational Hardening, I23 Optional Integration Extension Skeleton, I22 Network Environment Operations, I21 Configuration Rendering, I20 Reconciliation, I19 Network Enforcement Placement, I18 Technical-to-Domain Access Resolution, I17 Technical Access Evidence, I16B Connectivity Decision Runtime/Workflow and earlier increments remain complete and absorbed.

## Canonical references

Use the smallest relevant set:
- current catalogue curation requirement: `docs/requirements/catalogue-curation.md`;
- catalogue curation architecture: `docs/architecture/catalogue-curation-boundary.md`;
- catalogue command/HTTP contracts: `docs/engineering/catalogue-curation-command-contract.md`, `docs/engineering/catalogue-curation-http-api-contract.md`;
- Strategic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- Resource responsibility boundary: `docs/domain/resource-role-model.md`;
- Traffic Analysis boundary: `docs/requirements/traffic-analysis-checker.md`, `docs/architecture/network-context-candidate-boundary.md`;
- current target architecture: `docs/architecture/current-architecture.md`;
- local operator procedure: `docs/engineering/local-product-operator-runbook.md`;
- active work only: `docs/plans/active/`.

Completed execution plans are intentionally not retained as working-tree archives.
