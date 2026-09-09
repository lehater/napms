# Requirement-to-Policy Alignment requirements — I14

Status: `accepted I14 WP2 behavioral baseline`.

Date: 2026-09-09.

## Purpose

Define the first Requirement-centric comparison between authoritative Connectivity Requirements and authoritative effective Access Policy.

## Scope

I14 answers, for one Requirement and one explicit `asOf`:

```text
is this current semantic connectivity need covered by effective authorized policy?
```

I14 does not:
- approve/deny connectivity;
- persist Alignment as peer domain truth;
- infer configured/observed access;
- expose hidden Rule details;
- perform policy-centric orphan detection.

## ALN-001 — Exact semantic match

A Requirement matches an Access Rule only when:

```text
RequiredSemanticInteraction
==
RuleSemanticIdentity
```

using exact equality of:
- Source Component Deployment;
- Destination Component Deployment;
- immutable DCS revision.

Dependent, governance scopes, actor and technical realization are not part of semantic matching.

## ALN-002 — One explicit logical time

One offset-aware `asOf` is used for:
- Requirement applicability;
- Access Rule effective-state evaluation;
- any authority evaluation required by the composition.

No hidden wall-clock time is permitted.

## ALN-003 — Requirement currentness

A Requirement is current at `asOf` only when:
- lifecycle is Active; and
- applicability is Ongoing or includes `asOf` under half-open `[start,end)` semantics.

Otherwise result is `NotCurrent`.

## ALN-004 — Covered

Result is `Covered` only when:
- Requirement is current; and
- an exact matching Access Rule contributes effective desired policy at the same `asOf`.

## ALN-005 — Uncovered

Result is `Uncovered` when:
- Requirement is current; and
- no exact matching Access Rule contributes effective desired policy at `asOf`.

Examples:
- no matching Rule exists;
- matching Rule is Inactive;
- matching Rule's EffectiveWindow excludes `asOf`.

`Uncovered` does not mean `Denied`.

## ALN-006 — Unknown

Result is `Unknown` when the composition cannot safely establish coverage because required authoritative policy information is ambiguous/unavailable.

It must never convert hidden/ambiguous/failed policy access into `Uncovered`.

## ALN-007 — Status visibility

An actor authorized to `ReadConnectivityRequirement` may receive the derived Requirement alignment status.

This does not grant:
- Rule read permission;
- Rule mutation permission;
- Effective Desired Policy browsing permission.

## ALN-008 — Rule evidence enrichment

Rule-level evidence is optional enrichment.

It may be returned only when independently authorized by Access Policy read semantics.

Without Rule-level read authority:
- `Covered` may still be returned;
- no Rule ID, Rule governance scope, decision reference, proposal provenance, EffectiveWindow or Rule audit is leaked.

## ALN-009 — No Denied result in I14

I14 exposes no `Denied` alignment status.

Current Access Policy truth contains authorized/materialized Rules, not a durable NotAllowed decision record.

Durable denial semantics remain I15/I16.

## ALN-010 — No orphan-policy result in first slice

I14 Requirement-centric owner view does not infer global policy-without-requirement orphan status.

A later policy-centric operator view may add this only after explicit authority semantics are accepted.

## ALN-011 — No persistence

Alignment is recomputed from authoritative Connectivity Requirements and Access Policy truth.

No Alignment table, aggregate, lifecycle or business audit is introduced.

## ALN-012 — Explainability

Every successful result includes enough non-sensitive explanation to distinguish:
- Requirement currentness;
- exact semantic subject;
- selected `asOf`;
- coverage outcome.

Rule evidence/provenance is included only when independently admitted.

## ALN-013 — Failure safety

Dependency failure, ambiguity or corrupted cross-context result must not produce a stronger conclusion than evidence supports.

In particular:
- unknown policy visibility/facts -> `Unknown`;
- no partial Rule evidence;
- no configured/observed conclusion.

## Trace

Strategic ownership:
- `docs/domain/capabilities.md`;
- `docs/domain/semantic-ownership.md`.

Executable examples:
- `docs/requirements/requirement-policy-alignment-acceptance-examples.md`.
