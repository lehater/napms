# Requirement-to-Policy Alignment acceptance examples — I14

Status: `accepted I14 WP2 specification-by-example baseline`.

Date: 2026-09-09.

## A1 — Covered by exact effective Rule

Given:
- actor may read Requirement R;
- R is Active and applicable at T;
- R requires interaction X -> Y / DCS D;
- Access Rule P has the exact same semantic identity;
- P contributes effective desired policy at T.

When alignment is evaluated at T.

Then result is `Covered`.

## A2 — No matching Rule

Given R is current at T and no exact matching Rule exists.

Then result is `Uncovered`.

The result does not mean `Denied`.

## A3 — Matching Rule inactive

Given exact matching Rule exists but OperationalState is Inactive at T.

Then result is `Uncovered`.

## A4 — Matching Rule outside EffectiveWindow

Given exact matching Rule is Active but its EffectiveWindow excludes T.

Then result is `Uncovered`.

At the window start it is effective; at the window end it is not effective.

## A5 — Requirement outside applicability

Given R is Active but its absolute applicability excludes T.

Then result is `NotCurrent`, regardless of matching Rule state.

## A6 — Retired Requirement

Given R is Retired.

Then result is `NotCurrent`.

## A7 — Governance scopes differ

Given:
- Requirement Governance Scope = CR-SCOPE;
- exact matching Rule Governance Scope = AP-SCOPE;
- actor may read R;
- exact matching Rule is effective.

Then derived status may be `Covered` even though scopes differ.

No scope equality is required for semantic match.

## A8 — Covered without Rule detail permission

Given A7 and actor lacks Access Policy Rule read permission.

Then:
- result is `Covered`;
- Rule ID/scope/decision/proposal/effective-window/audit are absent.

## A9 — Covered with independent Rule detail permission

Given A7 and actor is independently authorized to read the matching Rule.

Then:
- result is `Covered`;
- optional Rule evidence may include the authorized Rule details/provenance selected by the contract.

## A10 — Hidden policy does not become false Uncovered

Given R is current but the policy dependency cannot establish authoritative coverage due to ambiguity/unavailability.

Then result is `Unknown`.

It must not return `Uncovered`.

## A11 — Requirement read denied

Given actor cannot read R.

Then no Alignment result or Requirement data is returned.

## A12 — Exact mismatch

Given effective Rule exists for X -> Y / DCS D2 while R requires X -> Y / DCS D1.

Then R is `Uncovered`.

## A13 — Source/destination direction matters

Given effective Rule exists for Y -> X / DCS D while R requires X -> Y / DCS D.

Then R is `Uncovered`.

## A14 — Dependent does not affect match

Given two Requirements have the same exact interaction but different participating Dependents.

Then the same effective matching Rule covers both Requirements at the same T.

## A15 — Alignment is recomputed, not persisted

Given R is `Covered` at T1.

When the matching Rule becomes Inactive and alignment is evaluated at T2.

Then result becomes `Uncovered` without mutating R or an Alignment aggregate.

## A16 — Rule window change changes result

Given matching Rule EffectiveWindow initially contains T, then is changed so T is excluded.

Then alignment changes `Covered -> Uncovered` on recomputation.

## A17 — Requirement applicability change changes currentness

Given R is Ongoing and Covered at T.

When R applicability is changed to a window that excludes T.

Then result is `NotCurrent`.

No Access Rule changes.

## A18 — No Denied result

Given R is current and no authorized Rule covers it.

Then output vocabulary is `Uncovered`, never `Denied`.

## A19 — No configured-state claim

Given R is Covered.

Then I14 still cannot conclude that firewall/device configuration exists or traffic is observed.

## A20 — Explicit asOf required

Given no valid offset-aware `asOf`.

Then alignment evaluation is rejected rather than consulting current wall-clock implicitly.
