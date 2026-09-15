# ADR-019 — Keep Business Connectivity separate and unify governance with Access Policy

Status: `accepted current target decision`.

Date: 2026-09-14; revalidated 2026-09-16.

## Context

The target model must preserve several independently meaningful truths:

- Business Process / Connectivity Need explains **why** application-semantic connectivity is needed;
- concrete Component Deployments identify the exact deployed source/destination instances involved in one access relationship;
- an exact immutable Interaction Contract Revision defines the traffic semantics being proposed or currently effective;
- bilateral approval/rejection/withdrawal history explains **how** current access became or ceased to be effective;
- current Policy Rule truth determines what semantic access is currently effective.

The previous target split used separate `Access Governance` and `Access Policy` Bounded Contexts:

```text
Access Governance
    AccessRequest
    GovernedAuthorization.effectiveGrant
        -> AuthorizationGranted / AuthorizationWithdrawn

Access Policy
    PolicyRule current authorization
```

After requirements revalidation, this creates duplicate ownership of one current-access fact. Access Policy does not make an independent decision after governance; it merely mirrors the effective grant for the same concrete connection.

The revalidated product behavior also requires a pending/rejected revision change to coexist with an already effective revision of the **same Policy Rule**. This is one rule lifecycle rather than two independently evolving authoritative lifecycles.

## Decision

### 1. Business Connectivity remains a distinct Bounded Context

**Semantic center:** why is application connectivity needed by the business?

Business Connectivity owns:

- Business Process identity/meaning;
- Connectivity Need identity/lifecycle/currentness;
- application-semantic required `InteractionRef`;
- business attribution/justification reconciliation.

A Need is independent from concrete Component Deployment, Resource, address and exact contract revision.

Observed brownfield traffic may be recognized before Process/Need attribution is known. Deliberate policy-change submission still requires the accepted Process-backed Need/business basis.

### 2. Access Governance is absorbed into Access Policy

**Semantic center:** what concrete access relationship exists as a Policy Rule, what change is proposed, what governance decisions apply, and what revision is currently effective?

Access Policy owns one complete concrete-rule lifecycle:

```text
PolicyRule
    PolicyRuleId
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    effectiveRevisionRef?
    RuleChange[]
    approval/withdrawal history
```

Governance is an internal domain capability of Access Policy, not a peer Bounded Context.

The Rule's concrete subject is the directed source/destination Component Deployment pair. The exact `revisionRef` is proposed/current traffic semantics and is not part of Rule identity.

A `RuleChange` preserves one formal attempt to establish/change the Rule revision, including business/evidence provenance, approval basis and bilateral decisions.

Pending/rejected changes do not overwrite current effective policy. An accepted applicable change may advance the same Policy Rule to another immutable revision.

Withdrawal clears current effectiveness without deleting the Rule or rewriting history. Reauthorization requires a new change attempt under then-current obligations.

### 3. Policy Rule is created before first approval

A Policy Rule may exist with no current effective revision while its first RuleChange is pending or after that initial attempt is rejected.

This avoids a parallel top-level Proposal aggregate whose identity/lifecycle would duplicate the Rule it is trying to establish.

Separate RuleChange identity remains semantically justified because multiple attempts for the same Rule/revision at different times must preserve different approval/provenance histories.

### 4. Authority Management remains separate

Authority Management owns whether Actor A may perform Action X for Responsibility Scope S at time T.

Access Policy consumes effective authority results for submission/approval/withdrawal. It does not infer authority from Resource owner/administrator/contact metadata and does not import AM private role/group models.

### 5. Concrete deployment ownership remains outside Access Policy

Application Deployment owns target `ComponentDeployment` identity and the exact:

```text
ComponentDeploymentRef -> ComponentRef + ResourceRef
```

relation.

Resource Catalogue owns Resource AddressSpace and Resource Scope Affiliation.

Access Policy combines public facts only to validate revision endpoints and derive governance obligations; it does not copy deployment/resource ownership.

### 6. Evidence-derived proposals use the same rule lifecycle

Technical Access Evidence remains evidence-only.

A non-peer Evidence Access Recognition composition may correlate TAE predicates through RC + Application Deployment + ACC and produce:

```text
RecognizedAccessCandidate {
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    revisionRef
    evidenceProvenance
}
```

That candidate may seed the same Access Policy RuleChange flow as manual creation. Recognition does not authorize access and does not bypass the Business Connectivity/authority requirements for formal submission.

## Primary semantic contracts

### Business Connectivity -> Access Policy

Purpose: supply business basis for a deliberate RuleChange.

```text
ConnectivityNeedRef
BusinessProcessRef
required InteractionRef
current/applicable justification status
explainable provenance
```

Need existence is not authorization.

### ACC -> Access Policy

Purpose: supply exact immutable traffic and endpoint Component meaning.

```text
InteractionContractRevisionRef
    -> owning Interaction
    -> sourceComponentRef
    -> destinationComponentRef
    -> complete traffic alternatives
```

A duplicate `InteractionRef` is unnecessary when an exact revision is already present.

### Application Deployment -> Access Policy

```text
ComponentDeploymentRef
    -> ComponentRef
    -> ResourceRef
```

The RuleChange is valid only when source/destination deployment Components match the exact revision's Interaction endpoints.

### Resource Catalogue -> Access Policy

```text
ResourceRef + logicalTime
-> effective ResourceScopeAffiliation[]
```

Access Policy derives source/destination approval obligations from these public facts. The MVP requires exactly one distinct applicable scope per side.

### Authority Management -> Access Policy

```text
actor + action + scope + time
-> admitted | denied | unknown
+ authority provenance
```

Denied/unknown fail closed.

### Access Policy -> downstream policy materialization

```text
EffectivePolicyRule {
    policyRuleRef
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    revisionRef
    authorizationProvenance
}
```

Pending/rejected RuleChanges are not current effective policy.

## Identity and change consequences

- PolicyRuleId is stable across approved revision changes for the same concrete directed Component Deployment pair.
- `PolicyRuleRef` is the opaque external reference to that identity.
- replacing either Component Deployment means a different concrete Rule subject;
- changing Resource AddressSpace does not change the Rule subject;
- changing traffic creates a new ACC revision but does not alter an existing Rule until an approved RuleChange activates that revision;
- rejected/pending changes never replace current effective revision;
- old approvals cannot silently restore withdrawn effectiveness.

## Consequences

- there is one authoritative owner for current concrete access rather than AG grant plus AP mirror;
- proposal/governance/current-rule semantics are one cohesive lifecycle while historical and current truth remain distinct;
- Business Need remains independently reusable and explainable;
- Authority Management remains reusable across protected actions;
- evidence-derived and manual access follow one governance path;
- downstream consumers receive stable PolicyRule references without knowing approval internals;
- migration from implemented legacy Connectivity Decision/Access Rule and ACC compatibility identities remains an Architecture/Implementation concern rather than target domain ownership.

## Rejected alternatives

### Keep Access Governance and Access Policy as separate target BCs

Rejected for the revalidated target because `GovernedAuthorization.effectiveGrant` and AP current Policy Rule would both own the same current authorization fact without an independent AP decision/lifecycle.

### Make Proposal a separate top-level aggregate/BC

Rejected for the first MVP because the proposal exists only to establish/change one Policy Rule. A child RuleChange identity is sufficient to preserve distinct attempts while avoiding a second competing rule lifecycle.

### Put business Need inside Access Policy

Rejected because business-purpose truth can exist/change independently from concrete authorization and may justify several concrete Rules over time.
