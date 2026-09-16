# Business Connectivity — target Tactical DDD model

Status: `S2 MVP Tactical model revalidated 2026-09-16; non-blocking extensions deferred`.

Accepted behavior: `docs/requirements/business-connectivity-g1.md`.

## Purpose

Own the business-purpose truth behind application connectivity without conflating that truth with security consent, concrete Component Deployment authorization or network realization.

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

The Need is **not** identified by:

- IP address/Prefix;
- Resource;
- ComponentDeployment;
- PolicyRule;
- one specific InteractionContractRevision.

The Need references stable Interaction meaning because the business requirement may outlive one technical/deployment realization or one particular immutable traffic-contract revision. Access Policy preserves the exact revision used by each submitted RuleChange.

### Sameness across technical change

A Need remains the same when:

- Resource address realization changes;
- one concrete ComponentDeployment is replaced by another realization of the same business/application role;
- several concrete Policy Rule changes are created over time to realize the same Need;
- the ACC Interaction receives a later traffic-contract revision, unless the business-required Interaction/participant meaning itself changes.

A materially different required Interaction or different dependent business participant meaning is a different Need rather than a silent mutation of its semantic identity.

### Required invariants

1. Every deliberate Connectivity Need belongs to exactly one Business Process in the first target model.
2. Every Need references an existing ACC-owned Interaction meaning rather than inventing network/IP semantics locally.
3. Need existence never implies authorization.
4. Need existence never implies network realization.
5. One Need may justify many concrete Policy Rule change attempts over time.
6. One semantic Policy Rule may be justified by several Needs; Business Connectivity does not enforce Rule uniqueness.
7. Losing/retiring one Need does not rewrite historical RuleChanges or approvals.
8. Losing all known current Needs for an authorization produces a business-justification reconciliation condition, not automatic revocation by Business Connectivity.

The exact uniqueness rule for semantically equivalent Need declarations is deferred until product behavior requires it.

## Need applicability/currentness

The domain requires a distinction between a Need that currently supplies business justification and one that no longer does, while preserving historical identity/provenance.

```text
Need applicability = Current | NotCurrent
```

These are semantic meanings, not a required storage enum or workflow state machine.

A consumer must also preserve `Unknown/Incomplete` when it cannot establish currentness from authoritative Business Connectivity truth; technical failure must not be converted into `NotCurrent`.

## Business attribution

Business attribution associates a recognized concrete access relationship or current authorization with one or more known Connectivity Needs/Processes for explanation/reconciliation.

Important semantics:

- observed traffic may exist with no attribution;
- source and destination sides may contribute attribution independently;
- absence of current attribution is not proof that access is forbidden;
- adding attribution to already authorized access does not create a duplicate Policy Rule;
- attribution does not transform observed traffic into a Need automatically.

Whether attribution becomes an independently identified durable entity is deferred until editing/history requirements demand that identity/lifecycle.

## Public semantic contract to Access Policy

For deliberate RuleChange submission Business Connectivity publishes enough trusted meaning to establish the business basis:

```text
ConnectivityNeedRef
BusinessProcessRef
required InteractionRef
current/applicable justification status
human-explainable business basis/provenance
```

Access Policy combines that stable Need basis with the exact concrete source/destination ComponentDeployment pair and exact `InteractionContractRevisionRef` proposed by the RuleChange. It preserves the basis used by the change and never infers authorization from Need existence.

Evidence-derived recognition may exist before Process/Need attribution is known. Formal deliberate submission still requires the accepted Need basis.

## Business-justification reconciliation

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
- Policy Rule/RuleChange lifecycle;
- concrete ComponentDeployment/Resource/address identity as Need identity;
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

Business Connectivity remains unchanged in its semantic center after the policy/deployment revalidation:

- Process and Need identities are application-semantic and deployment-independent;
- exact concrete ComponentDeployment pair and revision belong to Access Policy RuleChange, not Need identity;
- observed traffic may be recognized before Need attribution;
- deliberate submission requires current Process-backed business justification;
- disappearance of business justification is reconciliation input, not implicit revocation.
