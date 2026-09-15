# Technical Access Evidence acceptance examples

## E1 — Record one configured capture

Given a stable source reference, explicit source scope, stable capture reference, `Configured` kind, source time and faithfully normalized source items, recording produces one immutable Evidence Set with stable set/entry identities and preserved source/time provenance. No authorization or desired-policy conclusion is created.

## E2 — Identical retry is idempotent

Given an Evidence Set already exists for source + capture, recording the same source-qualified payload again returns the existing set with its original Set/Entry IDs and original RecordedAt. Retry comparison ignores candidate generated IDs, retry time and incidental parser/list order, while duplicate multiplicity and factual source positions remain significant.

## E3 — Conflicting retry fails

Given an Evidence Set exists for source + capture, a different source-qualified payload for the same identity is rejected as a capture conflict. The existing immutable set remains unchanged; no last-write-wins replacement occurs.

## E4 — Duplicate normalized entries are preserved

Two source records with identical normalized predicates become two Technical Access Entries with distinct generated identities. Optional native source references/positions remain traceable.

## E5 — Unknown source time remains unknown

An imported artifact with no trustworthy source time records `EvidenceTime = Unknown` and a separate RecordedAt. RecordedAt is not presented as source observation/effective time.

## E6 — Traffic-derived observation window

Traffic evidence derived from `[T1,T2)` records `TrafficDerived` plus `EvidenceTime = Window(T1,T2)` with `T1 < T2`. Observing a predicate does not manufacture a configured Permit/Block action, and absence of other predicates does not prove they were blocked.

## E7 — Invalid time window

A Window with `start >= end` is invalid and creates no Evidence Set.

## E8 — Normalization preserves represented space

Canonical range ordering/merging and protocol-name normalization may change representation but preserve exactly the same address/protocol/port region.

If a source service/object dimension cannot be reduced to the accepted model without loss, normalization fails. All-protocol with constrained ports is expanded into exact protocol-specific entries when source semantics permit; `Protocol Any + Port Ranges` is not an accepted shortcut.

## E9 — Unfaithful item blocks complete capture

If any source item cannot be represented faithfully, no successful complete Evidence Set is reported. The remaining items are not silently stored as though the capture were complete.

## E10 — Empty capture is evidence, not absence truth

A capture containing zero normalized entries may produce an empty Evidence Set. Without an explicit completeness contract, the product does not infer that no technical access exists outside the captured source scope.

## E11 — Action exists only when factual

A source record that faithfully asserts Block may preserve Block. A record or traffic observation without a compatible action claim stores no action rather than guessing one.

## E12 — Source order is local provenance

Source positions may be preserved when factual. They are meaningful only within their capture and do not create global/cross-source policy ordering.

## E13 — Source scope is not Responsibility Scope

Identical text in `SourceScopeReference` and an Authority Management `ResponsibilityScopeRef` does not make them the same concept. TAE infers no authority or Resource affiliation from such a string match.

## E14 — Listing does not select current truth

Several immutable captures for one source/scope remain listable/filterable. TAE does not automatically label the newest capture Current/Fresh or discard earlier captures.

## E15 — Persistence uncertainty does not become success

Persistence failure before authoritative commit is not reported as success. Unknown commit outcome remains explicit uncertainty and retries resolve through source + capture identity.

## E16 — Evidence recording has no Access Policy side effect

Recording a valid Evidence Set may increase evidence state only. It does not create or change Access Policy Rules, Access Governance decisions, Required Policy Materialization or network operations.

## E17 — TAE performs no business/domain resolution

An evidence predicate that happens to correspond to known Application/Resource semantics is still recorded/read only as technical evidence plus provenance. Correlation to business/application/resource meaning belongs to an explicit consuming workflow outside TAE.

## Executable evidence

Current implementation evidence includes core TAE tests, PostgreSQL round-trip/idempotency/conflict tests, local-import normalization tests and bounded-context architecture tests. Test names are implementation evidence rather than canonical semantic ownership; these examples and the TAE Tactical model remain the behavioral contract.
