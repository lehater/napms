# Wave-1 first implementation backlog — PLAN-028 WP-07

Status: `accepted ordered implementation backlog — domain/application-first refinement`.

Date: 2026-09-08.

## Mandatory staging rule

Implementation proceeds inside-out. First establish and exhaustively test Domain + Application + Ports using in-memory/fake adapters. **Real infrastructure is prohibited until the I1 core gate passes.** Infrastructure must adapt to accepted core semantics, not shape them prematurely.

## Ordered vertical increments

### I1 — Domain + Application executable core
Build the target package/module structure, Access Policy Tactical DDD model, application use case and real port contracts. Implement only in-memory/fake adapters for repository, authority, communication catalogue and connectivity decision. No ORM, SQL schema/migrations, real DB, external SDK/API or required HTTP adapter.

Test the full accepted first-slice behavior matrix: Allowed/new, Allowed/retry, NotAllowed, subject mismatch, authority permitted/denied/unknown, interaction valid/invalid/unknown, dependency failure/unknown, identity immutability and provenance/no-forbidden-side-effects.

**I1 exit gate:** all Domain/Application/port-contract tests green; architecture/import tests prove core independence from infrastructure/frameworks; no open/unaccepted P0/P1 model/application issue. Production concurrency is explicitly not claimed by in-memory tests.

### I2 — Infrastructure proof for the accepted core
Only after I1 gate: implement HTTP adapter as needed, real relational AccessRuleRepository/UoW, schema/migrations and persistence integration tests. Prove the already accepted uniqueness/idempotency requirement under retries/concurrent transactions against the selected production-grade database mechanism. Infrastructure must not redefine Rule semantics.

### I3 — Operational state mutation
Add authorized Active<->Inactive behavior first through Domain/Application/ports/tests; add infrastructure adaptation only after the core behavior passes. Preserve Rule identity/decision correlation and audit/provenance.

### I4 — Effective desired-policy selection
Add supported declarative effective conditions and authorized selection/read model for a logical as-of. Keep exact property representation no broader than accepted requirements; test core semantics before infrastructure concerns.

### I5 — Export Snapshot
Introduce Resource Catalogue and Application Communication Catalogue projection ports with fakes first; assemble/test immutable coherent logical Export Snapshot and fail-closed behavior. Only then implement real/transitional catalogue adapters needed by the selected environment.

### I6 — Vendor-neutral normalization/export
Transform successful snapshot to normalized rows with complete Rule/decision/source provenance; prove expansion and no provenance-losing merge; add transport/serialization adapters after core transformation semantics pass.

### I7 — First real/transitional integrations
Replace selected fake ports with the minimum real/manual/Legacy/enterprise adapters required for a controlled scope; preserve anti-corruption translation and source provenance.

### I8 — Controlled coexistence/cutover proof
Deploy selected scope, observe success/failure, exercise rollback routing and document adapter retirement evidence. Still no rendering/device mutation.

## Testing rule for every increment

For any new domain/application behavior:

`accepted behavior -> Domain/Application implementation -> exhaustive relevant core tests -> core gate -> infrastructure adapter/integration tests`.

Do not use a database, framework or external system to compensate for an unclear domain/application model. Technical integration tests prove adapter guarantees in addition to, not instead of, core tests.

## Reopen triggers

Return to the owning G2/G3 decision if implementation evidence invalidates a material semantic/architecture assumption, e.g. a required external source cannot support any credible version/effective-time capture for coherent export. Do not silently change domain semantics in infrastructure.