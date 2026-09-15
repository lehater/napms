# Technical Access Evidence core requirements

## Purpose

Define source-qualified durable technical-access evidence without choosing vendor syntax, device APIs, deployment topology or downstream policy-realization semantics.

## Evidence ownership

TAE owns immutable Technical Access Evidence Sets containing normalized entries qualified by evidence kind, source, source scope, source capture, source-time statement and NAPMS recording time.

Recording evidence never asserts that represented access is required, authorized, desired or domain-valid.

## Evidence kinds

The current source-neutral vocabulary is:

```text
Configured
TrafficDerived
Imported
```

Kind describes evidence provenance/derivation. It does not imply completeness, freshness or authorization.

## Identity and idempotency

Each Evidence Set has a generated stable `EvidenceSetId`.

Semantic capture identity is:

```text
EvidenceSourceReference + SourceCaptureReference
```

Retrying the same capture with identical source-qualified capture payload returns the existing set unchanged. Payload equality includes kind, source scope, EvidenceTime and a multiset of normalized source entry facts; incidental parser/list order is ignored while duplicate multiplicity and factual sourcePosition remain significant.

Generated Set/Entry IDs and retry-attempt recording time do not participate in payload equality. The same capture identity with a different source-qualified payload is a conflict and never overwrites the existing immutable set.

Each entry has a generated stable `EvidenceEntryId`. TAE does not deduplicate entries by normalized predicate content because duplicate source rules/records may themselves be factual evidence.

## Source qualification

Every Evidence Set carries a mandatory opaque `SourceScopeReference` describing the source collection boundary. It is not automatically an Authority Management Responsibility Scope, RC ownership scope, NEP target identity or Access Policy governance scope.

An optional source-native entry reference may be preserved for traceability.

## Time semantics

Every Evidence Set stores:

```text
RecordedAt
EvidenceTime = Unknown | Instant | Window
```

Known instants are offset-aware. A Window is ordered and half-open with `start < end`. Unknown source time remains unknown; `RecordedAt` is never substituted as source-effective or observation time.

## Normalized predicate

Every entry expresses:

```text
source address constraint
destination address constraint
ProtocolSelector = Any | IpProtocolNumber(0..255)
source port constraint
destination port constraint
```

Address constraints support `Any` or canonical IP ranges. Port constraints distinguish `NotApplicable`, `Any` and canonical ranges.

Source/vendor protocol names normalize to exact IP protocol numbers. Multi-protocol source expressions may expand into several entries only when expansion preserves the represented technical region exactly.

When `ProtocolSelector = Any`, both source and destination port constraints are `Any`. For one exact protocol number, `NotApplicable | Any | Ranges` is used only when faithful to that source fact.

Source-native service/object names remain provenance when they have no accepted source-neutral meaning. Normalization never broadens or narrows represented source semantics.

## Optional action and order

An entry may preserve normalized `Permit | Block` and source position/order only when the source fact supports them faithfully. TrafficDerived evidence does not manufacture Permit/Block merely because communication occurred.

## Complete capture rule

A successfully recorded Evidence Set contains the complete set of entries accepted from that semantic capture under the current TAE contract.

If any source item cannot be normalized faithfully, the capture is not reported as successfully recorded. The current contract has no partial-success capture semantics.

A capture that produces zero normalized entries may be persisted as an empty Evidence Set. Without an explicit source/consumer completeness contract, empty evidence does not mean that no access is configured, no traffic occurred outside the observed boundary, or desired policy is satisfied.

## Freshness, coverage and confidence

TAE does not select one globally current/fresh Evidence Set and defines no universal `Fresh | Stale`, `Complete | Partial` or confidence scale.

Queries may filter by source, source scope, kind and supported recorded/source-time ranges without turning recency into truth. Currentness, completeness and confidence exist only where a concrete source/consumer contract defines their meaning.

`SourceScopeReference` is provenance, not a completeness claim.

## Provenance

Every Evidence Set preserves source, capture, scope, kind, source-time and recording-time provenance. Every entry preserves generated identity plus factual optional native source reference/position.

Raw source payload is not mandatory TAE state, but a concrete producer/integration must retain enough source qualification or reference for traceability.

## Queries

TAE supports:

```text
GetTechnicalAccessEvidenceSet(evidenceSetId)
FindTechnicalAccessEvidenceSet(source, captureReference)
ListTechnicalAccessEvidenceSets(filters, page, pageSize)
```

Reads expose evidence facts only. They do not assign business meaning, select enforcement targets, compute required-vs-configured realization, design policy changes or render provider configuration.

## Persistence uncertainty

Recording reports success only when the authoritative immutable set outcome is established. Unknown commit outcome remains explicit uncertainty. Retry uses semantic capture identity to resolve authoritative state without creating an alternate version.

## Human workflow boundary

TAE core requires no human-facing ingest/read workflow merely to accept evidence from a trusted integration. Any operator action that is exposed to users requires its own accepted workflow and Authority Management admission.

## Current references

- Tactical semantics: `docs/domain/technical-access-evidence/tactical-model.md`.
- Executable requirements examples: `docs/requirements/technical-access-evidence-acceptance-examples.md`.
- Architecture boundary: `docs/architecture/technical-access-evidence-boundary.md`.
