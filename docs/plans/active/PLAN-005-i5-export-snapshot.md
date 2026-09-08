# PLAN-005 — I5 coherent Export Snapshot

Status: `active`

## Goal

Assemble and prove an immutable, complete, logically coherent Export Snapshot for one authorized effective desired-policy selection and one logical `as-of`, using Resource Catalogue and Application Communication Catalogue ports with fakes first.

I5 stops before vendor-neutral row normalization/serialization and before real/transitional catalogue adapters.

## Current stage

Refine the minimum projection-fact and failure contracts handed to application composition by Resource Catalogue and Application Communication Catalogue. Do not implement I5 code until the core can distinguish complete/as-of-valid facts from missing/stale/unknown facts without inventing source-system internals.

## Inputs

Canonical inputs:

- `docs/requirements/wave1-product-requirements.md` — REQ-W1-009, REQ-W1-010, REQ-W1-011 and REQ-W1-013;
- `docs/requirements/wave1-acceptance-examples.md` — E9-E11;
- `docs/requirements/wave1-quality-scenarios.md` — QS-03, QS-04, QS-05 and QS-10;
- `docs/requirements/wave1-semantic-contracts.md` — C6-C9;
- `docs/requirements/wave1-normalized-export-trace.md`;
- `docs/architecture/wave1-domain-message-flows.md` — F3/F4;
- `docs/architecture/wave1-data-ownership.md`;
- `docs/architecture/wave1-threat-model.md`;
- `docs/decisions/ADR-002-wave1-coherent-export-snapshot.md`;
- current I4 effective desired-policy application result and AccessRule model.

## Accepted behavior already fixed

- input Rules are the authorized effective desired-policy subset for one RuleGovernanceScope and one logical `as-of`;
- I5 must not reintroduce Inactive/non-effective Rules;
- for every selected effective Rule, Resource Catalogue supplies the source/destination technical realization required for projection and evidence that it is valid for the logical `as-of`;
- Application Communication Catalogue supplies referenced immutable DCS protocol/service/port semantics and other required projection facts;
- technical realization never changes RuleSemanticIdentity or historical Connectivity Decision;
- successful snapshot must be complete for every selected effective Rule;
- missing/stale/unknown required fact for any selected effective Rule prevents successful snapshot assembly;
- partial facts/diagnostics may be returned only under explicit non-success;
- one snapshot attempt has one logical `as-of`;
- snapshot is immutable per attempt and preserves correlations/provenance to every contributing Rule and owner fact;
- cross-module direct table reads are prohibited;
- source capture/version mechanism is adapter-owned; core consumes semantic as-of validity/provenance rather than source-specific storage mechanics.

## Bounded decisions before code

### D1 — Resource Catalogue projection-fact contract

Define the minimum target-language facts required by I5 without modeling RC internals:
- exact Rule-side correlation;
- technical endpoint/address realization required for later projection;
- validity evidence covering the requested `as-of`;
- opaque source/provenance reference;
- explicit missing/stale/unknown outcomes.

Do not introduce generic CMDB/device inventory concepts.

### D2 — Application Communication Catalogue projection-fact contract

Define the minimum immutable referenced DCS facts required by later normalization:
- exact DCS contract/revision correlation;
- directed protocol/service/port semantics needed for projection;
- provenance/reference;
- temporal validity only where a nonidentity fact genuinely varies;
- explicit missing/invalid/unknown outcomes.

Do not duplicate Application Communication Catalogue aggregate ownership inside Access Policy.

### D3 — Snapshot success/failure shape

Define:
- immutable successful snapshot metadata: selection scope, logical `as-of`, read-authority provenance and complete per-Rule projection facts;
- explicit non-success diagnostics naming affected Rule and missing/invalid fact category;
- no successful snapshot object when any selected effective Rule is incomplete or temporally incoherent.

The snapshot is application-composition truth for one attempt, not a new peer domain aggregate or long-lived business identity.

## Work packages

1. Refine D1-D3 from C7-C9/QS-03-QS-05 and ADR-002.
2. Update semantic/application contracts only where the concrete I5 boundary requires it.
3. Introduce Resource Catalogue and Application Communication Catalogue projection ports with fake adapters.
4. Implement immutable Export Snapshot assembly over an I4 effective-policy selection.
5. Prove complete success, missing/stale/unknown fail-closed behavior, exact Rule/DCS correlation, one logical as-of and full provenance.
6. Close P0/P1 semantic/temporal/provenance/architecture findings and pass the core gate.
7. Only after core PASS, introduce the minimum real/transitional catalogue adapters if a concrete environment/source is selected and recorded; otherwise keep infrastructure integration deferred rather than invent a source.
8. Record I5 PASS only when admitted exit criteria are proven.

## Exit criteria

- RC and ACC projection port semantics are explicit and source-neutral;
- successful snapshot is immutable and carries exactly one logical `as-of`;
- every selected effective Rule has complete RC + ACC facts in a successful snapshot;
- every snapshot item preserves Rule/decision/governance/property provenance plus contributing owner-fact provenance;
- missing/stale/unknown required fact prevents success;
- no selected effective Rule is silently dropped;
- no non-effective Rule is reintroduced;
- no direct cross-module persistence shortcut is used;
- source-specific adapter mechanics do not leak into Domain/Application;
- no normalized vendor-neutral rows are produced yet;
- no open P0/P1 semantic, temporal, provenance or architecture issue;
- I5 result is recorded in canonical engineering state.

## Blockers

D1-D3 require bounded application/semantic refinement before code.

Real catalogue adapter work is additionally blocked until a concrete authoritative source/environment is selected; this does not block fake-port/core I5 proof.

## Validation

- contract/living-model changes: `make knowledge-check`;
- active-plan changes: `make harness-check`;
- core candidate: `make test`;
- any later admitted integration adapter gets its own exact-candidate integration gate;
- final repository candidate: `make check` plus admitted integration gates.

## Next

I6 — vendor-neutral normalization/export from a successful immutable Export Snapshot, preserving independent Rule/decision/source provenance.
