# Technical-to-Domain Access Resolution acceptance examples — I18

Status: `accepted I18 WP0 specification-by-example baseline`.

Date: 2026-09-09.

## E1 — Exact one-interaction resolution

Given:
- predicate T is source 10.0.0.1 -> destination 10.0.0.2, TCP/6, destination port 443;
- one effective Domain Interaction D has exactly the same realized technical region at `asOf`;
- RC/ACC knowledge is complete.

Then:
- correspondence T↔D is `Exact`;
- resolution status is `Exact`;
- remainder is empty;
- D identity and RC/ACC provenance are preserved.

## E2 — Predicate is contained by a broader Domain Interaction

Given:
- T is TCP/443;
- one Domain Interaction region is TCP/440..450 for the same addresses;
- no competitor exists.

Then:
- correspondence is `CoveredBy`;
- overlap witness equals T;
- resolution status is `Covered`;
- remainder is empty.

## E3 — Predicate covers a narrower Domain Interaction and leaves remainder

Given:
- T is TCP/440..450;
- one Domain Interaction is TCP/443 for the same addresses;
- no other interaction covers the rest.

Then:
- correspondence is `Covers`;
- resolution status is `Partial`;
- remainder is exactly TCP/440..442 plus TCP/444..450.

## E4 — Several non-ambiguous interactions cover the predicate

Given:
- T contains destination ports 443 and 8443;
- D1 maps only 443;
- D2 maps only 8443;
- D1 and D2 technical regions do not overlap;
- knowledge is complete.

Then:
- both Domain Interactions are returned;
- remainder is empty;
- status is `Covered`, not Ambiguous.

## E5 — Partial address overlap preserves exact remainder

Given:
- T source range is 10.0.0.1..10.0.0.3;
- one Domain Interaction uses source endpoint 10.0.0.2 with otherwise equal transport/destination;
- no other interaction overlaps.

Then:
- one overlap witness exists for source 10.0.0.2;
- status is `Partial`;
- remainder preserves source 10.0.0.1 and 10.0.0.3 as unmapped fragments.

## E6 — Competing Domain Interactions are ambiguous

Given two distinct Domain Interaction identities D1 and D2 have the same effective technical region as T.

Then:
- both correspondences are returned;
- an ambiguity witness equals the overlapping technical fragment;
- status is `Ambiguous`;
- no winner is selected by catalogue order.

## E7 — Multiple facts for the same interaction are not ambiguity

Given one Domain Interaction identity is supported by two effective provenance facts that produce the same technical region.

Then:
- provenance is aggregated;
- only one business meaning exists;
- status is not Ambiguous solely because supporting facts are duplicated.

## E8 — No overlap is unresolved

Given complete RC/ACC knowledge and no candidate technical region overlaps T.

Then:
- correspondences are empty;
- status is `Unresolved`;
- complete remainder equals T.

## E9 — Missing bound Resource realization is Unknown

Given:
- an ACC DCS has effective source/destination Resource bindings;
- a bound Resource realization required to determine possible overlap cannot be established at `asOf`;
- known facts cannot prove the candidate disjoint from T.

Then:
- status is `Unknown`;
- a Resource Catalogue knowledge gap is preserved;
- the missing Resource is not treated as no-match.

## E10 — Unrelated unsupported DCS does not poison the result

Given:
- one DCS uses unsupported transport syntax;
- its fully resolved source/destination endpoint addresses are disjoint from T;
- another address-relevant DCS resolves exactly to T.

Then:
- the unrelated DCS does not create a predicate-relevant knowledge gap;
- T may resolve `Exact`.

## E11 — Address-relevant unsupported DCS transport is Unknown

Given:
- a DCS source/destination realization overlaps T addresses;
- its transport token cannot be translated to an exact IP protocol number/source-neutral port region.

Then:
- status is `Unknown`;
- ACC knowledge gap/provenance is preserved;
- APR does not guess the transport meaning.

## E12 — Protocol Any remains explicit Unknown

Given T has `ProtocolSelector = Any` and Any source/destination ports.

Then:
- T remains valid evidence;
- I18 result status is `Unknown`;
- no guessed per-protocol expansion is performed;
- revisit is required only when an accepted protocol-wide algebra exists.

## E13 — NotApplicable and numeric ports are distinct

Given same exact protocol/address dimensions:
- T source/destination ports are `NotApplicable`;
- D uses numeric `Any` or `Ranges`.

Then:
- the port dimensions do not overlap;
- APR does not coerce NotApplicable into port 0..65535.

## E14 — Effective time changes candidate realization

Given:
- the same Domain Interaction is bound to Resource realization A before T2 and B from T2;
- predicate matches only A.

Then:
- resolution at `asOf < T2` may match;
- resolution at `asOf >= T2` does not reuse stale A;
- both results preserve their explicit `asOf`.

## E15 — Unknown EvidenceTime never becomes RecordedAt

Given a TAE entry belongs to EvidenceTime Unknown and was recorded at R.

When a caller asks APR to resolve it.

Then:
- caller must still provide explicit `asOf`;
- APR/TAE adapter does not silently use R.

## E16 — Evidence action does not authorize

Given two TAE entries carry identical predicates, one with action Permit and one with Block.

When each predicate is resolved against the same RC/ACC snapshot.

Then:
- Domain Access Resolution correspondence is the same;
- the original action may remain traceable as evidence provenance;
- no Access Rule or Connectivity Decision is created.

## E17 — Consumer independence

Given the same technical predicate and same domain knowledge snapshot are passed by:
- a future proposal consumer;
- a future reconciliation consumer.

Then:
- Domain Access Resolution is equal;
- no consumer flag changes relation/status/remainder.

## E18 — No placement or reconciliation leakage

Given a predicate resolves to a Domain Interaction.

Then I18 result contains no:
- Logical Firewall/Enforcement Attachment;
- Satisfied/Unsatisfied result;
- Add/Remove/Replace/No-op;
- vendor/device operation.
