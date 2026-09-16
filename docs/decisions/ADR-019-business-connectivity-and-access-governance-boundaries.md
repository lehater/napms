# ADR-019 — Keep Business Connectivity separate and unify formal policy decisions with Access Policy

Status: `accepted current target decision`.

Date: 2026-09-14; revalidated 2026-09-16.

## Context

The target model must preserve several independently meaningful truths:

- Business Process / Connectivity Need explains **why** application-semantic connectivity is needed;
- concrete Component Deployments identify the exact deployed source/destination instances involved in one access relationship;
- an exact immutable Interaction Contract Revision defines the traffic semantics being proposed or currently effective;
- RuleChange history preserves what was proposed and the formal Accepted/Rejected outcome;
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

The product also requires a Pending/Rejected revision change to coexist with an already effective revision of the **same Policy Rule**. This is one rule lifecycle rather than two independently evolving authoritative lifecycles.

A later 2026-09-16 revalidation further established that the first MVP does not need an embedded bilateral approval workflow. Different adopters may use different procedures. NAPMS baseline semantics need only the formal RuleChange outcome that is necessary to change current policy.

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

**Semantic center:** what concrete access relationship exists as a Policy Rule, what change is proposed, what formal decision was made, and what revision is currently effective?

Access Policy owns one complete concrete-rule lifecycle:

```text
PolicyRule
    PolicyRuleId
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    effectiveRevisionRef?
    RuleChange[]
    withdrawal history
```

Governance is not a peer Bounded Context. The baseline policy-decision capability is internal to Access Policy.

The Rule's concrete subject is the directed source/destination Component Deployment pair. The exact `revisionRef` is proposed/current traffic semantics and is not part of Rule identity.

A `RuleChange` preserves one formal attempt to establish/change the Rule revision, including business/evidence provenance and one state:

```text
Pending -> Accepted | Rejected
```

Pending/Rejected changes do not overwrite current effective policy. An Accepted applicable change may advance the same Policy Rule to another immutable revision.

Withdrawal clears current effectiveness without deleting the Rule or rewriting history. Reauthorization requires a new explicit RuleChange and Accepted decision.

### 3. Customer approval workflow is outside the MVP domain baseline

The first MVP does not require Access Policy to model:

- source-side and destination-side approvers;
- approval obligation/basis snapshots;
- Responsibility Scope-derived approval routing;
- quorum or ordering;
- CAB/ticket/workflow stages;
- internals of an external approval product.

An organization-specific process may occur manually or in an external system. Once that process reaches a final outcome, an authorized caller/integration may record the formal `Accepted` or `Rejected` decision on the RuleChange.

This preserves extensibility without turning NAPMS into a general approval workflow engine.

### 4. Policy Rule is created before first acceptance

A Policy Rule may exist with no current effective revision while its first RuleChange is Pending or after that initial attempt is Rejected.

This avoids a parallel top-level Proposal aggregate whose identity/lifecycle would duplicate the Rule it is trying to establish.

Separate RuleChange identity remains semantically justified because multiple attempts for the same Rule/revision at different times must preserve different decision/provenance histories.

### 5. Authority Management remains separate

Authority Management owns whether Actor A may perform Action X for Responsibility Scope S at time T.

Access Policy may consume effective authority results to protect propose/decide/withdraw application actions, according to the deployed authority configuration. It does not infer authority from Resource owner/administrator/contact metadata and does not import AM private role/group models.

This authority check is not itself an approval workflow and does not imply multiple approvers or endpoint-derived approval obligations.

### 6. Concrete deployment ownership remains outside Access Policy

Application Deployment owns target `ComponentDeployment` identity and the exact:

```text
ComponentDeploymentRef -> ComponentRef + ResourceRef
```

relation.

Resource Catalogue owns Resource AddressSpace, Scope Affiliation and Responsibility. AP does not need RC scope facts merely to accept/reject a baseline RuleChange.

Access Policy combines ACC/AD public facts to validate revision endpoints; it does not copy deployment/resource ownership.

### 7. Evidence-derived proposals use the same rule lifecycle

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

That candidate may seed the same Access Policy RuleChange flow as manual creation. Recognition does not authorize access and does not bypass the Business Connectivity requirement for deliberate submission or the formal Accepted decision.

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

### Authority Management -> Access Policy

Optional protected-action admission:

```text
actor + action + configured authority scope/time
-> admitted | denied | unknown
+ authority provenance
```

Denied/unknown fail closed when the action is protected. This contract does not prescribe the approval process that produced the formal decision.

### Access Policy -> downstream policy materialization

```text
EffectivePolicyRule {
    policyRuleRef
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    revisionRef
    decisionProvenance
}
```

Pending/Rejected RuleChanges are not current effective policy.

## Identity and change consequences

- PolicyRuleId is stable across Accepted revision changes for the same concrete directed Component Deployment pair.
- `PolicyRuleRef` is the opaque external reference to that identity.
- replacing either Component Deployment means a different concrete Rule subject;
- changing Resource AddressSpace does not change the Rule subject;
- changing traffic creates a new ACC revision but does not alter an existing Rule until an Accepted RuleChange activates that revision;
- Pending/Rejected changes never replace current effective revision;
- old Accepted changes cannot silently restore withdrawn effectiveness.

## Consequences

- there is one authoritative owner for current concrete access rather than AG grant plus AP mirror;
- proposal/formal-decision/current-rule semantics are one cohesive lifecycle while historical and current truth remain distinct;
- NAPMS does not prematurely standardize customer-specific approval procedure;
- Business Need remains independently reusable and explainable;
- Authority Management remains reusable across protected actions;
- evidence-derived and manual access follow one RuleChange decision path;
- downstream consumers receive stable PolicyRule references without knowing decision-workflow internals;
- migration from implemented legacy Connectivity Decision/Access Rule and ACC compatibility identities remains an Architecture/Implementation concern rather than target domain ownership.

## Rejected alternatives

### Keep Access Governance and Access Policy as separate target BCs

Rejected because `GovernedAuthorization.effectiveGrant` and AP current Policy Rule would both own the same current authorization fact without an independent AP decision/lifecycle.

### Make Proposal a separate top-level aggregate/BC

Rejected for the first MVP because the proposal exists only to establish/change one Policy Rule. A child RuleChange identity is sufficient to preserve distinct attempts while avoiding a second competing rule lifecycle.

### Encode bilateral approval workflow in the MVP core

Rejected because the product currently requires only a formal allow/reject decision and customer procedures differ. Encoding endpoint-side approvals, scope-derived approvers or quorum would add domain complexity without accepted MVP behavior requiring it.

### Put business Need inside Access Policy

Rejected because business-purpose truth can exist/change independently from concrete authorization and may justify several concrete Rules over time.
