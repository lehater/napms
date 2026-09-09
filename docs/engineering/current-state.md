# Current implementation state

Status: `I17 Technical Access Evidence Core accepted and implemented; I18 Technical-to-Domain Access Resolution is the next roadmap increment`.

Date: 2026-09-09.

Current execution pointer: `docs/plans/active/README.md`.

This file is a capability snapshot, not an increment-by-increment changelog. Detailed history lives in Git; ordered future work lives in `docs/engineering/post-wave1-product-completion-roadmap.md`.

## Capability snapshot

| Capability | Semantic state | Runtime / persistence | Human-facing surface |
| --- | --- | --- | --- |
| Access Policy | accepted | PostgreSQL-backed Domain/Application implementation with materialization, Active/Inactive, EffectiveWindow and effective-policy selection | Access Rules, Rule Details, Effective Desired Policy |
| Authority Management | accepted | PostgreSQL-backed scoped action admission | consumed by authenticated use cases; no generic IAM admin surface |
| Application Communication Catalogue | accepted | PostgreSQL-backed catalogue, immutable DCS projection semantics, authorized interaction discovery and presentation metadata | label-first interaction selection/presentation |
| Resource Catalogue | accepted | PostgreSQL-backed Resource/Endpoint realization plus time-qualified Resource Scope Affiliation | supports policy/export and the resource-centric Connectivity workspace |
| Connectivity Requirements | accepted | PostgreSQL-backed declaration/read/change/retire lifecycle | Needs plus coarse Need state in Connectivity |
| Requirement-to-Policy Alignment | accepted application composition | no independent aggregate/table; derives `Covered | Uncovered | NotCurrent | Unknown` from authoritative Requirements + Access Policy | Needs and coarse coverage in Connectivity |
| Connectivity Decision | accepted first-class bounded context | PostgreSQL-backed immutable final Decision runtime with exact subject/scope/time selection, supersession and fail-closed persistence semantics | Decisions workspace plus coarse Decision state in Connectivity |
| Policy export / normalization | accepted | coherent snapshot + vendor-neutral normalized policy JSON | Normalized Policy |
| Scoped Connectivity Inventory | accepted owner-preserving product/application composition | framework-free read composition with module-owned PostgreSQL adapters, including durable coarse Decision enrichment; no independent persistence | primary post-login Connectivity workspace |
| Technical Access Evidence | accepted Tactical DDD | framework-free Domain/Application/Ports + TAE-owned PostgreSQL + strict local JSON import adapter + dedicated composition record/readback; no public TAE transport | none |
| Network Enforcement Placement | strategic future context | not implemented | none |
| Access Policy Realization | strategic future context | not implemented | none |

## Current runtime boundary

Implemented local runtime:

```text
browser
  -> nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

Current operational support includes:
- tracked PostgreSQL migrations and idempotent local demo seed;
- local login/password authentication with opaque server-side sessions;
- server-owned authenticated actor identity;
- structured runtime logging/correlation plus liveness/readiness;
- Docker Compose startup through `make dev-up`;
- one public local endpoint through nginx;
- PostgreSQL and FastAPI not exposed directly to the host by the normal local topology.

This remains a local/development topology, not a production deployment claim.

## Critical accepted boundaries

- `Required != Authorized`: a Connectivity Requirement never creates or permits an Access Rule by itself.
- Connectivity Decision owns final `Allowed | NotAllowed` reason/validity/supersession semantics; Access Policy owns Access Rule identity/state.
- Proposal authority does not imply decision authority.
- Normal product composition consumes durable Connectivity Decision truth; there is no deterministic allow fallback in the local runtime.
- Requirement-to-Policy Alignment is derived composition, not peer persisted business truth.
- authenticated actor identity comes from the server/session boundary; request payloads do not establish actor identity.
- business authority and catalogue visibility are distinct concerns.
- technical evidence is not authorization, desired policy, current/fresh truth or domain-resolution truth;
- source-qualified evidence time remains distinct from NAPMS recording time;
- technical realization changes do not silently redefine domain identity.
- Legacy/MSSQL and vendor/device execution are not current product dependencies.

## Current execution

No implementation plan is currently selected.

I17 Technical Access Evidence Core is complete and absorbed into canonical product/domain/architecture/engineering truth. The implemented core now provides:
- immutable source-qualified Technical Access Evidence Sets and duplicate-preserving entries;
- accepted `Configured | TrafficDerived | Imported` evidence kinds without authorization semantics;
- explicit source/scope/capture identity plus `Unknown | Instant | Window` Evidence Time distinct from `RecordedAt`;
- source-neutral address/protocol/port normalization with fail-closed ambiguity handling;
- source + capture retry/idempotency identity and explicit conflicting-capture / commit-unknown outcomes;
- TAE-owned append-only PostgreSQL persistence with corrupt-state fail-closed hydration;
- one strict local JSON import adapter and dedicated PostgreSQL composition record/readback path;
- executable proof that evidence recording creates neither Access Rules nor Connectivity Decisions;
- no current/fresh selection, technical-to-domain resolution, enforcement placement or reconciliation semantics.

There is intentionally no public TAE HTTP/Web surface or human Authority Management workflow in I17.

I16B Connectivity Decision Runtime and Workflow, including the later accepted Decisions frontend workspace, is also complete and absorbed into canonical truth.

The roadmap next increment is I18 — Technical-to-Domain Access Resolution. It is not yet selected for execution, so there is no active `PLAN-*.md`.

## Canonical references

Use the smallest relevant set:
- Strategic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- current accepted requirements: `docs/requirements/`;
- target architecture: `docs/architecture/`;
- consequential decisions: `docs/decisions/`, including ADR-005 for Connectivity Decision;
- runtime contracts: `docs/engineering/`;
- active work only: `docs/plans/active/`.

Completed execution plans and absorbed working packets are intentionally not retained as working-tree archives.
