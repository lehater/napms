# Current implementation state

Status: `I15 semantic baseline accepted; I16A Scoped Connectivity Workspace Foundation is current execution`.

Date: 2026-09-09.

Current execution pointer: `docs/plans/active/README.md`.

This file is a capability snapshot, not an increment-by-increment changelog. Detailed history lives in Git; ordered future work lives in `docs/engineering/post-wave1-product-completion-roadmap.md`.

## Capability snapshot

| Capability | Semantic state | Runtime / persistence | Human-facing surface |
|---|---|---|---|
| Access Policy | accepted | PostgreSQL-backed Domain/Application implementation with materialization, Active/Inactive, EffectiveWindow and effective-policy selection | Access Rules, Rule Details, Effective Desired Policy |
| Authority Management | accepted | PostgreSQL-backed scoped action admission | consumed by authenticated use cases; no generic IAM admin surface |
| Application Communication Catalogue | accepted | PostgreSQL-backed catalogue, immutable DCS projection semantics, authorized interaction discovery and presentation metadata | label-first interaction selection/presentation |
| Resource Catalogue | accepted | PostgreSQL-backed Resource/Endpoint realization | currently supporting policy/export and I16A resource-centric work |
| Connectivity Requirements | accepted | PostgreSQL-backed declaration/read/change/retire lifecycle | My Connectivity Needs |
| Requirement-to-Policy Alignment | accepted application composition | no independent aggregate/table; derives `Covered | Uncovered | NotCurrent | Unknown` from authoritative Requirements + Access Policy | shown from Requirement views |
| Connectivity Decision | accepted first-class bounded context through I15 | durable runtime not yet on main; current local-dev composition uses the explicit transitional `local-dev:allowed` adapter | no durable Decision workflow/workspace yet |
| Policy export / normalization | accepted | coherent snapshot + vendor-neutral normalized policy JSON | Normalized Policy |
| Scoped Connectivity Inventory | selected I16A product/application composition | current main remains gated by PLAN-029 semantic/application stages | target primary Connectivity workspace after I16A |
| Technical Access Evidence | strategic future context | not implemented | none |
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
- The `local-dev:allowed` adapter is transitional runtime plumbing and is not the accepted durable Decision mechanism.
- Requirement-to-Policy Alignment is derived composition, not peer persisted business truth.
- authenticated actor identity comes from the server/session boundary; request payloads do not establish actor identity.
- business authority and catalogue visibility are distinct concerns.
- technical realization changes do not silently redefine domain identity.
- Legacy/MSSQL and vendor/device execution are not current product dependencies.

## Current execution

I16A is owned by `docs/plans/active/PLAN-029-i16a-scoped-connectivity-workspace.md`.

The selected product direction is a responsibility-scope/resource-centric Connectivity workspace. The active plan owns its current gate, blockers and write-set; this snapshot deliberately does not mirror mutable work-package state.

After I16A completes, the roadmap currently sequences I16B Connectivity Decision Runtime and Workflow, which replaces the transitional local Decision provider with the accepted durable Decision application/runtime slice.

## Canonical references

Use the smallest relevant set:
- Strategic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- current accepted requirements: `docs/requirements/`;
- target architecture: `docs/architecture/`;
- consequential decisions: `docs/decisions/`, including ADR-005 for Connectivity Decision;
- runtime contracts: `docs/engineering/`;
- active work only: `docs/plans/active/`.

Completed execution plans and absorbed working packets are intentionally not retained as working-tree archives.
