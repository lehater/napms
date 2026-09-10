# Current implementation state

Status: `I24 Local Deployment and Operational Hardening accepted and implemented; I25 Product Completion, Operator UX and Acceptance is next`.

Date: 2026-09-10.

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
| Access Policy Realization | accepted I18 resolution + I20 derivation/reconciliation + I21 configuration rendering | framework-free Domain/Application/Ports + owner-preserving Access Policy/Policy Export, RC/ACC, NEP and TAE adapters + PostgreSQL-backed owner composition; derived on demand, no APR persistence; Cisco ASA renderer outer adapter with semantic equivalence proof | none |
| Network Environment Operations | accepted I22 stub-first Tactical DDD | framework-free Domain/Application/consumer-owned ports + deterministic in-process target stub + in-memory operation repository; no real Cisco transport or crash-durable audit claim | none |
| Optional external identity/source extension | accepted I23 dormant seam | source-neutral `VerifiedExternalIdentity` + `ActorIdentityResolver` deterministic mapping proof; no runtime wiring, provider transport, external source synchronization or persistence requirement | none |
| Local deployment and operations | accepted I24 local target | password/SCRAM PostgreSQL, repeatable non-mutating startup, logical backup/clean restore, forward migration procedure, structured diagnostics and low-risk container hardening | Make targets and operator documentation |

## Current runtime boundary

Implemented local runtime:

```text
browser
  -> loopback-published nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

Current operational support includes tracked PostgreSQL migrations, local login/password authentication, server-owned sessions/actor identity, structured logging/correlation, Docker Compose startup, one public nginx endpoint, PostgreSQL password authentication, logical backup/restore and local diagnostic helpers.

The supported Compose path no longer uses PostgreSQL network `trust`. Fresh volumes initialize host authentication with SCRAM-SHA-256. `make dev-up` generates an ephemeral local database credential, rotates the `napms` role before dependent services start, and verifies that the configured credential succeeds while a deliberately wrong credential fails. The normal startup probe is non-mutating and can be repeated on preserved local state.

Local PostgreSQL recovery uses validated custom-format logical backups. Clean restore is explicitly destructive, requires confirmation, restores into a new local volume, then re-enters the normal migration/startup path. Forward upgrade requires a pre-upgrade backup; arbitrary reverse-migration/downgrade compatibility is not claimed.

`make dev-status` exposes the supported local diagnostic path: Compose state plus public liveness/readiness and a PostgreSQL query probe. Structured application logs remain the detailed diagnostic source. A dedicated metrics backend is not required by the current local target.

Backend-derived and Web Compose services use init/reaping plus `no-new-privileges`; the backend runtime remains non-root. PostgreSQL retains the official image privilege/entrypoint model rather than a speculative override.

Local username/password authentication is the primary supported authentication path. Local Authority/ACC/Resource state remains the supported current source of truth. No external IdP, directory, CMDB, catalogue or MSSQL dependency is required for normal operation.

This remains a local deployment topology, not a claim of enterprise HA/SLA topology. No accepted workload target currently supports a throughput/latency/SLA claim; capacity validation remains deferred until such a target is accepted.

## Critical accepted boundaries

- `Required != Authorized`.
- Connectivity Decision owns final `Allowed | NotAllowed`; Access Policy owns Access Rule identity/state.
- business authority and catalogue visibility are distinct concerns.
- technical evidence is not authorization or desired policy.
- Logical Firewall identity is independent from provider/device realization, Resource identity and Enforcement Attachment identity.
- rendered configuration is a derived representation, not evidence of provider/device application.
- Network Environment Operations owns operation identity/outcome/concurrency/provenance, not desired policy, placement or rendering semantics.
- NEO `OperationTarget` is projected from APR `EnforcementTarget` only at composition; NEO Domain has no APR domain dependency.
- transport/apply acceptance is not semantic verification; `Verified` requires post-check evidence matching the requested artifact digest.
- Unknown apply is fail-closed and is not blindly retried.
- the current deterministic target stub proves execution semantics only; it does not prove Cisco ASA connectivity or compatibility.
- authentication identity does not grant business authority; Authority Management remains the permission owner.
- optional external identity mapping fails closed for `Unmapped | Ambiguous | Unknown` and is not wired as the primary login path.
- future external Authority/ACC/Resource adapters must terminate at context-owned boundaries; external integration remains optional.
- Legacy/MSSQL and real provider/device transport remain non-current product dependencies.
- local deployment hardening does not imply enterprise TLS, external secret management, HA or multi-node topology.

## Current execution

No implementation plan is currently selected after I24 absorption.

I24 Local Deployment and Operational Hardening is complete and absorbed into canonical engineering/runtime truth. Verified outcomes include:
- PostgreSQL network `trust` removed from the supported Compose path and replaced by password/SCRAM host authentication;
- ephemeral per-start database credentials with role rotation that remains compatible with preserved local volumes;
- correct-password and wrong-password executable verification;
- non-mutating repeatable local startup separated from the stateful fresh-product CI journey;
- validated PostgreSQL custom-format logical backup and explicit destructive clean-volume restore;
- Docker proof that durable Access Rule state survives backup -> volume replacement -> restore -> authenticated restart;
- documented forward-upgrade/recovery ordering with migration checksum fail-closed behavior;
- executable proof that migration replay leaves migration journal and durable Rule state unchanged;
- `make dev-status` for Compose/live/ready/PostgreSQL diagnostics;
- low-risk container hardening through non-root backend execution, init/reaping and `no-new-privileges` for NAPMS application containers;
- explicit deferral of enterprise HA/TLS/secret-store topology and performance claims that lack an accepted target.

The final I24 candidate passed core, PostgreSQL persistence, harness, knowledge and Docker local-runtime gates. The Docker gate covered fresh authenticated product execution, preserved-volume restart with credential rotation, logical backup/clean restore, migration replay no-op and operator status diagnostics.

I23 Optional Integration Extension Skeleton remains complete and dormant. I22 Network Environment Operations remains complete with deterministic stub-first execution semantics and no real Cisco transport claim. I21 Configuration Rendering, I20 Desired-vs-Configured Reconciliation and Enforcement Policy Derivation, I19 Network Enforcement Placement, I18 Technical-to-Domain Access Resolution, I17 Technical Access Evidence Core and I16B Connectivity Decision Runtime/Workflow remain complete and absorbed into canonical truth.

The next roadmap increment is I25 — Product Completion, Operator UX and Acceptance. It is not yet selected for execution, so there is no active `PLAN-*.md`.

## Canonical references

Use the smallest relevant set:
- Strategic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- current accepted requirements: `docs/requirements/`;
- target architecture: `docs/architecture/`;
- consequential decisions: `docs/decisions/`;
- runtime contracts: `docs/engineering/`;
- active work only: `docs/plans/active/`.

Completed execution plans and absorbed working packets are intentionally not retained as working-tree archives.
