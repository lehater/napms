# Wave-1 quality scenarios — PLAN-026 WP-05 QAW-lite

Status: `accepted G2 architecture-driver baseline`.

Date: 2026-09-08.

## Principle

Only quality attributes supported by selected Wave-1 behavior are promoted to architecture drivers. No arbitrary latency, throughput, availability or scale numbers are invented where repository evidence/product decisions do not establish them.

Priority:
- P1 — architecture-significant for Wave 1;
- P2 — important constraint/quality, should be demonstrable;
- P3 — ordinary engineering concern; no evidence yet that it should drive architecture choice.

## QS-01 — Semantic correctness of materialization

Priority: `P1`.

Source/stimulus: same valid `Allowed` proposal is materialized once or repeatedly, including concurrent/retried invocation.

Environment: normal operation.

Response:
- exactly one authoritative Rule exists for the semantic identity;
- every successful resolution returns the same Rule ID;
- first materialization is `Active`;
- no `NotAllowed` proposal materializes a Rule.

Measure: invariant holds for all acceptance tests; duplicate authoritative Rule count = 0.

Architecture consequence: solution must support authoritative uniqueness/idempotency without relying on UI-only prevention.

## QS-02 — No semantic drift across identity/projection boundaries

Priority: `P1`.

Stimulus: decision-relevant DCS/source/destination identity changes, or technical realization changes independently.

Response:
- identity-defining change never mutates an existing Rule subject/decision into new meaning;
- technical-realization-only change preserves Rule identity and is reflected by later projection.

Measure: all E5/E6 mutation cases preserve the decision matrix in `wave1-d1-decision-packets.md`; zero silent identity substitution.

Architecture consequence: immutable semantic identity and mutable realization must be representable distinctly.

## QS-03 — Coherent export under changing catalogue data

Priority: `P1`.

Stimulus: Resource Catalogue / Application Communication Catalogue facts change while an export is being evaluated.

Environment: concurrent domain/catalogue updates.

Response: successful export represents one logical `as-of`; every contributing fact is valid for that logical evaluation point or carries equivalent temporal evidence sufficient to prove coherence.

Measure: no successful export contains rows whose contributing facts cannot be shown coherent for its declared `as-of`.

Architecture consequence: candidate architecture must provide a credible consistency/temporal-read strategy; exact mechanism is not prescribed at G2.

## QS-04 — Fail closed on incomplete effective-policy projection

Priority: `P1`.

Stimulus: one selected effective Rule lacks required current/temporally valid technical realization.

Response: operation does not emit a downstream-ready successful Normalized Policy Export; diagnostics may identify unresolved Rule/fact and may contain explicitly partial rows.

Measure: successful artifact completeness = 100% of selected effective Rules; otherwise result status is non-successful/diagnostic.

Architecture consequence: partial failure and completeness must be explicit, not silently best-effort.

## QS-05 — End-to-end explainability

Priority: `P1`.

Stimulus: operator/auditor selects any normalized row from a produced export.

Response: product can correlate the row back through Rule ID, semantic identity, decision correlation, relevant operational state/properties, source realization/DCS facts, export `as-of`, and proposal/authority provenance required by the semantic contract.

Measure: every successful export row has a complete business-provenance chain; orphan normalized rows = 0.

Architecture consequence: provenance cannot be discarded at integration/projection boundaries.

## QS-06 — Authority is evaluated at action scope/time

Priority: `P2`.

Stimulus: actor attempts proposal, Rule state mutation, or read/export while authority assignments vary by scope/effective time.

Response: action succeeds only when current/effective Authority Management facts permit that action for that scope/time; historical authority facts remain explainable for prior actions.

Measure: unauthorized action acceptance = 0 in negative test set; prior provenance is not rewritten by later assignment changes.

Architecture consequence: authority must be consumed as domain input rather than hard-wired into static role assumptions.

## QS-07 — Auditability of operational state

Priority: `P2`.

Stimulus: Rule changes `Active <-> Inactive`.

Response: transition is attributable and temporally explainable; Rule identity and prior Connectivity Decision remain stable.

Measure: every accepted state transition has the minimum business audit/provenance required to reconstruct who/when/what transition occurred; unaudited accepted transitions = 0.

Architecture consequence: state mutation cannot be implemented as untraceable overwrite.

## QS-08 — Normalization preserves independent business meaning

Priority: `P2`.

Stimulus: one Rule expands to multiple technical rows or multiple Rules resolve to technically equivalent traffic effects.

Response: expansion is semantics-preserving; independent Rules are not merged when Rule/decision provenance would be lost.

Measure: normalized traffic set is equivalent to selected effective Rule semantics and every row retains required Rule/source correlation.

Architecture consequence: normalization/optimization requires provenance-aware semantics, not only technical tuple deduplication.

## QS-09 — Interoperable vendor-neutral handoff

Priority: `P2`.

Stimulus: a downstream human consumer or later renderer consumes a successful Normalized Policy Export.

Response: the consumer has sufficient technical semantics and provenance to act/render without querying Legacy implementation meaning or inferring missing protocol/address/schedule semantics.

Measure: all fields listed in REQ-W1-010 are present/derivable from the export contract; vendor/device syntax is absent from the domain meaning.

Architecture consequence: normalized handoff is a stable semantic boundary, serialization remains replaceable.

## QS-10 — Operability of degraded export

Priority: `P2`.

Stimulus: export cannot complete because one or more effective Rules have unresolved/stale required facts.

Response: diagnostics identify affected Rule(s), missing/invalid fact category and export `as-of` sufficiently for an operator to understand why no successful artifact was produced.

Measure: degraded test cases return explicit attributable diagnostics rather than empty/silent failure or misleading success.

## QS-11 — Performance / scale

Priority: `P3 pending evidence`.

Repository evidence does not currently establish target Rule counts, export row counts, concurrency, response-time SLA, throughput or availability objective for Wave 1. Therefore G2 does not invent numeric performance/availability requirements.

Architecture implication: PLAN-027 must avoid irreversible choices that assume tiny scale, but performance/scale does not outrank the P1 semantic correctness/coherence/provenance drivers until a real workload envelope is supplied or measured.

Revisit trigger: accepted workload/SLA data, production migration profile or architecture option whose feasibility materially depends on a numeric envelope.

## QS-12 — Execution reliability/device availability

Priority: `out of Wave 1`.

Retry, rollback, partial device mutation, device availability and network execution recovery belong to deferred Network Environment Operations/J9 and must not drive Wave-1 G2 architecture.

## WP-05 result

Wave-1 architecture drivers are, in order:

1. authoritative semantic correctness/idempotency;
2. coherent temporal export and fail-closed completeness;
3. end-to-end provenance/explainability;
4. authority/audit correctness;
5. semantics-preserving interoperable normalization.

No unsupported performance/SLA numbers are promoted to product truth.
