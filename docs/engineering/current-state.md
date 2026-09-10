# Current implementation state

Status: `I25 Product Completion, Operator UX and Acceptance accepted and implemented for the supported local target`.

Date: 2026-09-10.

Current execution pointer: `docs/plans/active/README.md`; no active implementation plan remains after I25 retirement.

This file is a capability snapshot, not an increment-by-increment changelog. Detailed history lives in Git; roadmap status lives in `docs/engineering/post-wave1-product-completion-roadmap.md`.

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
| Scoped Connectivity Inventory | accepted owner-preserving application composition | framework-free read composition with module-owned PostgreSQL adapters, including durable coarse Decision enrichment; no independent persistence | primary post-login Connectivity workspace |
| Technical Access Evidence | accepted Tactical DDD | framework-free Domain/Application/Ports + TAE-owned PostgreSQL + strict local JSON import adapter + dedicated composition record/readback; no public TAE transport | consumed by realization composition; no generic CRUD workspace |
| Network Enforcement Placement | accepted I19 Tactical DDD | framework-free Domain/Application/Ports + strict knowledge import + NEP-owned PostgreSQL immutable captures + time-qualified placement selection | consumed by Realization projection |
| Access Policy Realization | accepted I18 resolution + I20 derivation/reconciliation + I21 rendering | framework-free Domain/Application/Ports + owner-preserving AP/RC/ACC/NEP/TAE adapters + PostgreSQL-backed owner composition; derived on demand, no APR persistence; Cisco ASA renderer outer adapter with semantic equivalence proof | `Realization` read-only operator workspace via owner-preserving projection |
| Network Environment Operations | accepted I22 stub-first Tactical DDD | framework-free Domain/Application/consumer-owned ports + deterministic in-process target stub + in-memory operation repository; no real Cisco transport or crash-durable audit claim | operation stage is shown by Realization only when an actual operation result is supplied; otherwise `NotAvailable` |
| Network Operator Realization View | accepted I25 read composition | authority-first framework-free projection + PostgreSQL owner-preserving composition + authenticated HTTP router; no independent persistence | Realization workspace with `Available | NotAvailable | Unknown` stage availability and Rule navigation |
| End-to-end product acceptance | accepted I25 evidence | PostgreSQL-backed acceptance test proves Requirement -> Decision -> Rule -> NEP/TAE/APR -> render -> deterministic NEO -> `Verified` continuity | explainability navigation `Realization -> Rule -> Decision -> Connectivity Requirement` |
| Optional external identity/source extension | accepted I23 dormant seam | source-neutral `VerifiedExternalIdentity` + `ActorIdentityResolver` deterministic mapping proof; no runtime wiring, provider transport, external source synchronization or persistence requirement | none |
| Local deployment and operations | accepted I24/I25 local target | password/SCRAM PostgreSQL, repeatable non-mutating startup, logical backup/clean restore, forward migration procedure, structured diagnostics, low-risk container hardening and locked Web dependency graph | Make targets, local product operator runbook and Web UI |

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

Local PostgreSQL recovery uses validated custom-format logical backups. Clean restore is explicitly destructive, requires confirmation, restores into a new local volume, then re-enters the normal migration/startup path. Forward upgrade requires a pre-upgrade backup; arbitrary reverse-migration/downgrade compatibility is not claimed.

`make dev-status` is the supported local diagnostic path: Compose state plus public liveness/readiness and a PostgreSQL query probe. Structured application logs remain the detailed diagnostic source. A dedicated metrics backend is not required by the current local target.

Backend-derived and Web Compose services use init/reaping plus `no-new-privileges`; the backend runtime remains non-root. PostgreSQL retains the official image privilege/entrypoint model.

Local username/password authentication is the primary supported authentication path. Local Authority/ACC/Resource state remains the supported current source of truth. No external IdP, directory, CMDB, catalogue or MSSQL dependency is required for normal operation.

## I25 product-completion boundary

The supported local product has one executable full-chain acceptance proof:

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

This acceptance proof uses existing owner APIs/repositories and the accepted deterministic NEO target stub. It does not create copied cross-context authoritative state and does not claim real Cisco/device transport compatibility.

The interactive operator surface is intentionally narrower than the acceptance fixture universe. `Realization` composes current owner data and preserves stage availability as `Available | NotAvailable | Unknown`. If the running product has no selected configured-evidence/managed-scope input or no actual NEO operation result, reconciliation/operation remain `NotAvailable`; desired/rendered state is never reclassified as configured, applied or verified.

Cross-chain explainability is navigable through existing owner pages:

```text
Realization -> Access Rule -> Connectivity Decision -> Connectivity Requirement
```

Each destination performs its own read authorization. The Realization projection owns orchestration/presentation only.

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
- the current deterministic target stub proves execution semantics only; it does not prove Cisco connectivity or compatibility.
- Network Operator Realization View is read-only and owns no peer business truth.
- missing configured-evidence/managed-scope input or NEO result is `NotAvailable`, never inferred success.
- authentication identity does not grant business authority; Authority Management remains the permission owner.
- optional external identity mapping fails closed for `Unmapped | Ambiguous | Unknown` and is not wired as the primary login path.
- future external Authority/ACC/Resource adapters must terminate at context-owned boundaries; external integration remains optional.
- Legacy/MSSQL and real provider/device transport remain non-current product dependencies.
- local deployment hardening does not imply enterprise TLS, external secret management, HA or multi-node topology.
- Web dependency changes must update the repository lockfile with the package manager; supported CI/Docker builds use `npm ci`.

## Current execution

No implementation plan is selected after I25 absorption.

I25 Product Completion, Operator UX and Acceptance is complete. Durable outcomes include:
- a PostgreSQL-backed full-chain acceptance proof from Requirement through deterministic controlled execution and `Verified` post-state;
- an accepted owner-preserving Network Operator Realization View requirement/architecture boundary;
- dedicated `ReadNetworkOperatorRealization` authority admission, PostgreSQL composition and authenticated HTTP transport;
- one bounded read-only Realization Web workspace with explicit availability rather than inferred state;
- navigable provenance from Realization to Rule, Decision and Connectivity Requirement owner pages;
- no new generic IAM role model, copied authoritative cross-context persistence, speculative dashboard, global search, bulk mutation or extra export surface;
- a package-manager-generated Web lockfile with `npm ci` in CI and Docker build paths;
- `docs/engineering/local-product-operator-runbook.md` for supported startup/status/product/recovery/upgrade workflow and explicit exclusions.

The final I25 absorption candidate passed core, PostgreSQL persistence, Web, harness, knowledge and Docker local-runtime gates. Docker coverage includes fresh authenticated product execution, preserved-volume restart with credential rotation, logical backup/clean restore, migration replay no-op and operator status diagnostics.

I24 Local Deployment and Operational Hardening, I23 Optional Integration Extension Skeleton, I22 Network Environment Operations, I21 Configuration Rendering, I20 Reconciliation, I19 Network Enforcement Placement, I18 Technical-to-Domain Access Resolution, I17 Technical Access Evidence, I16B Connectivity Decision Runtime/Workflow and earlier increments remain complete and absorbed.

## Canonical references

Use the smallest relevant set:
- Strategic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- current accepted requirements: `docs/requirements/`;
- target architecture: `docs/architecture/`;
- consequential decisions: `docs/decisions/`;
- runtime/product state: `docs/engineering/`;
- local operator procedure: `docs/engineering/local-product-operator-runbook.md`;
- active work only: `docs/plans/active/`.

Completed execution plans and absorbed working packets are intentionally not retained as working-tree archives.