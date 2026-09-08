# Wave-1 G3 — Target + Transition Architecture

Status: `G3 PASS`.

Date: 2026-09-08.

## Selected target

Wave 1 uses a modular application architecture with explicit semantic modules and ports/adapters, initially one primary coherent application/deployment unit unless a concrete integration constraint requires a separate adapter/process.

Key decisions:
- Access Policy is the authoritative consistency boundary for Rule identity/state/idempotency;
- Bounded Contexts remain semantic ownership boundaries and are not mapped one-to-one to services/databases;
- successful normalized export is derived from an immutable logical Export Snapshot for one `asOf`;
- external facts require identity/version/effective-validity provenance sufficient to prove snapshot coherence;
- Connectivity Decision remains an external/deferred semantic port with only exact-subject Allowed|NotAllowed contract;
- Legacy dependencies are isolated behind transition adapters and retirement triggers.

## Canonical G3 artifacts

- `wave1-context-definitions.md`;
- `wave1-domain-message-flows.md`;
- `wave1-architecture-drivers.md`;
- `wave1-architecture-options.md`;
- `wave1-architecture-views.md`;
- `wave1-data-ownership.md`;
- `wave1-threat-model.md`;
- `wave1-transition-architecture.md`;
- `docs/decisions/ADR-001-wave1-modular-application.md`;
- `docs/decisions/ADR-002-wave1-coherent-export-snapshot.md`;
- `docs/decisions/ADR-003-connectivity-decision-port.md`.

## Independent G3 challenge

| Finding | Severity | Result |
|---|---|---|
| Could service-per-BC be inferred from Strategic DDD? | P1 | CLOSED — explicitly rejected; deployment follows drivers |
| Can Rule uniqueness/idempotency be guaranteed? | P1 | CLOSED — Access Policy authoritative consistency boundary |
| Can concurrent catalogue changes yield incoherent successful export? | P1 | CLOSED — logical Export Snapshot + fail-closed assembly |
| Can provenance disappear through normalization? | P1 | CLOSED — snapshot/row correlations required end-to-end |
| Could unknown Decision Domain logic leak into Access Policy? | P1 | CLOSED — external semantic port ADR-003 |
| Could Legacy schemas/request rows become target identity? | P1 | CLOSED — transition adapters/ACL only; target identity remains G2 semantic identity |
| Could direct shared-database access bypass semantic owners? | P1 | CLOSED — physical sharing allowed, cross-module persistence shortcut prohibited |
| Does threat model require additional deployment/security boundary? | P2 | NO current evidence; ports/authority/fail-closed/provenance controls sufficient at G3 |
| Numeric performance/availability envelope absent | P3 | ACCEPTED pending evidence; avoid irreversible scale assumptions; PLAN-028 may measure/revisit |
| Concrete authentication/crypto/retention mechanisms not chosen | P3 | IMPLEMENTATION DETAIL unless later evidence changes architecture |
| Exact external source version/as-of mechanism unknown | P2 | SAFE FOR G3 — semantic requirement fixed by ADR-002; source-specific mechanism belongs PLAN-028/spike if needed |

Open/unaccepted P0/P1 findings: `none`.

## G3 completion check

- architecture traces to G2 functional/quality drivers: PASS;
- credible alternatives compared: PASS;
- BC != service/database preserved: PASS;
- critical semantic interactions explicit: PASS;
- semantic/data ownership explicit: PASS;
- threats assessed and fed back: PASS;
- Target vs Transitional Architecture explicit: PASS;
- Legacy coexistence/cutover/recovery plausible at current evidence depth: PASS;
- hidden product/domain decision introduced: NONE;
- implementation can start inception without using Legacy implementation as target domain meaning: PASS.

## Handoff to G4

PLAN-028 may now define implementation inception: vertical Walking Skeleton, code/module/package structure, concrete interfaces/DTOs, persistence schema/migrations, source-specific adapters, test strategy and technical spikes required to prove uncertain integration mechanisms. It must preserve the G2/G3 semantic invariants and may reopen architecture only on evidence that invalidates a G3 assumption.