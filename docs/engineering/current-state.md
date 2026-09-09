# Current implementation state

Status: `I20 Desired-vs-Configured Reconciliation and Enforcement Policy Derivation accepted and implemented; I21 Configuration Rendering is next`.

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
| Network Enforcement Placement | accepted I19 Tactical DDD | framework-free Domain/Application/Ports + strict knowledge import + NEP-owned PostgreSQL immutable captures + time-qualified placement selection | none |
| Access Policy Realization | accepted I18 resolution + I20 enforcement derivation/reconciliation | framework-free Domain/Application/Ports + owner-preserving Access Policy/Policy Export, RC/ACC, NEP and TAE adapters + PostgreSQL-backed owner composition; derived on demand, no APR persistence | none |

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
- technical realization changes do not silently redefine domain identity;
- Logical Firewall identity is independent from provider/device realization, Resource identity and Enforcement Attachment identity;
- enforcement placement is independent from authorization/configured-policy satisfaction and fails closed on material path/correspondence/attachment uncertainty.
- Legacy/MSSQL and vendor/device execution are not current product dependencies.

## Current execution

No implementation plan is currently selected.

I20 Desired-vs-Configured Reconciliation and Enforcement Policy Derivation is complete and absorbed into canonical product/domain/architecture/engineering truth. The implemented APR slice provides:
- vendor-neutral desired Enforcement Intent derived from effective Access Policy + shared I18 domain resolution + NEP placement at one explicit `asOf`;
- Enforcement Target identity = Logical Firewall + Enforcement Attachment;
- explicit configured Evidence Set selection with same-managed-scope/source contract, exact evidence time and trustworthy effective-Permit completeness;
- exact canonical `common | missing | extra` technical witnesses and complete-only `No-op | Add | Remove | Replace` semantic delta;
- `Satisfied | Drift | Ambiguous | Unknown` with fail-closed Unknown/Ambiguous precedence and no ambiguity winner;
- target-local configured-domain attribution through the unchanged shared I18 matcher;
- owner-preserving anti-corruption adapters with explicit correlation checks for desired-policy, placement and configured-evidence projections;
- PostgreSQL-backed composition over existing owner contexts proving No-op/Add/Remove/Replace, incomplete-contract Unknown and temporal target movement;
- no APR-owned persistence, public HTTP/Web workflow, vendor rendering or provider/device execution.

I19 Network Enforcement Placement, I18 Technical-to-Domain Access Resolution, I17 Technical Access Evidence Core and I16B Connectivity Decision Runtime/Workflow remain complete and absorbed into canonical truth.

The next roadmap increment is I21 — Configuration Rendering. It is not selected for execution, so there is no active `PLAN-*.md`.

## Canonical references

Use the smallest relevant set:
- Strategic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- current accepted requirements: `docs/requirements/`;
- target architecture: `docs/architecture/`;
- consequential decisions: `docs/decisions/`, including ADR-005 for Connectivity Decision;
- runtime contracts: `docs/engineering/`;
- active work only: `docs/plans/active/`.

Completed execution plans and absorbed working packets are intentionally not retained as working-tree archives.
