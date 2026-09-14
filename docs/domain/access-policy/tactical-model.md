# Access Policy — target Tactical DDD model

Status: `S2 target candidate`.

Date: 2026-09-14.

Accepted behavior: `docs/requirements/access-policy-core.md`.

Strategic owner: **Access Policy** per ADR-019.

## Purpose

Own current authoritative semantic Policy Rule truth after Access Governance has granted or withdrawn authorization for an exact deployed interaction subject.

Access Policy does not own the Request/approval/revocation workflow that produces those authorization facts.

## RuleSemanticIdentity

Immutable value object:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
+ interactionContractRevisionRef
```

Equality is structural over those three trusted ACC identities.

Not part of semantic identity:
- ResourceEndpoint/IP realization;
- actor identity;
- business Process/Need references;
- AccessRequest identity;
- approval history;
- provider/firewall realization.

Changing either ComponentDeployment or the Interaction contract revision yields a different semantic subject. Address/Endpoint changes on the same Resource do not.

## PolicyRule

### Identity

`PolicyRuleId` is a stable domain identity for one authoritative Rule record associated with one immutable `RuleSemanticIdentity`.

For one exact semantic identity there shall be at most one authoritative current Policy Rule meaning.

Repeated/concurrent processing of equivalent authorization grants must resolve that same Rule identity rather than create duplicates.

### Authoritative facts

Minimum target facts:

- stable `PolicyRuleId`;
- immutable `RuleSemanticIdentity`;
- current authorization effectiveness derived from the latest accepted Access Governance grant/withdrawal basis;
- correlation/provenance sufficient to explain the authorization basis that established or withdrew current effect;
- historical correlation sufficient to explain prior authorization epochs without copying the Access Governance journal.

The Rule may retain stable identity across withdrawal and later explicit reauthorization, but exact revision/reactivation representation is not fixed by current requirements. The invariant is one authoritative semantic Rule meaning per subject and no silent reauthorization.

## Authorization basis consumption

Access Policy consumes only explicit Access Governance semantic facts for the exact subject:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

### Grant

On a valid `AuthorizationGranted` for subject S:

1. validate exact subject identity;
2. resolve the authoritative Rule for S or create it if none exists;
3. establish S as currently effectively authorized under that explicit grant basis;
4. preserve enough provenance/correlation to explain the transition;
5. repeated delivery of the same grant basis is idempotent;
6. concurrent equivalent first grants cannot create multiple authoritative Rules for S.

### Withdrawal

On a valid `AuthorizationWithdrawn` for subject S:

1. resolve the authoritative Rule for S if it exists;
2. make S no longer contribute to current effective authorized policy;
3. preserve Rule identity and historical authorization provenance;
4. do not rewrite historical Request/approval facts;
5. do not create a semantic deny Rule;
6. do not allow an old historical grant to make the subject effective again without a new explicit Access Governance authorization action.

If no Rule exists for a withdrawal subject, the operation must not invent an authorized Rule. Exact diagnostic/idempotent non-result is an application concern as long as authoritative state remains not authorized.

## Current effective authorization

The target domain distinction is:

```text
Rule exists historically
!=
Rule currently contributes to effective authorized policy
```

A Rule contributes to effective authorized policy only when a valid current Access Governance authorization basis exists and any later accepted applicability constraints are satisfied.

The previous `Active | Inactive` operational state and `EffectiveWindow` model are not carried forward automatically as target truth. They remain current-state evidence until a specific accepted behavior justifies equivalent target semantics.

Time-bounded authorization is a valid product direction, but exact state/window/revision representation remains deferred.

## Business justification provenance

Several Connectivity Needs and several approved Requests may support the same semantic Policy Rule.

Access Policy may retain correlation references needed to explain authorization provenance, but:

- Connectivity Need identity/lifecycle remains Business Connectivity truth;
- Request/side-decision/grant history remains Access Governance truth;
- losing one Need does not by itself withdraw the Rule;
- rejection of a Request does not create a deny Rule;
- loss of all current known Needs is a reconciliation finding, not automatic Access Policy revocation unless a later policy explicitly requires it.

## Public semantic projection

Access Policy shall publish current effective authorized semantic Rules for admitted consumers.

Conceptually:

```text
EffectiveAuthorizedPolicy(asOf/context)
    -> PolicyRule[0..N]
```

Each selected Rule supplies its stable semantic subject and authorization provenance/freshness semantics required by the consumer contract.

Technical translation to ResourceEndpoint/IP prefixes, protocol/port predicates, enforcement locations, provider rules or rendered configuration is downstream and does not alter Rule identity.

## Cross-context contracts

### ACC -> Access Policy

Provides trusted `RuleSemanticIdentity` references and immutable interaction-contract meaning.

### Access Governance -> Access Policy

Provides `AuthorizationGranted` / `AuthorizationWithdrawn` facts for the exact subject. Access Policy must not inspect peer-private Request/ApprovalObligation/SideDecision state to recompute bilateral consent.

### Business Connectivity -> Access Policy

No direct authorization dependency is required. Business Need/provenance may be correlated for explanation/reconciliation, but Need existence is not permission.

### Authority Management -> Access Policy

Authority Management may admit Access Policy read/administrative actions required by product use cases. Such authority is independent from Access Governance approval authority.

## Concurrency / uniqueness invariant

The semantic invariant is:

> one exact RuleSemanticIdentity resolves to one authoritative PolicyRule identity.

The implementation must enforce first-materialization/idempotency strongly enough that retries/concurrency do not create duplicate authoritative Rules. Database unique constraints/locking are implementation mechanisms, not the source of the invariant.

## Authoritative vs derived state

Authoritative in Access Policy:
- PolicyRule identity;
- immutable RuleSemanticIdentity;
- current semantic authorization effectiveness according to consumed grant/withdrawal facts;
- Access Policy-owned provenance/correlation required to explain that current/historical Rule state.

External truth:
- ACC subject validity/meaning;
- Access Governance request/decision/consent history;
- Business Connectivity Need/Process truth;
- Resource technical realization;
- actor authority.

Derived/downstream:
- technical traffic predicates;
- enforcement targets;
- configured-vs-required reconciliation;
- rendered/provider configuration.

## Explicit non-goals

- bilateral approval workflow;
- durable `NotAllowed` rule created from rejection;
- Resource/IP identity inside RuleSemanticIdentity;
- provider/firewall rule identity;
- preserving previous `Active/Inactive`, proposal or single ConnectivityDecision concepts solely because current code has them.

## Remaining non-blocking questions

- whether one long-lived PolicyRule or explicit authorization revisions best represent repeated grant/withdraw/regrant epochs;
- exact time-bounded authorization semantics and representation;
- any independently user-controlled administrative suspension capability, if later required;
- exact read-governance scope model after Access Governance/Authority Management revalidation;
- precise provenance projection needed by UI/audit consumers.
