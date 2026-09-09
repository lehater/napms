# Access Policy product requirements

Status: `accepted current behavior`.

Date: 2026-09-09.

## Purpose

Define the current product behavior from application-backed connectivity proposal through authoritative Access Rule management and effective desired-policy selection.

Domain identity, invariants and command semantics are owned by `docs/domain/access-policy/tactical-model.md`. Connectivity Decision meaning is owned by its own context. This document owns externally observable Access Policy behavior.

## Proposal composition

An actor may propose connectivity only when Authority Management admits the proposal action for the relevant governance scope and effective time.

A valid proposal is formed from trusted Application Communication Catalogue facts and identifies exactly:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable DCS revision
```

The selected DCS must describe the directed interaction. The client must not create arbitrary identifier combinations and the product must not infer structural validity from technical addresses.

A proposal:
- is not an Access Rule;
- has no desired-policy effect by existing;
- does not imply a final connectivity decision.

## Decision consumption and materialization

Connectivity Decision owns the final business result for the exact proposed subject.

```text
Allowed
    -> materialize or resolve authoritative Access Rule

NotAllowed
    -> no Access Rule materialization
```

Requirements:
- the consumed Decision subject must match the exact proposal semantic identity;
- an unknown/unavailable/ambiguous Decision is not permission and is not `NotAllowed`;
- proposal authority does not imply decision authority;
- Connectivity Requirement existence does not imply `Allowed`.

The current target Decision model is defined by `docs/requirements/connectivity-decision-core.md` and ADR-005. Historical external-port deferral is not current product truth.

## Authoritative Access Rule

For one exact semantic identity there is at most one authoritative Access Rule.

On the first successful Allowed materialization:
- a stable Rule ID is created;
- Operational State is `Active`;
- the accepted proposal governance scope becomes the Rule Governance Scope;
- Decision and proposal/authority/catalogue provenance required for explanation are retained.

Retries and concurrent identical Allowed materializations must resolve the same authoritative Rule and Rule ID. They must not create duplicate authoritative Rules.

The following do not redefine Rule semantic identity:
- technical address/endpoint changes;
- responsibility/ownership changes;
- Rule Governance Scope;
- Operational State;
- EffectiveWindow.

## Authorized reads

Access Rule read authority is independent from mutation authority.

The product must support:
- authorized paged Rule listing over scopes unambiguously admitted by `ReadAccessRule`;
- authorized Rule detail by Rule ID using the Rule's stored governance scope;
- explicit not-found, denied and authority-unknown outcomes without leaking Rule data.

Read permission alone does not imply permission to change Rule state or EffectiveWindow.

## Operational State

The current Rule operational state is:

```text
Active | Inactive
```

An admitted state mutation:
- uses the authoritative Rule's stored governance scope;
- preserves Rule ID, semantic identity, Decision correlation and governance scope;
- records attributable business audit/provenance;
- commits state and audit consistently.

Requesting the already-current state is an explicit no-op and does not create a transition audit record.

No approval/request lifecycle is encoded into Operational State.

## EffectiveWindow

A Rule may have no EffectiveWindow or one absolute offset-aware half-open window:

```text
[start, end)
```

Requirements:
- `start < end`;
- changing/clearing the window requires its own admitted action;
- changing the window does not change Rule identity, Operational State or Decision correlation;
- an accepted change records business audit/provenance;
- requesting the current value is a no-op without new audit.

Recurring schedule semantics are deferred until accepted product examples require them.

## Effective desired policy

The product can select effective desired policy for one admitted Rule Governance Scope and one explicit `asOf`.

A Rule contributes only when:
- it belongs to the selected scope;
- it is `Active`;
- it has no EffectiveWindow, or `start <= asOf < end`.

Denied/unknown authority returns no policy data. An authorized empty policy is a valid empty result and is distinct from denied/unknown/technical failure.

Effective desired-policy selection is Access Policy truth. Technical realization and normalized export are downstream concerns.

## Failure and safety behavior

The system fails closed for authority, catalogue, Decision or persistence uncertainty.

In particular:
- denied/unknown proposal authority -> no valid proposal;
- structurally invalid/unknown interaction -> no valid proposal;
- `NotAllowed` -> valid business result, no Rule;
- Decision subject mismatch/ambiguity -> no Rule;
- uncertain persistence outcome is not reported as success unless the authoritative result is established;
- client-supplied actor identity, mutation time or replacement governance scope are not trusted as authority.

Operational logs do not replace durable business audit/provenance.

## Acceptance examples

1. Repeating the same exact Allowed proposal resolves one Rule ID.
2. Two concurrent identical Allowed materializations leave one authoritative Rule.
3. Changing Source, Destination or immutable DCS revision creates a different semantic subject.
4. `NotAllowed` creates no Rule.
5. An `Inactive` Rule remains authoritative but contributes no effective desired policy.
6. An Active Rule contributes only inside its EffectiveWindow when one exists.
7. A user allowed to read a Rule but not mutate it receives Rule data with mutation capability independently denied.
8. Technical endpoint changes do not create a new Access Rule.

## Canonical references

- domain semantics: `docs/domain/access-policy/tactical-model.md`;
- final Decision semantics: `docs/requirements/connectivity-decision-core.md`, ADR-005;
- architecture: `docs/architecture/current-architecture.md`;
- HTTP/runtime realization: `docs/engineering/http-api-contract.md`, `docs/engineering/current-state.md`.
