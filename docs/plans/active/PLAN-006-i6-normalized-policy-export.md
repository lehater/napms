# PLAN-006 — I6 vendor-neutral normalization/export

Status: `active`

## Goal

Transform a successful immutable I5 Export Snapshot into complete vendor-neutral normalized policy rows while preserving Rule/decision/owner-fact provenance and semantics.

I6 stops before vendor/device rendering, configured-state reconciliation and provider/device execution.

## Current stage

Normalization-facing semantic refinement before code.

I5 deliberately preserves DCS projection semantics as a complete immutable ACC-owned payload without interpreting protocol/service/port structure. I6 must define the smallest source-neutral row schema and transformation semantics required by REQ-W1-010/012 and E12/E13 before implementation.

## Inputs

Canonical inputs:

- `docs/requirements/wave1-product-requirements.md` — REQ-W1-010, REQ-W1-012 and REQ-W1-013;
- `docs/requirements/wave1-acceptance-examples.md` — E9, E12 and E13;
- `docs/requirements/wave1-quality-scenarios.md` — QS-05, QS-08 and QS-09;
- `docs/requirements/wave1-semantic-contracts.md` — C8-C10;
- `docs/requirements/wave1-normalized-export-trace.md`;
- `docs/architecture/wave1-domain-message-flows.md` — F3;
- `docs/architecture/wave1-threat-model.md`;
- `docs/decisions/ADR-002-wave1-coherent-export-snapshot.md`;
- current `policy_export` SuccessfulExportSnapshot contract/tests.

## Accepted behavior already fixed

- normalization consumes only one successful immutable Export Snapshot;
- normalization performs no live catalogue/authority lookup;
- one logical `as-of` from the snapshot is preserved on all rows;
- every row remains correlated to its authoritative Rule and Connectivity Decision;
- contributing ACC/RC fact/provenance references remain explainable downstream;
- one Rule may expand to multiple technical rows;
- independently authoritative Rules must not be merged when Rule/decision provenance would be lost;
- normalization must not broaden or narrow selected Rule semantics;
- vendor/device syntax and rendering are outside Wave 1 normalization meaning;
- serialization format is replaceable interface detail, not domain meaning.

## Bounded decisions before code

### D1 — DCS normalization-facing schema

Define the smallest explicit source-neutral semantics required from the I5 DCS projection payload for I6:
- protocol semantics;
- service/port semantics and cardinality;
- any source/destination port distinction actually required;
- representation of ranges/sets where material.

Do not invent a generic service-expression language or vendor syntax.

### D2 — Endpoint/address row semantics

Define how captured source/destination Resource endpoint/address realizations become normalized row fields:
- minimum stable correlation fields retained;
- whether one endpoint with multiple addresses is represented as multiple realizations or one set;
- how source/destination realization combinations expand without semantic broadening.

Do not turn normalized export into a Resource Catalogue schema.

### D3 — Row expansion and provenance

Confirm the executable transform:
- each output row belongs to exactly one authoritative Rule;
- expansion is the semantics-preserving product of captured endpoint realizations and DCS projection alternatives required by the accepted schema;
- no cross-Rule deduplication/merge;
- row provenance retains Rule ID, decision reference, snapshot `asOf`, effective Rule property state and ACC/RC fact references.

This decision is mostly constrained by E12/E13/QS-08; only concrete cardinality details should remain open after D1/D2.

## Work packages

1. Resolve D1-D3 at the requirements/semantic-contract layer before code.
2. Update the normalization/export contract only where needed.
3. Implement pure snapshot -> normalized-row transformation in `policy_export` core.
4. Prove single/multi-endpoint and multi-DCS expansion, exact semantics, deterministic output and provenance preservation.
5. Prove independently authoritative Rules are never provenance-losing merged.
6. Close all P0/P1 semantic/provenance/architecture findings and pass the core gate.
7. Only after core PASS, add serialization adapters if a concrete Wave-1 output format is selected; otherwise keep serialization deferred.
8. Record I6 PASS only when admitted exit criteria are proven.

## Exit criteria

- normalization-facing DCS schema is explicit and source-neutral;
- endpoint/address row semantics are explicit without copying RC ownership;
- transform consumes no live owner source after snapshot assembly;
- every successful snapshot item is represented completely in normalized output;
- expansion preserves exact Rule semantics and deterministic provenance;
- independent Rules retain independent rows/provenance even when technical effects match;
- all rows carry Rule/decision/snapshot-asOf and required ACC/RC provenance;
- no vendor/device rendering semantics leak into normalized meaning;
- no open P0/P1 semantic, provenance or architecture issue;
- I6 result is recorded in canonical engineering state.

## Blockers

D1-D2 are explicit semantic decision gates. No I6 transformation code should be written until they are resolved.

Serialization is additionally deferred until a concrete output format is selected; that does not block core normalization proof.

## Validation

- contract/living-model changes: `make knowledge-check`;
- active-plan/harness changes: `make harness-check`;
- core candidate: `make test`;
- any admitted serialization adapter gets its own tests;
- final repository candidate: `make check`.

## Next

I7 — first real/transitional integrations for a selected controlled environment, preserving anti-corruption translation and source provenance.
