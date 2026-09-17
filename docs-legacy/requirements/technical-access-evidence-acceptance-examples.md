# Technical Access Evidence acceptance examples — I17

Status: `accepted I17 WP0 specification-by-example baseline`.

Date: 2026-09-09.

## E1 — Record one configured capture

Given:
- source S has stable source reference;
- source scope Q is explicit;
- capture reference C is stable;
- kind is Configured;
- source time is Instant T;
- every source item is normalized faithfully.

When the capture is recorded at NAPMS time R.

Then:
- one immutable Evidence Set receives a stable Evidence Set ID;
- S/Q/C/Configured/T/R are preserved;
- every normalized entry receives its own stable Entry ID;
- no authorization or desired-policy conclusion is created.

## E2 — Identical retry is idempotent

Given Evidence Set E already exists for source S + capture C.

When the same source-qualified capture payload is recorded again later.

Then:
- comparison ignores new candidate generated IDs, retry-attempt recording time and incidental parser/list order;
- duplicate multiplicity and factual source positions still participate in equality;
- E is returned with its original Set/Entry IDs and original RecordedAt;
- no second set is created;
- no history is mutated.

## E3 — Same capture identity with different content conflicts

Given E exists for S + C.

When another record attempt uses S + C but contains different normalized predicate/action/order/time facts.

Then:
- the attempt is rejected as a capture identity/content conflict;
- E remains unchanged;
- no last-write-wins replacement occurs.

## E4 — Duplicate normalized entries are preserved

Given one source capture contains two distinct source records whose normalized predicates are identical.

When the capture is recorded.

Then:
- two Technical Access Entries are stored;
- each has a different generated Entry ID;
- optional distinct native entry references/positions remain traceable;
- the entries are not collapsed by content.

## E5 — Unknown source time remains unknown

Given an Imported artifact has no trustworthy source observation/effective time.

When it is recorded at R.

Then:
- EvidenceTime is Unknown;
- RecordedAt is R;
- the product does not present R as source observation/effective time.

## E6 — Traffic-derived observation window

Given traffic evidence is derived from observation window [T1,T2).

When recorded.

Then:
- kind is TrafficDerived;
- EvidenceTime is Window(T1,T2);
- T1 < T2;
- presence of an observed predicate does not create a configured Permit rule;
- absence of other predicates does not prove they were blocked.

## E7 — Invalid time window

Given EvidenceTime Window has start >= end.

Then recording is invalid and no Evidence Set is created.

## E8 — Address/port normalization preserves the region

Given source syntax describes one exact set of IP ranges and transport ports.

When an outer adapter normalizes the source item.

Then:
- canonical range ordering/merging may change representation;
- source protocol names are mapped to `Any | IpProtocolNumber(0..255)`;
- represented address/protocol/port space remains exactly equal;
- no broader/narrower predicate is accepted.

If a source service/object dimension cannot be reduced to the accepted address/protocol/port model without loss, the item is unfaithful and E9 applies.

If source syntax means all protocols with no port restriction, it may normalize to protocol Any + source/destination ports Any.

If source syntax combines an all-protocol selector with a constrained port range, it must be expanded into exact protocol-specific entries when semantics permit; `Protocol Any + Port Ranges` is not accepted as a shortcut.

## E9 — Unfaithful item blocks the first-slice capture

Given a capture has N source items and one cannot be represented faithfully by the accepted normalized predicate/action model.

When recording is attempted.

Then:
- no successful complete Evidence Set is reported for that capture;
- N-1 items are not silently stored as though complete;
- the failure identifies normalization as the reason.

## E10 — Empty configured capture is evidence, not absence truth

Given source S/Q/C reports zero normalized entries.

When the capture is recorded.

Then:
- an empty Evidence Set may be stored;
- the product may say the capture contained zero entries;
- it may not conclude no technical access exists outside an accepted completeness model.

## E11 — Optional action only when source asserts it

Given one Configured source record can be mapped faithfully to Block.

Then the entry may store Block.

Given another source record or TrafficDerived observation has no compatible action claim.

Then action is absent rather than guessed.

## E12 — Source order is local provenance

Given a configured source exposes positions 10 and 20.

Then those positions may be preserved on entries.

They do not define ordering against another source/capture and do not become a universal firewall-evaluation model.

## E13 — Source scope is not Responsibility Scope

Given SourceScopeReference is `policy-package-a` and an AM Responsibility Scope happens to have the same text.

Then TAE still treats them as different concepts.

No authority or Resource affiliation is inferred from the string match.

## E14 — Listing does not select current truth

Given two immutable captures C1 and C2 exist for the same source/scope at different times.

When evidence is listed.

Then both can be returned/filterable.

TAE does not automatically label C2 Current/Fresh or discard C1.

## E15 — Persistence failure does not claim success

Given a valid capture but persistence fails before authoritative commit.

Then recording is not reported as successful.

If commit outcome is unknown, return explicit uncertainty and resolve retries using source + capture identity.

## E16 — Evidence has zero Access Policy side effect

Given zero Access Rules exist before a valid Evidence Set is recorded.

After recording:
- Evidence Set count may increase;
- Access Rule count remains zero;
- no Connectivity Decision is created/changed.

## E17 — No technical-to-domain resolution in I17

Given an evidence predicate happens to correspond to a known ACC/RC interaction.

When I17 records or reads the evidence.

Then it returns only the technical predicate and provenance.

Any exact/partial/ambiguous/unresolved domain interpretation is I18 behavior and is absent from the I17 result.


## Executable evidence at I17 closure

| Example | Primary executable evidence |
| --- | --- |
| E1 Configured capture | `backend/tests/integration/postgres/test_technical_access_evidence.py::test_round_trip_preserves_full_source_qualified_evidence` |
| E2 Identical retry | `backend/tests/technical_access_evidence/test_core.py::test_identical_retry_returns_existing_ids_and_recorded_at`; dedicated TAE composition durable retry proof |
| E3 Conflicting retry | `backend/tests/technical_access_evidence/test_core.py::test_same_capture_with_different_payload_is_conflict`; PostgreSQL conflict test |
| E4 Duplicate entries | `backend/tests/technical_access_evidence/test_core.py::test_duplicate_entry_payloads_are_preserved`; PostgreSQL round-trip |
| E5 Unknown source time | `backend/tests/integration/postgres/test_technical_access_evidence.py::test_empty_unknown_time_capture_round_trips` |
| E6 Traffic-derived window/action | `backend/tests/technical_access_evidence/test_core.py::test_configured_block_and_traffic_derived_action_absence_are_preserved`; PostgreSQL window/list proof |
| E7 Invalid time window | `backend/tests/technical_access_evidence/test_core.py::test_evidence_time_keeps_unknown_and_recorded_time_distinct` |
| E8 Exact normalization | core canonicalization tests + strict local-import protocol/port tests |
| E9 No silent partial normalization | `backend/tests/technical_access_evidence/test_local_import.py::test_local_import_rejects_one_invalid_entry_before_any_record_command_exists`; duplicate/unsupported-field rejection; dedicated composition no-side-effect failure proof |
| E10 Empty capture | `backend/tests/integration/postgres/test_technical_access_evidence.py::test_empty_unknown_time_capture_round_trips` |
| E11 Optional factual action | `test_configured_block_and_traffic_derived_action_absence_are_preserved`; local-import action tests |
| E12 Source order provenance | PostgreSQL round-trip preserves source positions; retry equality includes factual position |
| E13 Source scope isolation | bounded-context architecture dependency tests; TAE core imports no Authority Management/Resource/NEP context |
| E14 No current winner | `backend/tests/technical_access_evidence/test_core.py::test_list_keeps_multiple_captures_without_selecting_current_truth` |
| E15 Persistence uncertainty | core commit-unknown test + PostgreSQL repository commit-failure test |
| E16 No Access Policy/Decision side effect | `backend/tests/integration/postgres/test_technical_access_evidence_greenfield.py::test_local_import_records_and_reads_back_durable_evidence` |
| E17 No technical-to-domain resolution | bounded-context architecture tests + TAE read DTOs expose evidence facts only |

This table records proof locations; it does not transfer semantic ownership from the canonical Tactical DDD/requirements to tests.
