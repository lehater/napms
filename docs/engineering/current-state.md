# Current implementation state

Status: `I26 Traffic Analysis Checker accepted and implemented for the supported local target`.

Date: 2026-09-10.

Current execution pointer: `docs/plans/active/README.md`; no active implementation plan remains after I26 absorption.

This file is a capability snapshot, not an increment-by-increment changelog. Detailed history lives in Git; roadmap status lives in the corresponding engineering roadmaps.

## Capability snapshot

| Capability | Semantic state | Runtime / persistence | Human-facing surface |
| --- | --- | --- | --- |
| Access Policy | accepted | PostgreSQL-backed Domain/Application implementation with materialization, Active/Inactive, EffectiveWindow and effective-policy selection | Access Rules, Rule Details, Effective Desired Policy |
| Authority Management | accepted | PostgreSQL-backed scoped action admission | consumed by authenticated use cases; no generic IAM admin surface |
| Application Communication Catalogue | accepted | PostgreSQL-backed catalogue, immutable DCS projection semantics, authorized interaction discovery and presentation metadata | label-first interaction selection/presentation; contributes Traffic Analysis component/DCS context |
| Resource Catalogue | accepted through I26 | PostgreSQL-backed Resource/Endpoint realization plus time-qualified Resource Scope Affiliation; reverse technical-address resolution; Resource Responsibility domain/read seam with deterministic local adapter | Connectivity workspace and Checker ownership/domain resolution |
| Connectivity Requirements | accepted | PostgreSQL-backed declaration/read/change/retire lifecycle | Needs plus coarse Need state in Connectivity; summarized in Checker policy matches |
| Requirement-to-Policy Alignment | accepted application composition | no independent aggregate/table; derives coverage from authoritative Requirements + Access Policy | Needs and coarse coverage in Connectivity |
| Connectivity Decision | accepted first-class bounded context | PostgreSQL-backed immutable final Decision runtime with exact subject/scope/time selection, supersession and fail-closed persistence semantics | Decisions workspace plus coarse Decision state in Connectivity and Checker |
| Policy export / normalization | accepted | coherent snapshot + vendor-neutral normalized policy JSON | Normalized Policy |
| Scoped Connectivity Inventory | accepted owner-preserving application composition | framework-free read composition with module-owned PostgreSQL adapters; no independent persistence | primary Connectivity workspace and policy/governance input to Checker |
| Technical Access Evidence | accepted Tactical DDD through I26 | framework-free Domain/Application/Ports + TAE-owned PostgreSQL + strict local JSON import adapter; shared backend technical-predicate matching | consumed by Realization and Checker; Checker exposes last-known configured snapshots/rule matches |
| Network Enforcement Placement | accepted through I26 | proven ForwardingPath remains an optional stronger capability; baseline Network Context candidate-set contract is unordered, provenance-bearing and may be incomplete/false-positive | consumed by Realization and Checker Network Context |
| Access Policy Realization | accepted I18 resolution + I20 derivation/reconciliation + I21 rendering | framework-free owner-preserving AP/RC/ACC/NEP/TAE composition; derived on demand; Cisco ASA renderer outer adapter | Realization read-only operator workspace |
| Network Environment Operations | accepted I22 stub-first Tactical DDD | deterministic in-process target stub + in-memory operation repository; no real Cisco transport or crash-durable audit claim | operation stage in Realization when actual result exists |
| Network Operator Realization View | accepted I25 read composition | authority-first PostgreSQL owner-preserving composition + authenticated HTTP router | Realization workspace with explicit stage availability and Rule navigation |
| Traffic Analysis Checker | accepted I26 read composition | no independent persistence; RC reverse resolution + ACC bindings + Scoped Connectivity policy summaries + unordered Network Context candidates + PostgreSQL Configured TAE lookup + Resource Responsibility projection; authenticated HTTP API | Checker workspace: Overview, Network Context, Policy, Ownership, Evidence |
| End-to-end product acceptance | accepted I25 evidence | PostgreSQL-backed acceptance proof from Requirement through deterministic controlled execution and Verified post-state | explainability navigation Realization -> Rule -> Decision -> Connectivity Requirement |
| Optional external identity/source extension | accepted I23 dormant seam | source-neutral verified external identity mapping proof; no primary runtime wiring | none |
| Local deployment and operations | accepted I24/I25 local target | password/SCRAM PostgreSQL, repeatable non-mutating startup, logical backup/clean restore, forward migration procedure, structured diagnostics, container hardening and locked Web dependency graph | Make targets, local product operator runbook and Web UI |

## Current runtime boundary

Implemented local runtime:

```text
browser
  -> loopback-published nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

Current operational support includes tracked PostgreSQL migrations, local login/password authentication, server-owned sessions/actor identity, structured logging/correlation, Docker Compose startup, one public nginx endpoint, PostgreSQL password authentication, logical backup/restore, local diagnostic helpers and reproducible Web dependency installation through `web/package-lock.json` + `npm ci`.

The supported Compose path does not use PostgreSQL network `trust`. Fresh volumes initialize host authentication with SCRAM-SHA-256. `make dev-up` generates an ephemeral local database credential, rotates the `napms` role before dependent services start, and verifies that the configured credential succeeds while a deliberately wrong credential fails. The normal startup probe is non-mutating and can be repeated on preserved local state.

Local username/password authentication is the primary supported authentication path. Local Authority/ACC/Resource state remains the supported current source of truth. No external IdP, directory, CMDB, catalogue or MSSQL dependency is required for normal operation.

## I25 product-completion boundary

The supported local product retains one executable full-chain acceptance proof:

```text
declared Connectivity Requirement
    -> immutable Connectivity Decision
    -> authoritative Access Rule
    -> effective desired policy
    -> enforcement placement / technical realization
    -> desired-vs-configured reconciliation
    -> target rendering
    -> controlled deterministic execution
    -> post-change verification (`Verified`)
```

This acceptance proof uses existing owner APIs/repositories and the accepted deterministic NEO target stub. It does not claim real Cisco/device transport compatibility.

## I26 Traffic Analysis Checker boundary

The product now also supports the inverse operational question from a technical traffic tuple:

```text
source IP + destination IP + protocol + port/range + asOf
    -> Resource Catalogue endpoint/resource resolution
    -> Application Communication Catalogue component/DCS context
    -> Requirement / Decision / Rule / Effective Policy summaries
    -> unordered Network Context candidate devices/enforcement targets
    -> latest applicable stored Configured TAE snapshot per candidate
    -> matching technical entries
    -> Resource Responsibility/contact information
```

The authenticated endpoint is `/api/v1/traffic-analysis`; Web exposes the result as the dedicated `Checker` workspace.

Important behavior:
- IP resolution preserves `Resolved | Ambiguous | Historical | Unknown` and does not collapse several candidate Resources into a false single answer;
- policy/governance may produce several matches and remains separate from technical evidence;
- Network Context candidate membership is not proof that traffic traverses a device and carries no reliable order unless another stronger source proves a path;
- candidate enumeration may be incomplete and may contain false positives;
- configured rules are read only from stored Technical Access Evidence, never synchronously from a firewall/device;
- snapshot capture time, record time, source and provenance remain explicit;
- a missing snapshot is `unknown/missing evidence`, not proof that no configured rule or enforcement exists;
- technical rule matching is backend-owned and covers exact, containment and overlap semantics for supported address/protocol/port predicates;
- Resource Responsibility/contact data is distinct from Authority Management and does not grant NAPMS action authority;
- the supported local target uses deterministic Network Context/responsibility adapters and seeded stored TAE snapshots; no real lab is required.

## Critical accepted boundaries

- `Required != Authorized`.
- Connectivity Decision owns final `Allowed | NotAllowed`; Access Policy owns Access Rule identity/state.
- business authority, catalogue visibility and operational responsibility/contact are distinct concerns.
- technical evidence is not authorization or desired policy.
- Logical Firewall identity is independent from provider/device realization, Resource identity and Enforcement Attachment identity.
- rendered configuration is a derived representation, not evidence of provider/device application.
- Network Context candidate membership is not a proven path/traversal/order fact.
- a proven `ForwardingPath` is a stronger optional capability and must not be fabricated from candidate enumeration.
- Network Environment Operations owns operation identity/outcome/concurrency/provenance, not desired policy, placement or rendering semantics.
- transport/apply acceptance is not semantic verification; `Verified` requires post-check evidence matching the requested artifact digest.
- Unknown apply is fail-closed and is not blindly retried.
- the current deterministic target stub proves execution semantics only; it does not prove Cisco connectivity or compatibility.
- Network Operator Realization View and Traffic Analysis Checker are read compositions and own no peer business truth.
- missing configured evidence remains explicit and is never inferred success or absence.
- authentication identity does not grant business authority; Authority Management remains the permission owner.
- optional external identity mapping remains dormant and fail-closed.
- Legacy/MSSQL and real provider/device transport remain non-current product dependencies.
- local deployment hardening does not imply enterprise TLS, external secret management, HA or multi-node topology.
- Web dependency changes must update the repository lockfile; supported CI/Docker builds use `npm ci`.

## Current execution

No implementation plan is selected after I26 absorption.

I26 Traffic Analysis Checker is complete for the supported local target. Durable outcomes include:
- a dedicated technical-entry-point Checker Web workspace with Overview, Network Context, Policy, Ownership and Evidence tabs;
- authenticated `/api/v1/traffic-analysis` runtime composition with no independent Checker persistence;
- Resource Catalogue reverse address resolution preserving ambiguous/historical/unknown outcomes;
- reuse of existing scoped connectivity policy composition rather than duplicated cross-context business truth;
- corrected NEP Network Context candidate-set semantics while retaining proven `ForwardingPath` only as a stronger optional capability;
- per-candidate latest applicable stored Configured TAE lookup with capture/record/provenance and backend traffic-predicate matching;
- a Resource Catalogue Resource Responsibility/contact seam distinct from Authority Management;
- deterministic local Network Context/responsibility adapters and demo configured-evidence snapshots, including an intentional missing-evidence candidate;
- focused tests for Network Context, address resolution, predicate matching, evidence selection and Traffic Analysis composition.

The pre-absorption I26 candidate passed core, PostgreSQL persistence, Web, harness, knowledge and Docker local-runtime gates. Docker coverage includes fresh authenticated product execution, preserved-volume restart with credential rotation, logical backup/clean restore, migration replay no-op and operator status diagnostics.

I25 Product Completion, I24 Local Deployment and Operational Hardening, I23 Optional Integration Extension Skeleton, I22 Network Environment Operations, I21 Configuration Rendering, I20 Reconciliation, I19 Network Enforcement Placement, I18 Technical-to-Domain Access Resolution, I17 Technical Access Evidence, I16B Connectivity Decision Runtime/Workflow and earlier increments remain complete and absorbed.

## Canonical references

Use the smallest relevant set:
- Strategic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- Resource responsibility/role boundary: `docs/domain/resource-role-model.md`;
- Checker requirement: `docs/requirements/traffic-analysis-checker.md`;
- Network Context boundary: `docs/architecture/network-context-candidate-boundary.md`;
- current target architecture: `docs/architecture/current-architecture.md`;
- Checker roadmap/history: `docs/engineering/traffic-analysis-checker-roadmap.md`;
- local operator procedure: `docs/engineering/local-product-operator-runbook.md`;
- active work only: `docs/plans/active/`.

Completed execution plans and absorbed working packets are intentionally not retained as working-tree archives.
