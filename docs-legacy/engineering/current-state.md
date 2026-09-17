# Current implementation state

Status: `I31 Application Catalogue migration accepted and implemented for the supported local target; APR target semantics under active revalidation`.

Date: 2026-09-13.

Current execution pointer: `docs/plans/active/README.md`.

This file is a capability snapshot, not an increment-by-increment changelog. It must not be used to infer target APR semantics from existing runtime code.

## Capability snapshot

| Capability | Semantic state | Runtime / persistence | Human-facing surface |
| --- | --- | --- | --- |
| Access Policy | accepted | PostgreSQL-backed Domain/Application implementation with materialization, Active/Inactive, EffectiveWindow and effective-policy selection | Access Rules, Rule Details, Effective Desired Policy |
| Authority Management | accepted through I31 | PostgreSQL-backed scoped action admission including separate catalogue curation actions | consumed by authenticated use cases; no generic IAM admin surface |
| Application Communication Catalogue | accepted through I31 | PostgreSQL-backed Application Definition / Component / Interaction Definition / Application Deployment / Deployment Interaction model; interaction-scoped Resource membership; immutable DCS compatibility snapshots; preserved legacy I27 truth | `Applications -> Definitions | Deployments`, Definition tabs, Deployment connectivity and Resource-set drill-downs |
| Resource Catalogue | accepted through I27 | PostgreSQL-backed Resource lifecycle, Endpoint/realization history, Resource Scope Affiliation, Resource Responsibility/contact, reverse address resolution and curation read/write seams | Resources catalogue workspace, Connectivity and Checker ownership/domain resolution |
| Connectivity Requirements | accepted | PostgreSQL-backed declaration/read/change/retire lifecycle | Needs plus coarse Need state in Connectivity; summarized in Checker policy matches |
| Requirement-to-Policy Alignment | accepted application composition | no independent aggregate/table; derives coverage from authoritative Requirements + Access Policy | Needs and coarse coverage in Connectivity |
| Connectivity Decision | accepted first-class bounded context | PostgreSQL-backed immutable final Decision runtime with exact subject/scope/time selection, supersession and fail-closed persistence semantics | Decisions workspace plus coarse Decision state in Connectivity and Checker |
| Policy export / normalization | accepted | coherent snapshot + vendor-neutral normalized policy JSON | Normalized Policy |
| Scoped Connectivity Inventory | accepted owner-preserving application composition | framework-free read composition with module-owned PostgreSQL adapters; no independent persistence | primary Connectivity workspace and policy/governance input to Checker |
| Technical Access Evidence | accepted | Domain/Application/Ports + TAE-owned PostgreSQL + strict local JSON import adapter | consumed through explicit downstream contracts |
| Network Enforcement Placement | accepted target by ADR-018; runtime migration pending where required | current-state Firewall/routing/interface/override model and policy-locator contract are normative; older stronger runtime path capabilities are not APR input semantics | target/candidate information for downstream consumers |
| Access Policy Realization | **target under active revalidation** | existing runtime implementation remains migration code only; it is not a source of target semantics | no APR product contract is normative beyond `docs/domain/access-policy-realization/README.md` |
| Network Environment Operations | accepted stub-first Tactical DDD | deterministic in-process target stub + in-memory operation repository; no real Cisco transport or crash-durable audit claim | controlled operation evidence where explicitly invoked |
| Traffic Analysis Checker | accepted read composition | no independent persistence; RC reverse resolution + ACC bindings + Scoped Connectivity summaries + Network Context + stored TAE + Resource Responsibility | Checker workspace |
| Catalogue Curation | accepted through I31 | RC curation from I27 plus current ACC target commands/read models, PostgreSQL UoWs, authenticated task-oriented HTTP API, optimistic concurrency and durable idempotency receipts | `CATALOGUES -> Applications / Resources` |
| Optional external identity/source extension | accepted dormant seam | source-neutral verified external identity mapping proof; no primary runtime wiring | none |
| Local deployment and operations | accepted local target | password/SCRAM PostgreSQL, repeatable non-mutating startup, logical backup/clean restore, migrations, diagnostics, container hardening and locked Web dependency graph | Make targets, operator runbook and Web UI |

## Current runtime boundary

Supported local topology remains:

```text
browser
  -> loopback-published nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

Local username/password authentication with server-side sessions remains primary. PostgreSQL is authoritative local persistence. No external IdP, directory, CMDB, application registry, catalogue source, MSSQL dependency or real network lab is required for normal supported operation.

The Compose path keeps PostgreSQL internal and password-authenticated with SCRAM-SHA-256 on fresh volumes. Startup is non-mutating apart from explicit credential preparation/rotation; logical backup/clean restore and forward migrations remain the supported recovery/upgrade mechanisms.

## Application Catalogue — current I31 boundary

I31 supersedes the I27 Application-side authoring hierarchy with the current model:

```text
Application Definition
  -> Components
  -> Interaction Definitions

Application Deployment
  -> Application Definition
  -> Company / Environment / Scope context
  -> selected Deployment Interactions
      -> Source Resource set
      -> Destination Resource set
      -> internal compatibility DirectedInteractionIdentity
```

The existing stable Application and Component identities remain valid. Application Deployment and Deployment Interaction are new first-class ACC identities. Resource membership belongs to a Deployment Interaction side rather than globally to a Component.

Interaction Definition owns current reusable vendor-neutral traffic intent. A Deployment selects an Interaction Definition without endpoint or traffic override. Potentially unbounded Definition, Deployment, Interaction, Resource and dependency lists use bounded server-side paging/search/filter/sort.

### Downstream compatibility

Each Active Deployment Interaction projects internally to stable source/destination compatibility Component Deployment IDs and a current immutable DCS revision. Existing Connectivity Requirement, Connectivity Decision, Access Policy and export contracts continue consuming their existing directed interaction identity shape.

Compatibility IDs remain backend-only implementation identities in current Application authoring. Users operate on Definitions, Components, Deployments, Interactions and Resources.

A permitted Interaction Definition traffic edit creates new immutable DCS snapshots for all affected Active Deployment Interactions while preserving old DCS revisions and historical downstream references. Active/effective downstream dependencies block unsafe edits and retirements through explicit owner-query ports and grouped dependency projections.

### Legacy coexistence

Pre-I31 Component Deployments, DCS revisions and Deployment Resource Bindings remain valid legacy ACC/downstream truth. They are not automatically converted into Application Deployments because Company/Environment/Scope and target interaction ownership cannot be inferred safely.

Legacy truth remains available to compatibility/history consumers; the current Applications Web/API authoring model does not present Component Deployment as the deployment unit.

### Current Web and HTTP behavior

Application routes remain under `/api/v1/catalogues/**` and expose task-oriented target commands/read models. The Web entry point provides:

- `Definitions | Deployments` working sets;
- Definition Overview / Components / Interactions / Deployments;
- create/edit/retire flows for current ACC entities;
- Deployment connectivity with selected interaction subset;
- source/destination Resource counts and bounded drill-down/edit;
- structured dependency counts/drill-downs for blocked operations;
- no ordinary hard-delete path or user-facing compatibility UUID workflow.

Resource Catalogue curation behavior from I27 remains current and unchanged by I31.

## Authority and ownership

Application Communication Catalogue owns current Application Definition, Component, Interaction Definition, Application Deployment, Deployment Interaction and interaction-side membership semantics plus the internal compatibility projection.

Resource Catalogue owns stable Resource identity, technical realization history, Resource Scope Affiliation and Resource Responsibility/contact.

Authority Management owns catalogue mutation admission through:
- `CurateApplicationCatalogue` at server-selected scope `application-catalogue`;
- `CurateResourceCatalogue` at server-selected scope `resource-catalogue`.

Catalogue visibility, Resource Scope Affiliation, Resource Responsibility, Application owner reference, Deployment Company/Environment/Scope and `ReadScopedConnectivity` do not imply catalogue mutation authority.

## Access Policy Realization revalidation boundary

APR target semantics must be read only from:

- `docs/domain/access-policy-realization/README.md`.

The target direction is:

```text
supplied target + required effective policy
                +
comparable configured effective policy
                |
                v
realization assessment
    -> exact semantic delta
    -> policy change design
    -> pre-change semantic verification
    -> semantics-preserving rendering
    -> downstream operational execution
```

Existing APR runtime types, routes, tests and read compositions are not target-domain evidence. They remain implementation/migration material until a new Tactical DDD and migration plan are accepted.

In particular, target selection/relevance remains upstream, and large policy-space comparison is expected to be data-local behind APR semantic contracts rather than requiring full application-memory materialization.

## Visual regression evidence

The browser acceptance uses a fixed desktop viewport and deterministic pixel-derived perceptual fingerprints for representative current Application layouts:

- Definitions list;
- Definition Interactions;
- Deployment Connectivity.

The semantic assertions execute before screenshot comparison. Screenshot evidence therefore protects accepted rendering without replacing domain/product assertions.

## Critical accepted boundaries

- `Required != Authorized`.
- Connectivity Decision owns final `Allowed | NotAllowed`; Access Policy owns Access Rule identity/state.
- Application Catalogue current authoring identities are distinct from internal compatibility Component Deployment/DCS identities.
- interaction-scoped Resource membership does not redefine Component identity.
- catalogue visibility, Resource Scope Affiliation, Resource Responsibility and catalogue mutation authority are distinct.
- Resource responsibility/contact is not Authority Management truth.
- DCS revision is immutable application communication snapshot truth, not a firewall rule row.
- technical realization changes do not redefine Resource or ACC business identity.
- technical evidence is not authorization or desired policy.
- NEP target relevance is not APR policy-realization semantics.
- APR compares effective policy behavior, not raw rule/configuration decomposition.
- semantic delta is not a concrete policy edit plan.
- rendered configuration is derived representation, not evidence of provider/device application.
- transport/apply acceptance is not semantic verification; downstream operational verification requires matching post-check evidence.
- authentication identity does not grant business authority.
- cross-context composition consumes owner contracts and does not acquire peer persistence ownership.
- physical PostgreSQL colocation does not authorize cross-context private-table coupling.
- Legacy/MSSQL, external catalogue sync and real provider/device transport remain non-current dependencies.
- Web dependency changes must keep package intent and lockfile consistent.

## Current execution

I31 Application Catalogue migration is absorbed for the supported local target.

APR is the active domain-design/revalidation area. No implementation migration should promote existing APR runtime semantics until the target contracts and Tactical DDD are accepted.

Future catalogue expansion requires a new accepted requirement. Explicit non-current candidates include Application Definition versioning, Deployment-specific interaction overrides, explicit legacy-to-Deployment migration with sufficient business input, bulk import/edit, external catalogue/CMDB synchronization, organization/company hierarchy management, fine-grained catalogue visibility, generic custom fields and catalogue approval workflow.

## Canonical references

Use the smallest relevant set:
- current ACC Tactical DDD: `docs/domain/application-communication-catalogue/tactical-model.md`;
- current Application Catalogue requirement: `docs/requirements/application-catalogue-target.md`;
- current Application Catalogue architecture: `docs/architecture/application-catalogue-target-boundary.md`;
- I31 compatibility decisions: `docs/decisions/ADR-012-application-definition-deployment-model.md`, `docs/decisions/ADR-013-i31-application-catalogue-compatibility-and-reference-semantics.md`;
- Resource catalogue curation: `docs/requirements/catalogue-curation.md`, `docs/architecture/catalogue-curation-boundary.md`;
- Strategic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- Resource responsibility boundary: `docs/domain/resource-role-model.md`;
- Network Enforcement Placement target: `docs/domain/network-enforcement-placement/target-tactical-model.md`;
- Access Policy Realization current framing: `docs/domain/access-policy-realization/README.md`;
- Traffic Analysis boundary: `docs/requirements/traffic-analysis-checker.md`, `docs/architecture/network-context-candidate-boundary.md`;
- current target architecture: `docs/architecture/current-architecture.md`;
- local operator procedure: `docs/engineering/local-product-operator-runbook.md`;
- active work only: `docs/plans/active/`.

Completed execution plans are intentionally not retained as working-tree archives.
