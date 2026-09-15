# Business Connectivity — target Tactical DDD model

Status: `S2 MVP Tactical model accepted 2026-09-15; non-blocking extensions deferred`.

Date: 2026-09-15.

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
ACC InteractionRef
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
- business importance/criticality only when a later accepted scale exists.

Exact organization registry integration and criticality scale are outside the MVP Tactical requirement.

### Lifecycle classification

No detailed Process workflow/state machine is justified by current accepted behavior.

The domain guarantee is only that historical Process references remain explainable if a Process later ceases to be current. Exact retirement/archive mechanics are deferred until a concrete product journey needs them.

## ConnectivityNeed

### Identity

`ConnectivityNeedId` is a stable domain identity for one enduring business requirement.

Its semantic subject is application-level:

```text
BusinessProcessRef
+ required InteractionRef
+ dependent participant/component-role meaning
```

The domain identifier remains stable when non-identity justification metadata changes.

The Need is **not** identified by:

- IP address/Prefix;
- Resource;
- ComponentPlacement;
- ApplicationDeployment;
- Access Request;
- Policy Rule;
- one specific InteractionContractRevision.

The Need references stable Interaction meaning because the business requirement may outlive one technical/deployment realization or one particular immutable traffic-contract revision. Access Governance chooses/preserves the exact `InteractionContractRevisionRef` used by each concrete governed Request.

### Sameness across technical change

A Need remains the same when:

- Resource address realization changes;
- Component placement changes while the same application-semantic participant role remains;
- one logical ApplicationDeployment is replaced by another realization of the same business/application need;
- several concrete Access Requests are created over time to realize the same Need;
- the ACC Interaction receives a later traffic-contract revision, unless the business-required Interaction/participant meaning itself changes.

A materially different required Interaction or different dependent business participant meaning is a different Need rather than a silent mutation of its semantic identity.

### Required invariants

1. Every deliberate Connectivity Need belongs to exactly one Business Process in the first target model.
2. Every Need references an existing ACC-owned Interaction meaning rather than inventing network/IP semantics locally.
3. Need existence never implies authorization.
4. Need existence never implies network realization.
5. One Need may justify many concrete Access Requests over time.
6. One semantic Policy Rule may be justified by several Needs; Business Connectivity does not enforce Rule uniqueness.
7. Losing/retiring one Need does not rewrite historical Access Requests or approvals.
8. Losing all known current Needs for an authorization produces a business-justification reconciliation condition, not automatic revocation by Business Connectivity.

The exact uniqueness rule for semantically equivalent Need declarations is deferred until product behavior requires whether separate Processes/participants may intentionally carry separately identified equivalent Needs.

## Need applicability/currentness

The domain requires a distinction between a Need that currently supplies business justification and one that no longer does, while preserving historical identity/provenance.

```text
Need applicability = Current | NotCurrent
```

These are semantic meanings, not a required storage enum or workflow state machine.

A consumer must also preserve `Unknown/Incomplete` when it cannot establish currentness from authoritative Business Connectivity truth; technical failure must not be converted into `NotCurrent`.

Exact temporal-window representation is downstream design unless a product journey requires scheduled business-validity semantics.

## Business attribution

Business attribution associates a recognized deployed interaction or authorization with one or more known Connectivity Needs/Processes for explanation/reconciliation.

Important semantics:

- observed traffic may exist with no attribution;
- source and destination sides may contribute attribution independently;
- absence of current attribution is not proof that access is forbidden;
- adding attribution to already authorized access does not create a duplicate Policy Rule;
- attribution does not transform observed traffic into a Need automatically.

Whether attribution becomes an independently identified durable entity is deferred until editing/history requirements demand that identity/lifecycle.

## Public semantic contracts

### Need basis for Access Governance

For a deliberate request Business Connectivity publishes enough trusted meaning to establish the business basis:

```text
ConnectivityNeedRef
BusinessProcessRef
required InteractionRef
current/applicable justification status
human-explainable business basis/provenance
```

Access Governance combines that stable Need with the exact concrete `InteractionContractRevisionRef + source/destination ApplicationDeploymentRef` governed subject. It preserves the basis used by the Request and never infers authorization from Need existence.

### Business-justification reconciliation

A consumer may ask whether one recognized/authorized interaction has current known Need justifications. The result distinguishes:

```text
Known
NoneKnown
Unknown/Incomplete
```

`NoneKnown` is valid only from complete authoritative knowledge; unknown evidence is not absence.

## Derived vs authoritative truth

Authoritative:

- Process identity/meaning;
- Connectivity Need identity/meaning/currentness;
- explicit attribution facts if/when recorded here.

External references:

- ACC Interaction/Component references;
- organization/responsibility references.

Derived/composition:

- whether the Need is currently authorized;
- whether technical access is realized;
- impact analysis combining peer context facts.

## Explicit non-goals

- BPMN/workflow execution;
- Process hierarchy unless later required;
- security approval/consent;
- Access Request lifecycle;
- Policy Rule lifecycle;
- concrete ApplicationDeployment/Resource/address identity as Need identity;
- firewall/network realization;
- automatic revocation when business justification disappears.

## Deliberately deferred non-blocking extensions

- exact Process retirement/archive mechanics;
- business criticality scale and propagation rules;
- exact organization-unit/responsibility reference semantics;
- duplicate/equivalent Need declaration policy;
- durable attribution identity/history;
- scheduled/time-window representation beyond Current/NotCurrent meaning.

## Tactical coherence result

Business Connectivity is sufficient for the first MVP DDD baseline:

- Process and Need identities are explicit;
- Need is application-semantic and independent of deployment/address realization;
- currentness needed for deliberate request justification is explicit;
- exact governed contract revision remains AG/ACC truth, not Need identity;
- disappearance of business justification is reconciliation input, not implicit revocation;
- remaining questions are future extensions and do not require implementation invention for the happy path.
