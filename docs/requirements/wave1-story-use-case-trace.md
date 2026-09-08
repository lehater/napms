# Wave-1 story/use-case trace — PLAN-026 WP-01

Status: `accepted Wave-1 behavior trace; WP-04 examples aligned`.

Date: 2026-09-08.

## Current Wave-1 chain

```text
J5 Compose/request one or more Access Rule Proposals
    -> consume Connectivity Decision: Allowed | NotAllowed
    -> Access Policy materializes/resolves authoritative Rule only for Allowed
    -> newly materialized allowed Rule starts Active
    -> maintain/select effective Rules
    -> J7 Export selected effective policy in normalized technical form
    -> STOP
```

J8 Configuration Rendering and J9 provider/device execution remain future-wave capabilities. Connectivity Decision internals are explicitly deferred.

## J5 — Propose and materialize Access Rules

### Actor / authority

Primary actor: user with effective request authority for the relevant scope/time as established by Authority Management.

Request authority does not imply `Allowed`.

### Goal

Request concrete application-backed connectivity from trusted domain objects without manually entering firewall addresses, protocol/ports or vendor syntax, then consume the decision required before an authoritative Access Rule exists.

A UI/API operation may submit `1..N` proposals together, but there is no persistent bulk `Access Request` business identity/lifecycle. Each proposed Rule is independently decided/materialized.

### Proposal identity

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable decision-relevant DCS contract/revision
```

The proposal has no authoritative Rule ID/state/effect merely by existing.

### Structural validity

A proposal is structurally valid only when required domain references resolve and the selected DCS explicitly describes a compatible directed interaction for the selected Source/Destination Component Deployments/component roles.

No separate blanket `same Application` constraint is introduced. The normal composition surface should expose only valid references/described interactions; structurally undescribed combinations are not valid proposal subjects.

### Connectivity Decision seam

```text
ConnectivityDecision
    subject = proposed Rule semantic identity
    result = Allowed | NotAllowed
    provenance/reason reference = opaque where available
```

Wave 1 deliberately does not model the internal policy/reasons/actors/workflow producing the result.

### Materialization / identity

Only `Allowed` permits Access Policy to materialize/resolve an authoritative Rule.

Exactly one authoritative Rule exists per semantic identity tuple. Repeating allowed materialization is idempotent and returns the same Rule ID. Changing Source Deployment, Destination Deployment or decision-relevant DCS semantics creates another Rule subject and requires another decision.

### Operational state / properties

Wave 1 uses:

```text
Active <-> Inactive
```

First materialization from `Allowed` starts `Active`. `Inactive` is explicit operational suspension: Rule identity/history remain but desired network effect is removed. State transitions are auditable.

Schedule/periodicity and supported frequency/duration semantics are declarative operational Rule data. They do not redefine Rule identity, do not require a new Connectivity Decision by themselves and do not periodically mutate stored `Active/Inactive` state.

### Context contributions

- **Authority Management** — effective authority for domain actions; not decision reasons.
- **Resource Catalogue** — trusted Resource/Endpoint identity and current/historical technical realization; technical realization is not Rule identity.
- **Application Communication Catalogue** — Application/Component/Deployment structure and immutable DCS communication semantics used for proposal identity/validity.
- **Access Policy** — authoritative Rule identity/uniqueness/state/properties and desired-policy projection.
- **Deferred Connectivity Decision Domain** — reasons/process behind `Allowed | NotAllowed`, only via safe consumed seam in Wave 1.

Component-to-Application and Deployment-to-Component rebinding must not silently repurpose identities already referenced by Rules. Decision-relevant DCS semantics are immutable for the referenced contract/revision.

### Outcomes / failures

Known outcomes:

- actor lacks request authority -> proposal unavailable/rejected for scope;
- invalid/unresolved domain references -> no valid proposal subject;
- no DCS-described compatible interaction -> no valid proposal subject;
- `NotAllowed` -> no authoritative Rule;
- first `Allowed` materialization -> one stable Rule ID, initial state `Active`;
- repeated same `Allowed` identity -> same Rule ID, no duplicate;
- identity-defining semantic change -> another Rule + another decision;
- `Active/Inactive` or schedule change -> same Rule/decision coverage;
- technical realization change -> same Rule; later projection recalculated;
- ownership/responsibility change -> same identity by itself; authority may change;
- `Inactive` never deletes the Rule.

Acceptance examples: `docs/target/wave1-acceptance-examples.md`.

## J7 — Export selected effective policy

Detailed trace: `docs/target/wave1-normalized-export-trace.md`.

## Deferred J8/J9

- J8 Configuration Rendering: future wave.
- J9 Provider/device execution: future wave.
