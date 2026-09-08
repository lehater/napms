# Current implementation state

Status: `I5 PASS — I6 vendor-neutral normalization refinement may begin under the active plan`.

Date: 2026-09-08.

Current execution is owned by `docs/plans/active/README.md`; do not mirror its work-package status here.

## Completed through I5

- I1 authoritative Access Rule materialization core;
- I2 PostgreSQL uniqueness/concurrency/rollback proof;
- I3 authorized Active/Inactive mutation with durable business audit;
- I4 EffectiveWindow mutation/evaluation and authorized effective desired-policy selection;
- accepted ACC ownership of time-qualified ComponentDeployment -> one-or-more stable Resource references;
- Resource Catalogue realization remains owned/resolved by stable Resource reference + logical `asOf`;
- accepted I5 capture-only treatment of complete immutable DCS projection-semantics payload;
- separate `policy_export` application capability owns Export Snapshot composition and its ACC/RC projection ports;
- Access Policy remains owner of Rule/effective-selection semantics and does not absorb catalogue ownership;
- successful snapshot requires an already-authorized effective selection with valid scope, authority provenance and logical `asOf`;
- snapshot assembly rechecks selection scope/effectiveness before any catalogue access;
- ACC responses require exact RuleSemanticIdentity/asOf correlation, non-empty Resource bindings, complete immutable DCS payload and fact/validity/provenance evidence;
- RC responses require exact Resource/asOf correlation, endpoint/address realization and fact/validity/provenance evidence;
- missing/invalid/stale/unknown owner facts fail closed and produce no successful snapshot;
- one incomplete selected Rule prevents snapshot success; selected Rules are never silently dropped;
- repeated Resource references are captured once per snapshot attempt;
- successful snapshot is immutable and preserves Rule/decision/governance/property plus ACC/RC provenance;
- no normalized rows, live post-snapshot lookup, real catalogue adapter or source-specific schema is introduced in I5;
- policy-export application is covered by core no-framework/no-adapter architecture checks;
- final I5 semantic/temporal/provenance/architecture review has no open P0/P1 finding;
- hosted core gate passed on the I5 core candidate.

## I5 result

`PASS`.

The logical Export Snapshot consistency boundary is executable with source-neutral fake ports. Real catalogue integration remains intentionally deferred until a concrete authoritative source/environment is selected.

## Current infrastructure boundary

Existing Access Policy PostgreSQL behavior remains proven through I4.

I5 adds no production infrastructure. Real Authority/Resource Catalogue/Application Communication Catalogue/Connectivity Decision adapters are still not implied.

I6 may transform only a successful immutable Export Snapshot into vendor-neutral normalized rows. It must not perform live catalogue lookups or infer missing DCS/address semantics.
