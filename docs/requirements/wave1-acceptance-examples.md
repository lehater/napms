# Wave-1 acceptance examples — PLAN-026 WP-04

Status: `accepted specification-by-example baseline`.

Date: 2026-09-08.

## Purpose

Make material Wave-1 product rules testable without choosing APIs, persistence, services, topology or vendor implementation.

## E1 — Proposal structural validity

### Valid described interaction

Given:
- actor has effective request authority for the relevant scope/time;
- Source Component Deployment and Destination Component Deployment resolve to trusted catalogue objects;
- an immutable DCS contract/revision explicitly describes a compatible directed interaction for those selected deployments/component roles.

When the actor composes a proposal.

Then the proposal subject is valid and is exactly:

```text
Source Component Deployment
+ Destination Component Deployment
+ DCS contract/revision
```

No additional blanket `same Application` invariant is introduced. Structural validity follows the explicitly described DCS interaction and valid domain references.

### Structurally undescribed interaction

Given the actor has request authority and both deployments exist, but no DCS contract/revision describes the selected directed interaction.

Then the product must not form/submit a valid Access Rule Proposal for that combination.

The normal composition surface should restrict visible/selectable combinations to valid references and described interactions rather than relying only on post-submit rejection.

## E2 — Authority to propose is not permission to connect

Given the actor has effective request authority and composes a structurally valid proposal.

When ConnectivityDecision returns `NotAllowed`.

Then no authoritative Access Rule is materialized.

Request authority does not imply connectivity permission.

## E3 — First allowed materialization

Given a valid proposal for semantic identity `R` and ConnectivityDecision(`R`) = `Allowed`, and no authoritative Rule exists for `R`.

When Access Policy materializes the decision.

Then:
- one authoritative Rule ID is created for `R`;
- its initial operational state is `Active`;
- it may contribute desired effect immediately, subject to declarative effective conditions.

## E4 — Idempotent repeated allowed materialization

Given authoritative Rule `R1` already exists for semantic identity `R` from an Allowed decision.

When the same allowed semantic identity is materialized again.

Then the existing Rule ID `R1` is resolved and no duplicate authoritative Rule is created.

## E5 — Identity-defining change creates another Rule subject

Given an existing allowed Rule identified by Source Deployment A + Destination Deployment B + DCS revision D1.

When Source Deployment, Destination Deployment or decision-relevant DCS semantics change.

Then the resulting combination is another semantic Rule subject and requires another Connectivity Decision.

The historical Rule/decision is not rewritten.

## E6 — Technical realization change preserves Rule identity

Given an existing allowed Rule whose Source Resource Endpoint changes IP/VM/provider realization without changing Source Deployment, Destination Deployment or DCS semantics.

Then:
- the Rule ID remains unchanged;
- the historical Connectivity Decision remains unchanged;
- later normalized export resolves the current authoritative realization for its export `as-of`.

## E7 — Operational suspension

Given an allowed `Active` Rule.

When an authorized actor changes it to `Inactive`.

Then:
- the same Rule ID is retained;
- no new Connectivity Decision is required solely for the state transition;
- the Rule contributes no desired network effect;
- the state transition is auditable.

When it is later changed back to `Active`, the same Rule and prior decision coverage remain, subject to current declarative conditions and any explicitly superseding decision contract.

## E8 — EffectiveWindow condition

Given an allowed `Active` Rule with `EffectiveWindow(start, end)`.

Then:
- at `as-of == start`, the window permits effect;
- at any `start < as-of < end`, the window permits effect;
- at `as-of == end` or outside the interval, the window does not permit effect;
- a Rule with no EffectiveWindow has no time-window restriction.

The interval is therefore `[start, end)`, with explicit offset-aware instants and `start < end`.

Setting, changing or removing the window preserves Rule ID and historical Connectivity Decision and is business-audited. The window never periodically toggles stored `Active/Inactive`.

## E9 — Complete normalized export

Given an authorized export selection containing effective Rules R1 and R2.

At one logical export `as-of`, all required current Resource Catalogue realization and DCS facts for R1/R2 are known and temporally valid.

When export is produced.

Then the result is a successful vendor-neutral Normalized Policy Export containing complete technical projection for both selected effective Rules with Rule/decision/source-fact provenance.

## E10 — Missing/stale realization blocks successful export

Given an authorized export selection containing effective Rules R1 and R2, but required realization for R2 is missing, stale or cannot be established as valid for the export `as-of`.

Then the operation must not present a complete successful Normalized Policy Export.

It may return explicit diagnostics and partial rows, but those rows are not a downstream-ready successful export artifact.

## E11 — Inactive/non-effective Rules do not create export failure

Given the selected domain-policy subset contains an `Inactive` Rule or an `Active` Rule whose declarative condition is false at export `as-of`.

Then that Rule is not part of the effective desired-policy subset and contributes no normalized row.

Absence of technical realization for such a non-effective Rule does not by itself make the effective-policy export incomplete.

## E12 — One Rule may expand to several rows

Given one authoritative Rule maps at export time to several concrete endpoint/protocol/port rows without changing its semantic meaning.

Then normalization may emit multiple rows, and every row retains correlation to the same authoritative Rule and relevant decision/source facts.

## E13 — Equivalent technical effects keep independent provenance

Given two independently authoritative Rules project to technically equivalent traffic rows.

Then normalization must not collapse them if doing so would lose Rule/decision provenance.

Representation optimization must not broaden, narrow or erase independent business meaning.

## E14 — Historical decisions are not silently reinterpreted

Given an existing Rule was materialized from an Allowed decision and later ownership/responsibility, technical realization or other external catalogue context changes.

Then the historical Connectivity Decision record is not rewritten.

Current action authority and export realization are evaluated from their respective current/effective authorities. Any rule that a changed external fact requires decision re-evaluation/supersession remains inside the deferred Connectivity Decision Domain unless explicitly promoted later.

## WP-04 result

Normal, boundary, negative and degraded examples cover the material Wave-1 rules through normalized export. No additional product state, bulk-request lifecycle, same-Application constraint, vendor rendering or execution semantics are introduced by the examples.
