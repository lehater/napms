# Technical Access Evidence Core requirements — I17

Status: `accepted I17 WP0 behavioral baseline`.

Date: 2026-09-09.

## Purpose

Define the first executable product behavior for Technical Access Evidence without choosing vendor syntax, device APIs, deployment topology, technical-to-domain resolution or reconciliation.

## REQ-TAE-001 — Own source-qualified technical evidence

TAE shall own durable immutable Technical Access Evidence Sets containing normalized technical access entries qualified by:
- evidence kind;
- evidence source;
- source scope;
- source capture;
- source-time statement;
- NAPMS recording time.

Recording evidence shall not assert that the represented access is required, authorized, desired or domain-valid.

## REQ-TAE-002 — Support the accepted evidence kinds

The first vocabulary is exactly:
- `Configured`;
- `TrafficDerived`;
- `Imported`.

Configured evidence reports configured material from a source.
TrafficDerived evidence is derived from observed communication.
Imported evidence comes from a file/external artifact.

Kind alone shall not imply completeness, freshness or authorization.

## REQ-TAE-003 — Stable set identity and capture idempotency

Each Evidence Set has a generated stable `EvidenceSetId`.

One semantic capture is identified by:

```text
EvidenceSourceReference + SourceCaptureReference
```

Retrying the same capture with identical **source-qualified capture payload** returns the existing set.

Payload equality includes kind, source scope, Evidence Time and a multiset of normalized source entry facts. Incidental parser/list order is ignored; duplicate multiplicity and factual sourcePosition remain significant.

It excludes generated Set/Entry IDs and the retry attempt's recording time.

The existing set keeps its original IDs and original `RecordedAt`.

The same capture identity with different source-qualified payload is a conflict and shall not overwrite history.

## REQ-TAE-004 — Preserve duplicate source entries

Each Technical Access Entry has a generated stable `EvidenceEntryId`.

TAE shall not deduplicate entries by normalized predicate content because duplicate rules/records can be factual source evidence.

An optional source-native entry reference may be preserved as provenance.

## REQ-TAE-005 — Keep source scope distinct from business/enforcement scope

Each Evidence Set stores a mandatory opaque `SourceScopeReference`.

The reference describes the source collection boundary only.

It shall not automatically be interpreted as:
- Authority Management Responsibility Scope;
- Resource Catalogue ownership scope;
- Network Enforcement Placement Logical Firewall;
- Access Policy governance scope.

## REQ-TAE-006 — Keep source time distinct from recording time

Every Evidence Set stores:
- mandatory offset-aware `RecordedAt`;
- `EvidenceTime = Unknown | Instant | Window`.

Known times are offset-aware and windows are valid half-open/ordered observation ranges with `start < end`.

Unknown source time shall remain unknown. `RecordedAt` shall not be substituted as source-effective/observation time.

## REQ-TAE-007 — Normalize the technical communication region

Every entry shall express a normalized Technical Access Predicate containing:
- source address constraint;
- destination address constraint;
- `ProtocolSelector = Any | IpProtocolNumber(0..255)`;
- source port constraint;
- destination port constraint.

Address constraints support Any or canonical IP ranges.

Port constraints distinguish `NotApplicable`, `Any` and canonical ranges.

Source/vendor protocol names shall be normalized to exact IP protocol numbers. A multi-protocol source expression may be expanded into multiple entries only when that preserves the represented region exactly.

When `ProtocolSelector = Any`, both source and destination port constraints shall be `Any`; `Any + Ranges` and `Any + NotApplicable` are invalid because they do not define one unambiguous cross-protocol technical region.

For one exact protocol number, `NotApplicable | Any | Ranges` may be used only when faithful to that protocol/source fact.

Source-native service/object names are provenance, not predicate semantics in the first slice.

Normalization shall not broaden or narrow represented source semantics.

## REQ-TAE-008 — Store action/order only when factual

An entry may preserve:
- normalized `Permit | Block` action;
- source position/order.

These facts are optional and must be absent when the source cannot support a faithful mapping.

Observed traffic shall not manufacture a configured Permit/Block action merely because communication occurred.

## REQ-TAE-009 — Reject silent partial normalization

A successful Evidence Set represents the complete set of entries accepted from that capture under the first I17 contract.

If any source item cannot be normalized faithfully, the capture shall not be reported as a successfully recorded complete Evidence Set.

Future explicit partial-capture semantics require an accepted coverage model.

## REQ-TAE-010 — Allow empty evidence without claiming absence

A source capture that produces zero normalized entries may be persisted as an empty Evidence Set.

Without an accepted coverage/completeness claim, empty evidence shall not mean:
- no access is configured;
- no traffic occurred outside the observed boundary;
- desired policy is satisfied.

## REQ-TAE-011 — Do not invent current/fresh evidence

I17 shall not expose a domain operation that automatically selects one globally current/fresh Evidence Set.

Freshness thresholds and winner selection remain undefined until a source/consumer contract requires them.

Queries may filter evidence by source, source scope, kind and recorded/source time without converting recency into truth.

## REQ-TAE-012 — Defer universal freshness/coverage/confidence vocabulary

The first slice shall not invent:
- `Fresh | Stale`;
- `Complete | Partial`;
- a global confidence score.

These concepts may be added only with an accepted source/consumer meaning and revisit trigger.

Source Scope is provenance, not a completeness claim.

## REQ-TAE-013 — Preserve traceable provenance

Every Evidence Set shall preserve source/capture/scope/kind/time/recorded-at provenance.

Every entry shall preserve its generated identity and optional native source entry reference/position.

Raw source payload is not mandatory TAE domain state, but the concrete adapter must preserve enough source qualification/reference for traceability.

## REQ-TAE-014 — Query durable evidence without realization semantics

The first read capability shall support:
- get by Evidence Set ID;
- find by source + capture reference;
- paged listing/filtering of Evidence Sets.

Reads shall return evidence facts only.

They shall not:
- map predicates to ACC/RC domain interactions;
- select enforcement placement;
- compute desired-vs-configured status;
- render vendor configuration.

## REQ-TAE-015 — Persistence uncertainty is explicit

Recording shall not report success unless the authoritative immutable set outcome is established.

A commit outcome that cannot be established shall be returned as explicit uncertainty.

A retry must use source + capture identity so it can resolve the authoritative result without creating a silent alternate version.

## REQ-TAE-016 — Keep human authority/workflow out until required

I17 core does not require a new human-facing ingest/read workspace or new Authority Management actions.

The first source path may be a trusted outer adapter/composition path.

Human/operator actions require a separate accepted workflow and authority contract.

## Trace

Tactical semantics:
- `docs/domain/technical-access-evidence/tactical-model.md`.

Executable examples:
- `docs/requirements/technical-access-evidence-acceptance-examples.md`.

Architecture:
- `docs/architecture/technical-access-evidence-boundary.md`.
