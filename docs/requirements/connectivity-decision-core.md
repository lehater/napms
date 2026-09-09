# Connectivity Decision Core Requirements

Status: `accepted I15 baseline`.

Date: 2026-09-09.

## REQ-CD-001 — Own durable final connectivity decisions

Connectivity Decision shall own durable final `Allowed | NotAllowed` decisions independently from Access Policy, Connectivity Requirements and Authority Management.

Each Decision has a stable DecisionId and exact RuleSemanticIdentity subject.

## REQ-CD-002 — Preserve exact subject and governance scope

A Decision shall preserve:
- exact Source Component Deployment;
- exact Destination Component Deployment;
- immutable DCS revision;
- stable Decision Governance Scope.

The first model uses the accepted proposal authority scope as Decision Governance Scope.

Subject/scope mismatch must fail closed.

## REQ-CD-003 — Separate proposal authority from decision authority

Authority Management shall independently admit:
- `DecideConnectivity`;
- `ReadConnectivityDecision`.

`ProposeConnectivity` shall not imply decision or read authority.

One unambiguous effective `DecideConnectivity` authority is sufficient in the first model.

## REQ-CD-004 — Keep final outcome binary

A final business Decision outcome shall be exactly:

`Allowed | NotAllowed`

Missing, expired, inaccessible, ambiguous or technically uncertain Decisions shall not be converted into Allowed/NotAllowed.

No approval-state lifecycle is required by I15.

## REQ-CD-005 — Record reason and provenance

Every Decision shall record:
- non-empty reason code;
- non-empty human-readable reason;
- deciding principal;
- decision time;
- effective Authority reference;
- subject/proposal correlation.

Optional evidence references may point to authoritative facts in other contexts.

## REQ-CD-006 — Treat requirements as evidence, not authorization

A Decision may reference Connectivity Requirements as decision evidence.

The product shall preserve:

`Required != Authorized`

Declaring/changing/retiring a Requirement shall not itself create, alter or supersede a Decision.

## REQ-CD-007 — Use explicit decision validity

Every Decision shall have offset-aware `validFrom` and optional `validUntil` with half-open semantics.

Access Policy may consume a Decision only when it is effective at the proposal logical time.

Decision expiry shall not silently mutate an existing Access Rule.

## REQ-CD-008 — Represent reconsideration by immutable supersession

A reconsideration shall create a new Decision rather than editing an existing Decision.

A superseding Decision shall:
- have the same subject and governance scope;
- reference the immediately superseded Decision;
- preserve the historical record.

At most one current effective Decision may be selected for one subject/scope/asOf.

## REQ-CD-009 — Fail closed on no trustworthy effective decision

When no single trustworthy effective Decision can be selected, the proposal/materialization flow shall not materialize a new Access Rule.

Ambiguity, persistence uncertainty and unavailable decision data remain explicit non-success outcomes.

## REQ-CD-010 — Keep existing Rule lifecycle in Access Policy

An Allowed Decision may authorize Access Policy to materialize/resolve a Rule.

A later Decision expiry or supersession shall not silently change an already existing Rule's operational state in I15/I16.

Any automatic revocation/change-management behavior requires its own accepted requirement.
