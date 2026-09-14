# Business Connectivity — target Tactical DDD model

Status: `S2 target candidate`.

Date: 2026-09-14.

Strategic owner: **Business Connectivity** per ADR-019.

Accepted behavior: `docs/requirements/business-connectivity-g1.md`.

## Purpose

Own the business-purpose truth behind application connectivity without conflating that truth with security consent, concrete deployment authorization or network realization.

The core question is:

> Which business process requires which application-semantic interaction, and why is that requirement currently meaningful?

## Core model

```text
BusinessProcess
    1
    |
    | owns/describes
    v
ConnectivityNeed [0..N]
    |
    | requires
    v
Application Interaction reference
```

The context stores only opaque references to ACC-owned application/component/interaction identities. It does not copy ACC private models.

## BusinessProcess

### Identity

`BusinessProcessId` is a stable domain identity independent from display name, organizational assignment and criticality metadata.

A rename or responsibility metadata change does not create a different Process. Splitting/merging Processes is a semantic business change and is not modelled as silent identifier reuse.

### Authoritative meaning

BusinessProcess owns the NAPMS-relevant statement that a recognizable business activity/process exists and carries business responsibility/context for connectivity justification.

Minimum target facts:

- stable `BusinessProcessId`;
- human-recognizable name/title;
- business description/purpose when supplied;
- organizational-responsibility reference(s) sufficient for explanation/governance correlation;
- business importance/criticality value only when a later accepted scale exists.

Exact organization registry integration and criticality scale are deliberately outside this tactical slice.

### Lifecycle

No detailed Process workflow/state machine is currently justified by G1.

The model requires only that historical references remain explainable if a Process is later retired/replaced. Exact retirement/archive mechanics are deferred until a concrete requirement needs them.

## ConnectivityNeed

### Identity

`ConnectivityNeedId` is a stable domain identity for one enduring business requirement.

Its semantic subject is application-level, conceptually:

```text
BusinessProcessRef
+ required InteractionRef
+ dependent participant/component-role meaning
```

The domain identifier remains stable when non-identity justification metadata changes.

The Need is **not** identified by:

- IP address;
- ResourceEndpoint;
- Resource;
- concrete source/destination ComponentDeployment;
- Access Request;
- Policy Rule.

### Sameness across technical change

A Need remains the same when:

- endpoint/address realization changes;
- one concrete deployment is replaced by another deployment fulfilling the same application-semantic role;
- several concrete Access Requests are created over time to realize the same Need.

A materially different required Interaction or different dependent business participant meaning is a different Need rather than a silent mutation of its semantic identity.

### Required invariants

1. Every deliberate Connectivity Need belongs to exactly one Business Process in this first target model.
2. Every Need references an existing ACC-owned Interaction meaning rather than inventing network/IP semantics locally.
3. Need existence never implies authorization.
4. Need existence never implies network realization.
5. One Need may justify many concrete Access Requests over time.
6. One semantic Policy Rule may be justified by several Needs; Business Connectivity does not enforce Rule uniqueness.
7. Losing/retiring one Need does not rewrite historical Access Requests or approvals.
8. Losing all known current Needs for an authorization produces a business-justification reconciliation condition, not automatic revocation by Business Connectivity.

The exact uniqueness rule for semantically duplicate Need declarations is deferred until product behavior requires whether two Processes/participants may intentionally carry separately identified equivalent Needs.

## Need applicability/currentness

G1 requires a distinction between a business requirement that is current and one that no longer supplies current justification, but does not require the previous `Active -> Retired` ConnectivityRequirement state machine.

Target semantic guarantee:

```text
Need may be current/applicable
or no longer current/applicable
while its historical identity/provenance remains explainable
```

Exact state names, temporal-window model and commands are deferred to a later tactical increment unless required by a current use case.

## Business attribution

Business attribution is a relation/finding that associates a recognized deployed interaction or authorization with one or more known Connectivity Needs/Processes for explanation/reconciliation.

Important semantics:

- observed traffic may exist with no attribution;
- source and destination sides may contribute attribution independently;
- absence of current attribution is not proof that access is forbidden;
- adding attribution to already authorized access does not create a duplicate Policy Rule;
- attribution does not transform observed traffic into a Need automatically.

Whether attribution is stored as an independently identified entity or computed/recorded evidence is deferred until its editing/history requirements are specified.

## Public semantic contracts

### Need summary for Access Governance

For a deliberate request Business Connectivity must be able to publish enough trusted meaning to establish the business basis without exposing private internals:

```text
ConnectivityNeedRef
BusinessProcessRef
required InteractionRef
current/applicable justification status
human-explainable business basis
```

Access Governance must preserve the referenced basis used by the Request and must not infer authorization from it.

### Business-justification reconciliation

A consumer may ask whether one recognized/authorized interaction has zero/one/many current known Need justifications. The result must distinguish at least:

```text
Known
NoneKnown
Unknown/Incomplete
```

when data completeness makes `NoneKnown` versus `Unknown` material.

## Derived vs authoritative truth

Authoritative:
- Process identity/meaning maintained by this context;
- Connectivity Need identity/meaning/currentness maintained by this context;
- explicitly accepted attribution facts if/when recorded here.

External references:
- ACC Interaction/Component references;
- organization/responsibility references.

Derived/composition:
- whether the Need is currently authorized;
- whether technical access is realized;
- impact analysis that combines other context facts.

## Explicit non-goals

- BPMN/workflow execution;
- Process hierarchy unless later required;
- security approval/consent;
- Access Request lifecycle;
- Policy Rule lifecycle;
- concrete Deployment/IP identity as Need identity;
- firewall/network realization;
- automatic revocation when business justification disappears.

## Remaining non-blocking questions

- exact Process retirement/archive semantics;
- accepted business criticality scale and propagation rules;
- exact organization-unit/responsibility references;
- duplicate/equivalent Need declaration policy;
- durable attribution entity/history once editing/audit requirements are known;
- exact applicability/time-window representation.
