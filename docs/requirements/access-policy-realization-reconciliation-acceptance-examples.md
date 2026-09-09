# Access Policy Realization Reconciliation acceptance examples — I20

Status: `accepted I20 WP-0 specification-by-example baseline`.

Date: 2026-09-09.

Unless stated otherwise, examples use:
- one Access Policy governance scope S;
- one Enforcement Target T = Logical Firewall LF1 + Enforcement Attachment EA1;
- one explicit `asOf = 2026-09-09T12:00:00+00:00`;
- exact TCP/6 source/destination endpoints;
- a trusted configured source contract proving same managed scope, effective Permit-set semantics and complete coverage;
- selected TAE `Configured` Evidence Time exactly `Instant(asOf)`;
- complete non-ambiguous RC/ACC and NEP knowledge.

## E1 — Exact configured match is No-op

Given desired region D is destination TCP/443 and configured effective Permit region C is exactly TCP/443.

Then:
- `common = TCP/443`;
- `missing = ∅`;
- `extra = ∅`;
- reconciliation = `Satisfied`;
- Required Semantic Change = `No-op`.

## E2 — Complete empty configured snapshot requires Add

Given desired D is TCP/443 and the configured effective Permit snapshot is empty **and complete for the same managed scope**.

Then:
- `missing = TCP/443`;
- `extra = ∅`;
- reconciliation = `Drift`;
- Required Semantic Change = `Add`.

The conclusion comes from the completeness/source contract, not from empty TAE entries alone.

## E3 — Configured permit with no desired region requires Remove

Given desired D is empty for T and configured C contains TCP/22 under the same exclusive managed scope.

Then:
- `missing = ∅`;
- `extra = TCP/22`;
- reconciliation = `Drift`;
- Required Semantic Change = `Remove`.

If the configured capture also contains policy belonging to another management scope, this example is invalid and must be Unknown rather than Remove.

## E4 — Disjoint desired/configured regions are Replace

Given desired D is TCP/443 and configured C is TCP/80.

Then:
- `common = ∅`;
- `missing = TCP/443`;
- `extra = TCP/80`;
- Required Semantic Change = `Replace`.

Replace is the compact scope-level semantic classification of simultaneous missing+extra; it does not prescribe a single device replace command.

## E5 — Partial overlap preserves exact witnesses

Given:
- desired destination ports = 1000..2000;
- configured effective Permit destination ports = 1500..2500.

Then:
- common = 1500..2000;
- missing = 1000..1499;
- extra = 2001..2500;
- reconciliation = `Drift`;
- Required Semantic Change = `Replace`.

No port widening is allowed.

## E6 — Incomplete configured capture is Unknown

Given desired D is TCP/443, configured entries are empty, but source completeness for the managed scope is Unknown/Partial.

Then:
- APR may show known evidence diagnostics;
- it shall not conclude Add or No-op from absence;
- reconciliation = `Unknown`;
- Required Semantic Change is not complete.

## E7 — Shared-firewall scope mismatch is Unknown

Given:
- LF1 hosts policy for governance scopes S1 and S2;
- selected configured capture covers both;
- reconciliation requests only S1;
- no exact source contract partitions configured evidence between S1 and S2.

Then:
- APR shall not classify S2 policy as extra S1 access;
- result = `Unknown`;
- no Remove classification is produced.

## E8 — Evidence instant mismatch is Unknown

Given desired/placement `asOf = T1`, but selected configured Evidence Time is `Instant(T0)` where T0 != T1.

Then:
- RecordedAt or capture recency does not repair the mismatch;
- result = `Unknown`.

The same applies to `EvidenceTime.Unknown` and the first-slice `Window` evidence.

## E9 — Raw Block/order semantics are unsupported until normalized

Given a configured source has:
- overlapping Permit and Block entries;
- source rule order/default behavior determines effective permission;
- no source-specific evaluator establishes effective Permit regions.

Then:
- APR shall not compare raw entries as if they were an unordered set;
- configured snapshot has an evaluation knowledge gap;
- reconciliation = `Unknown`.

## E10 — Desired placement ambiguity selects no enforcement target

Given one desired effective Rule resolves to one exact technical region but NEP selection is `Ambiguous` between two placements.

Then:
- both NEP competitors are preserved;
- APR does not choose a target;
- desired enforcement derivation = `Ambiguous`;
- no complete target reconciliation is claimed for that row.

## E11 — Desired technical collision with non-desired interaction is ambiguous

Given:
- effective desired Rule set contains Domain Interaction D1;
- the exact technical region needed for D1 also maps, under I18, to distinct Domain Interaction D2;
- D2 has no effective desired Rule in the selected scope.

Then:
- enforcing that technical region would necessarily permit both D1 and D2;
- APR does not call it business-correct desired enforcement;
- desired derivation = `Ambiguous`;
- D1 is not silently treated as uniquely enforceable.

## E12 — Shared technical region is acceptable when every interaction is desired

Given:
- the same exact technical region maps to D1 and D2;
- both D1 and D2 have effective desired Rules in the selected scope.

Then:
- the technical intent may be canonicalized once for the same target;
- both Rules/Domain Interactions remain provenance;
- policy-level derivation is not Ambiguous solely because the network representation is shared.

## E13 — Configured domain ambiguity blocks Satisfied

Given:
- configured effective Permit C is technically equal to desired D;
- I18 maps C to competing Domain Interactions and not all ambiguity is eliminated by the desired Rule set.

Then:
- raw technical equality is retained as a witness;
- reconciliation = `Ambiguous`, not Satisfied;
- no ambiguity winner is selected.

## E14 — NoEnforcement remains a complete placement fact, not configured absence

Given a desired Rule has NEP `NoEnforcement`.

Then:
- APR records the row as a complete no-enforcement derivation diagnostic;
- it generates no guessed Enforcement Target;
- it does not infer that configured policy is missing at an arbitrary firewall.

## E15 — NoForwardingPath remains distinct

Given a desired Rule has NEP `NoForwardingPath`.

Then:
- APR preserves the positive no-route provenance;
- it generates no enforcement target for that row;
- it does not rewrite the outcome to NoEnforcement, Add or Remove.

## E16 — Provider replacement does not change target identity by itself

Given LF1 + EA1 remains the accepted Enforcement Target while NEP provider realization correspondence changes over time.

Then:
- desired enforcement target identity remains LF1 + EA1;
- provider/path provenance changes with `asOf`;
- I20 does not create a new target merely because provider realization changed.
