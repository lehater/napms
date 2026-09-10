# I25 Product Completion Gap Matrix

Status: `accepted I25 WP1 completion audit`.

Date: 2026-09-10.

## Purpose

Map the mandatory supported-local product-completion chain to current executable/runtime/user-facing evidence and identify only the gaps that block truthful product completion.

This audit does not make optional enterprise identity/source integrations, real Cisco transport, HA or enterprise infrastructure mandatory.

## Current human-facing surface

The authenticated Web application currently exposes these primary workspaces:
- Connectivity;
- Needs (Connectivity Requirements);
- Decisions;
- Rules;
- Effective Desired Policy;
- Export / Normalized Policy.

The current application shell has no primary workspace for Technical Access Evidence, Network Enforcement Placement, Access Policy Realization/reconciliation/rendering or Network Environment Operations.

## Completion matrix

| Mandatory chain stage | Current semantic/runtime evidence | Current human-facing evidence | Completion gap |
| --- | --- | --- | --- |
| Declared connectivity need | Connectivity Requirements Domain/Application/PostgreSQL; HTTP tests; local Docker journey declares/reuses a Requirement | Connectivity + Request Access + Needs/detail workspaces | none for first local slice |
| Connectivity decision | Connectivity Decision Domain/Application/PostgreSQL and HTTP tests; Scoped Connectivity exposes final-decision state | Decisions list/detail plus Connectivity coarse decision state | none for first local slice |
| Authoritative desired Access Rule | Access Policy PostgreSQL runtime; proposal/materialization flow; Rule HTTP tests | Rules list/detail; Request Access resolves/materializes Rule | none for first local slice |
| Effective desired policy | effective-policy selection and coherent policy HTTP/runtime evidence | Effective workspace with Rule navigation | none for first local slice |
| Enforcement placement / technical realization | NEP-owned durable knowledge + APR owner-preserving composition/integration tests | none | P1 operator visibility/explainability gap |
| Desired-vs-configured conclusion | APR reconciliation Domain/Application + PostgreSQL owner-preserving integration tests | none | P1 operator visibility/explainability gap |
| Target rendering | APR rendering + Cisco ASA outer adapter + semantic equivalence proof | none | P1 operator visibility/explainability gap |
| Controlled execution | NEO Domain/Application + deterministic target stub + integration proof | none | P1 network-operator workflow gap |
| Post-change technical evidence | TAE-owned durable evidence and NEO post-state verification semantics | none | P1 operator evidence/explainability gap |
| Explainable end-to-end provenance | provenance exists inside Requirement/Decision/Rule/APR/NEP/TAE/NEO contracts and tests | fragmented Requirement/Decision/Rule details only | P1 cross-chain explainability/navigation gap |

## Executable acceptance coverage

Current executable evidence is split into two substantial but disconnected chains.

### Upstream product/runtime journey

The local Docker product journey exercises authenticated product behavior through the existing Web/HTTP runtime family, including requirement/proposal/decision/rule state and current product reads.

### Downstream realization/execution journey

`tests/integration/postgres/test_network_environment_operations_stub_flow.py` proves a desired-policy -> rendering -> deterministic target apply -> post-check `Verified` path while preserving owner state.

That downstream proof seeds/materializes the Access Rule and placement/evidence prerequisites directly. It does not begin from a declared Connectivity Requirement and final Connectivity Decision.

### Missing proof

There is no single executable acceptance scenario that starts from a declared connectivity need and continues through the accepted decision/materialization path into placement, realization, reconciliation, rendering, controlled execution and verified post-state.

This is the highest-priority I25 blocker because the roadmap product-completion criterion explicitly requires the complete local chain to be demonstrable.

## Ranked findings

### P0 — No single full-chain executable acceptance proof

The product has strong upstream and downstream proofs, but they are separated by fixture/seed boundaries. Product completion cannot truthfully claim one demonstrated Requirement -> Decision -> Rule -> realization -> rendering -> execution -> verification chain until one owner-preserving acceptance composition/test crosses that boundary.

Required closure:
- reuse existing application/domain APIs and owner-owned repositories;
- create no copied cross-context truth;
- use the accepted deterministic NEO target stub;
- assert provenance/identity continuity at each semantic handoff;
- fail closed when placement/evidence/reconciliation prerequisites are missing or ambiguous.

### P1 — Downstream network-operator stages have no HTTP/Web read surface

APR/NEP/TAE/NEO semantics are executable internally but invisible to a human operator. A network/security operator cannot inspect where access should be enforced, whether configured evidence matches desired policy, what configuration would be rendered, what operation occurred or why verification succeeded/failed.

Required closure should prefer one owner-preserving operator read composition over exposing each bounded context as a generic CRUD workspace.

### P1 — End-to-end explainability is fragmented

Requirement, Decision and Rule detail screens exist, but there is no navigation/read model connecting those facts to enforcement target, reconciliation/rendering and execution/post-check evidence.

Required closure should compose references/provenance already owned by existing contexts; it must not create a new authoritative cross-context aggregate.

### P2 — Primary navigation is capability-centric, not role-task-oriented

The current shell exposes all current policy workspaces uniformly. Existing Authority checks protect actions, but the UI does not yet organize the supported journey around requirement owner, decision participant and network/security operator tasks.

This is a usability/productivity gap, not a new role/IAM semantic requirement.

### P2 — Search/filter coverage is uneven

List workspaces provide bounded paging and selected filters but there is no accepted evidence yet that broader global search or bulk actions are necessary. Improve only where WP2/WP3 operator journeys demonstrate a concrete task bottleneck.

### P2 — Web dependency lockfile remains absent

This is a reproducibility/dependency-hardening debt carried from I24. It does not block semantic product acceptance but should be closed before final roadmap completion if the supported Web build is expected to be reproducible.

### P3 — Dashboard/export expansion is not currently justified

A generic dashboard, extra CSV/XLSX exports or bulk mutation surfaces have no demonstrated consumer need from this audit. Do not implement them by default.

## Selected I25 sequencing

1. **WP2A — Full-chain acceptance composition/test (P0).** Close executable evidence first without UI changes.
2. **WP2B — Network-operator realization/execution read model and HTTP surface (P1).** Define the smallest read-only owner-preserving projection required to explain downstream state.
3. **WP3 — Web operator journey + cross-chain explainability navigation (P1/P2).** Present the selected read model and link existing Requirement/Decision/Rule references into it.
4. Reassess search/filter/role-oriented navigation and dependency reproducibility after the actual operator journey exists.

## Non-goals confirmed

I25 does not require by default:
- real Cisco/device transport or a lab;
- external IdP/OIDC;
- external CMDB/catalogue/Authority sources;
- MSSQL/Legacy bridge;
- enterprise HA/TLS/secret-store topology;
- new generic IAM roles;
- new cross-context authoritative persistence;
- speculative dashboards, exports or bulk operations.
