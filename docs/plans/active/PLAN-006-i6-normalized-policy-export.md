# PLAN-006 — I6 vendor-neutral normalization/export

Status: `active`

## Goal

Transform a successful immutable I5 Export Snapshot into complete vendor-neutral normalized policy rows while preserving Rule/decision/owner-fact provenance and semantics.

I6 stops before vendor/device rendering, configured-state reconciliation and provider/device execution.

## Current stage

D1-D3 are accepted and propagated through requirements, C9, normalized-export trace, Ubiquitous Language and F3. Next stage: implement pure I5 snapshot -> normalized rows in `policy_export` core, using a local DCS payload decoder boundary and no live owner lookup.

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

## Refinement findings

### D2 — resolved: atomic endpoint/address realization rows

I5 already captures each Resource realization as one-or-more atomic `EndpointRealization(endpointReference, technicalAddress)` values.

I6 row semantics therefore use one captured source EndpointRealization and one captured destination EndpointRealization per row and retain:
- source/destination ResourceReference;
- source/destination endpointReference;
- source/destination technicalAddress;
- the RC fact/validity/provenance references that justified each side at snapshot as-of.

If a Resource has multiple captured endpoint/address realizations, normalization expands them; it does not invent address-set/group semantics. Resource Catalogue ownership is preserved because the normalized row only carries the captured projection facts.

### D3 — resolved: deterministic semantics-preserving product

For each successful snapshot item, rows are the deterministic product of:
- captured source endpoint/address realizations;
- captured destination endpoint/address realizations;
- normalized DCS traffic alternatives from D1.

Rules:
- every row belongs to exactly one Rule;
- no cross-Rule merge/deduplication;
- range semantics remain ranges rather than enumerating every port;
- deterministic ordering is by Rule ID, source Resource/endpoint/address, destination Resource/endpoint/address, then normalized DCS alternative;
- row provenance retains Rule ID + semantic identity, Connectivity Decision reference, RuleGovernanceScope, current EffectiveWindow/state needed to explain snapshot selection, snapshot as-of/read-authority provenance, ACC fact/validity/provenance and both RC fact/validity/provenance chains.

### D1 — accepted: normalization-facing DCS selector

Known:
- downstream must not infer missing protocol/address/schedule meaning (QS-09);
- DCS provides protocol/service/port semantics;
- one Rule may expand by protocol/port alternatives;
- normalized meaning must be vendor-neutral and exact.

Repository evidence does **not** specify source-vs-destination port shape, Any/not-applicable semantics, canonical protocol identifier form, or whether a service label is traffic semantics or supporting ACC correlation.

#### Accepted option A — bounded source-neutral L3/L4 selector

Decode the I5 DCS payload into one-or-more immutable `DcsTrafficAlternative` values:

```text
DcsTrafficAlternative
    protocol = canonical source-neutral token
    sourcePorts = NotApplicable | Any | inclusive PortRange set
    destinationPorts = NotApplicable | Any | inclusive PortRange set
    serviceReference = optional ACC-owned semantic reference/label
```

`PortRange(first, last)`:
- integer boundaries 0..65535;
- inclusive;
- `first <= last`;
- range sets are sorted, non-overlapping and non-adjacent after canonicalization;
- ranges remain ranges in output; normalization does not enumerate individual ports.

Rules:
- `Any` means unconstrained ports for that side when ports are meaningful;
- `NotApplicable` is distinct from `Any` for protocols without port semantics;
- `serviceReference` is preserved ACC meaning/provenance and does not replace the explicit protocol/port selector;
- protocol tokens are canonical within the export contract but are not vendor/device syntax.

Why recommended:
- enough technical meaning for QS-09/future rendering;
- explicit direction avoids ambiguous generic "ports";
- explicit Any vs NotApplicable avoids semantic guessing;
- bounded to protocol + ports + optional service reference; no generic expression engine.

#### Alternative B — destination ports only

Model `protocol + destination ports + serviceReference`.

Smaller, but repository evidence does not establish that source-port constraints can never be meaningful. Choosing this would permanently narrow the handoff without supporting evidence.

#### Alternative C — protocol-specific union

Model TCP/UDP/ICMP/etc as separate selector variants with protocol-specific fields.

More semantically precise for non-port protocols, but substantially broader than current Wave-1 evidence and would force ICMP/other protocol decisions not required by any accepted example.

Decision: **Option A accepted**.

## Implementation boundary

I5 stores the ACC-owned DCS projection payload as immutable bytes. I6 may introduce a pure/local decoder port:

`DcsProjectionDecoder.decode(payload) -> DcsTrafficAlternative+`

The decoder:
- performs no live catalogue/authority lookup;
- must return one-or-more valid alternatives or fail normalization;
- is a translation/codec boundary, not a semantic owner;
- concrete ACC byte encoding remains deferred until a real source/format is selected.

## Blockers

None for I6 core proof.

Serialization and the concrete DCS payload codec remain deferred until a real output/source format is selected; those deferrals do not block pure core normalization proof.

## Validation

- contract/living-model changes: `make knowledge-check`;
- active-plan/harness changes: `make harness-check`;
- core candidate: `make test`;
- any admitted serialization adapter gets its own tests;
- final repository candidate: `make check`.

## Next

I7 — first real/transitional integrations for a selected controlled environment, preserving anti-corruption translation and source provenance.
