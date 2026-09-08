# Wave-1 first implementation backlog — PLAN-028 WP-07

Status: `accepted ordered implementation backlog — greenfield execution through I8 decision gate`.

Date: 2026-09-08.

## Mandatory staging rule

Implementation proceeds inside-out. Establish and test Domain + Application + Ports before infrastructure. Infrastructure adapts to accepted core semantics and does not redefine them.

## Ordered vertical increments

### I1 — Domain + Application executable core
Build the target Access Policy domain/application shape and consuming ports using fakes/in-memory adapters. Prove the accepted behavior matrix and infrastructure independence.

### I2 — PostgreSQL persistence proof
Implement the relational AccessRuleRepository/UoW, schema/migrations and concurrency/rollback proof against PostgreSQL without changing Rule semantics.

### I3 — Operational state mutation
Add authorized Active<->Inactive behavior, audit/provenance and persistence adaptation.

### I4 — Effective desired-policy selection
Add EffectiveWindow semantics plus authorized logical-as-of desired-policy selection.

### I5 — Export Snapshot
Assemble an immutable coherent Export Snapshot from Access Policy selection plus source-neutral ACC/RC projection ports; fail closed on incomplete/correlated facts.

### I6 — Vendor-neutral normalization/export core
Transform a successful snapshot into deterministic vendor-neutral normalized rows with complete Rule/decision/source provenance and no provenance-losing cross-Rule merge.

### I7 — Greenfield PostgreSQL owned-module integration
Implement Authority Management, Application Communication Catalogue and Resource Catalogue as first-class NAPMS modules with module-owned PostgreSQL schemas/repositories. Add the strict internal DCS codec, typed local-dev composition and an end-to-end proposal -> normalized-export PostgreSQL proof. Keep Connectivity Decision behind its accepted port. No Legacy/MSSQL/transitional adapter is part of I7.

### I8 — First concrete consumer/runtime boundary
Select the first actual consumer and only then implement the minimum invocation/handoff adapter required by that consumer. The boundary must add accepted structured logging/correlation and startup/operability behavior without redefining core semantics. HTTP, CLI and public JSON/CSV/XLSX are choices, not defaults.

Rendering, configured-state reconciliation and device/provider execution remain deferred by the Wave-1 deferral register.

## Testing rule for every increment

For new domain/application behavior:

`accepted behavior -> Domain/Application implementation -> exhaustive relevant core tests -> core gate -> infrastructure adapter/integration tests`.

Do not use a database, framework or external system to compensate for an unclear domain/application model.

## Reopen triggers

Return to the owning requirement/architecture decision if implementation evidence invalidates a material assumption. Do not silently change domain semantics in infrastructure.
