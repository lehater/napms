# Current implementation state

Status: `I16B implemented; I17 Technical Access Evidence WP3 durable source proof complete, WP4 closure active`.

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
| Technical Access Evidence | accepted Tactical DDD through I17 WP0 | Domain/Application/Ports + TAE-owned PostgreSQL + strict local/import normalization and durable composition readback implemented on active branch | none |
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
- technical realization changes do not silently redefine domain identity.
- Legacy/MSSQL and vendor/device execution are not current product dependencies.

## Current execution

I17 Technical Access Evidence Core is selected. WP0-WP3 are complete on the active branch; WP4 final proof/closure is active.

I16B Connectivity Decision Runtime and Workflow is complete and absorbed into canonical product, architecture and engineering truth. The implemented runtime now provides:
- durable immutable final `Allowed | NotAllowed` Decisions with validity, reason/evidence, provenance and supersession;
- independent `DecideConnectivity` and `ReadConnectivityDecision` authority;
- Access Policy selection by exact subject + governance scope + logical time;
- coarse Decision enrichment in Scoped Connectivity without protected-detail leakage;
- authenticated Decision record/list/detail Web/HTTP workflows;
- a local Docker journey using real durable Decisions rather than deterministic allow plumbing.

The active execution plan is `docs/plans/active/PLAN-017-i17-technical-access-evidence-core.md`. Current task is WP4 final proof/closure. No public TAE HTTP/Web, human authority workflow or provider/device integration has been introduced.

## Canonical references

Use the smallest relevant set:
- Strategic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- current accepted requirements: `docs/requirements/`;
- target architecture: `docs/architecture/`;
- consequential decisions: `docs/decisions/`, including ADR-005 for Connectivity Decision;
- runtime contracts: `docs/engineering/`;
- active work only: `docs/plans/active/`.

Completed execution plans and absorbed working packets are intentionally not retained as working-tree archives.
