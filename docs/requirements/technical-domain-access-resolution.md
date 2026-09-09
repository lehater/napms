# Technical-to-Domain Access Resolution requirements — I18

Status: `accepted I18 WP0 behavioral baseline`.

Date: 2026-09-09.

## Purpose

Define the first observable behavior for interpreting one normalized Technical Access Predicate in domain-interaction terms without turning technical evidence into authorization, desired policy, placement or reconciliation truth.

## REQ-APR-RES-001 — Own one shared resolution capability

Access Policy Realization shall own Technical-to-Domain Access Resolution.

Proposal and Reconciliation consumers shall receive the same result for the same predicate + effective RC/ACC knowledge + `asOf`.

No consumer-specific matching mode may change domain meaning.

## REQ-APR-RES-002 — Require explicit logical time

Every resolution shall require offset-aware `asOf`.

The product shall not substitute:
- TAE `RecordedAt`;
- latest capture time;
- wall-clock now
for unknown source/effective time.

## REQ-APR-RES-003 — Preserve upstream ownership

Resolution shall consume source-neutral projections of:
- normalized technical predicate/provenance;
- effective RC Resource/Endpoint realization;
- effective ACC DCS + DeploymentResourceBinding facts.

APR shall not mutate or persist copies as authoritative peer-context truth.

## REQ-APR-RES-004 — Resolve Domain Interaction identity exactly

A resolved Domain Interaction is identified by:
- Source Component Deployment;
- Destination Component Deployment;
- immutable DCS revision.

Resolution shall not manufacture an Access Rule identity or Rule state.

## REQ-APR-RES-005 — Compare exact technical regions

For supported predicates, APR shall compare source addresses, destination addresses, exact IP protocol number, source ports and destination ports without broadening or narrowing.

Pairwise correspondence vocabulary is exactly:
- `Exact`;
- `Covers`;
- `CoveredBy`;
- `PartialOverlap`;
- `None`.

Every non-empty correspondence shall carry an exact technical overlap witness.

## REQ-APR-RES-006 — Produce one resolution status

Resolution status is:
- `Exact`;
- `Covered`;
- `Partial`;
- `Ambiguous`;
- `Unresolved`;
- `Unknown`.

Status follows the Tactical DDD precedence and never hides Unknown behind a more confident classification.

## REQ-APR-RES-007 — Preserve unresolved technical remainder

With complete supported knowledge, APR shall return the exact canonical set difference:

```text
input predicate - union(all resolved overlap witnesses)
```

A successful complete result shall not silently drop unmapped technical space.

## REQ-APR-RES-008 — Never pick an ambiguity winner

When the same non-empty technical fragment maps to more than one distinct Domain Interaction, result status shall be `Ambiguous`.

All competing interactions/witnesses shall remain visible.

No ordering, first-match or arbitrary catalogue iteration rule may choose one business meaning.

## REQ-APR-RES-009 — Fail closed on predicate-relevant unknowns

Missing/stale/non-unique RC realization, invalid/ambiguous ACC projection state or untranslatable address-relevant DCS transport meaning shall produce explicit `Unknown` when the missing fact could affect the predicate.

Facts proven disjoint from the predicate shall not create unrelated global Unknown.

## REQ-APR-RES-010 — First exact algebra is protocol-number scoped

The first executable exact difference algebra supports `ProtocolSelector = IpProtocolNumber`.

`ProtocolSelector = Any` remains valid evidence but resolves as `Unknown` until a protocol-wide port-applicability/difference model is accepted.

The product shall not expand `Any` using guessed protocol semantics.

## REQ-APR-RES-011 — Keep port semantic modes distinct

For one exact protocol:
- `Any` means numeric ports 0..65535;
- `Ranges` means the canonical numeric subset;
- `NotApplicable` is a distinct semantic;
- numeric and NotApplicable regions do not overlap.

## REQ-APR-RES-012 — Use effective domain realization only

Candidate technical regions shall be built from effective ACC bindings and effective RC realizations at the requested `asOf`.

An ACC interaction with no effective Resource binding has no effective technical realization candidate for I18.

A bound Resource whose effective realization cannot be established is not silently treated as no-match.

## REQ-APR-RES-013 — Preserve explainable provenance

Resolution shall preserve:
- input/evidence provenance;
- `asOf`;
- Domain Interaction identity;
- ACC DCS/binding provenance;
- source and destination RC realization provenance;
- exact overlap witnesses;
- attributable knowledge gaps.

## REQ-APR-RES-014 — Keep TAE action outside domain meaning

TAE entry action `Permit | Block | absent` may be carried as provenance but shall not change Domain Interaction correspondence.

Technical correspondence is not authorization.

## REQ-APR-RES-015 — No persistence or public workflow required

I18 does not require an APR database/table, public HTTP/Web workspace or new Authority Management action.

A Domain Access Resolution is derived on demand unless a later accepted lifecycle/identity requirement establishes persistence.

## REQ-APR-RES-016 — Keep I19/I20 semantics out

I18 shall not determine:
- Logical Firewall / Enforcement Attachment;
- desired-vs-configured satisfaction;
- Add/Remove/Replace/No-op;
- vendor rendering;
- provider/device execution.

## Trace

Tactical semantics:
- `docs/domain/access-policy-realization/tactical-model.md`.

Executable examples:
- `docs/requirements/technical-domain-access-resolution-acceptance-examples.md`.

Architecture:
- `docs/architecture/access-policy-realization-resolution-boundary.md`.
