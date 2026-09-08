# Current implementation state

Status: `I7 PASS — I8 first consumer/runtime boundary decision may begin under the active plan`.

Date: 2026-09-08.

Current execution is owned by `docs/plans/active/README.md`; do not mirror its work-package status here.

## Completed through I7

- I1 authoritative Access Rule materialization core;
- I2 PostgreSQL uniqueness/concurrency/rollback proof;
- I3 authorized Active/Inactive mutation with durable business audit;
- I4 EffectiveWindow mutation/evaluation and authorized effective desired-policy selection;
- I5 coherent immutable Export Snapshot;
- I6 vendor-neutral normalized policy transformation;
- first-class greenfield Authority Management bounded context with exact actor/action/scope/effective-validity semantics;
- first-class greenfield Application Communication Catalogue bounded context owning ComponentDeployment identity, immutable DCS revision and time-qualified Deployment -> ResourceReference bindings;
- first-class greenfield Resource Catalogue bounded context owning Resource realization versions and endpoint/address facts;
- PostgreSQL-only persistence for all implemented bounded contexts, with separate module-owned schemas/migrations/repositories;
- architecture guard forbidding cross-module PostgreSQL schema access;
- bounded-context core independence guard: Domain/Application of one bounded context cannot import another bounded context core;
- ACC identity translated at consumer adapter boundaries rather than importing Access Policy domain identity into ACC core;
- ACC projection evidence preserves attributable DCS/binding fact, validity and provenance references rather than irreversible provenance hashes;
- explicit half-open `valid_from <= asOf < valid_to` semantics for Authority, ACC bindings and RC realization facts;
- fail-closed ambiguity: overlapping Authority assignments, ACC versions or RC realization versions never become permission/success;
- strict versioned internal greenfield DCS JSON codec preserving accepted I6 protocol/source-port/destination-port/service semantics;
- one typed local-dev application configuration with PostgreSQL DSN validation and no secret leakage through repr;
- explicit greenfield PostgreSQL composition root with separate owner connections; ACC/RC snapshot reads use `REPEATABLE READ READ ONLY`;
- direct end-to-end integration proof:
  proposal -> Authority -> ACC -> ConnectivityDecisionPort -> Access Policy/PostgreSQL -> authorized effective selection -> ACC/RC snapshot -> normalized export;
- end-to-end degraded paths proven for denied/ambiguous authority, missing/mismatched DCS, decision subject mismatch, missing/stale RC facts and denied policy read;
- Connectivity Decision remains intentionally behind its accepted semantic port; no internal Decision Domain model was invented;
- no HTTP, CLI, public serializer, vendor rendering/device execution, Legacy or MSSQL dependency was introduced;
- final I7 semantic/provenance/architecture review has no open P0/P1 finding;
- hosted core and PostgreSQL gates passed after the final I7 P1 corrections.

## I7 result

`PASS` for the explicitly bounded `local-dev` greenfield PostgreSQL environment.

I7 proves that the accepted Wave-1 semantics can run end-to-end through owned NAPMS modules and PostgreSQL adapters without cross-owner persistence shortcuts or Legacy dependencies. It does **not** claim a public runtime/API, production deployment topology, public export serialization, durable Connectivity Decision internals or device enforcement.

## Current infrastructure boundary

Implemented:
- Access Policy PostgreSQL;
- Authority Management PostgreSQL;
- Application Communication Catalogue PostgreSQL;
- Resource Catalogue PostgreSQL;
- strict internal DCS projection codec;
- typed local-dev configuration and explicit composition root.

Still deferred:
- first real consumer/invocation surface;
- public normalized-export handoff/serialization;
- runtime structured logging/correlation implementation required by the accepted observability policy;
- durable Connectivity Decision Domain internals;
- rendering/configured-state reconciliation/device execution according to the Wave-1 deferral register.
