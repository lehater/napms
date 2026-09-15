# Access Policy — target Tactical DDD model

Status: `S2 MVP Tactical model revalidated 2026-09-16`.

## Purpose

Own one durable Policy Rule lifecycle for a concrete directed Component Deployment pair, including proposed traffic-revision changes, bilateral governance decisions/history, current effective revision and withdrawal.

Access Policy does not own Application/Component/Interaction meaning, Component Deployment truth, Resource/scope truth or actor authority. It consumes those owners through public semantic references/contracts.

## Aggregate root — PolicyRule

```text
PolicyRule {
    policyRuleId
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    lifecycle: Active | Retired
    effectiveRevisionRef?
    changes: RuleChange[]
    currentAuthorizationBasis?
    authorizationHistory[]
}
```

`PolicyRule` exists before it necessarily contributes effective access. A newly submitted initial change may create an Active Rule with no `effectiveRevisionRef` while approval is pending or after that first attempt is rejected.

### Policy Rule identity / sameness

`policyRuleId` is the stable Access Policy-owned semantic identity.

The Rule's business uniqueness is the directed pair:

```text
(sourceComponentDeploymentRef,
 destinationComponentDeploymentRef)
```

For the first MVP there is at most one non-Retired Policy Rule for one exact directed pair.

Consequences:

- `A -> B` and `B -> A` are different Rule subjects;
- replacing either Component Deployment produces a different concrete subject and therefore a different Rule;
- changing only the traffic revision does not create a different Policy Rule;
- Resource AddressSpace change does not change Rule identity while the Component Deployment identities remain unchanged;
- `revisionRef` is current/proposed traffic semantics, not Rule identity.

The external semantic reference used by other contexts/compositions is `PolicyRuleRef`. `PolicyRuleId` is the identity name inside Access Policy. They may share one runtime value, but external consumers depend only on opaque reference meaning.

## Endpoint and revision consistency

Each `RuleChange.revisionRef` resolves through ACC to one exact immutable Interaction Contract Revision and its owning Interaction endpoint Components.

A Rule change is semantically valid only when:

```text
source ComponentDeployment.componentRef
    == revision.Interaction.sourceComponentRef

destination ComponentDeployment.componentRef
    == revision.Interaction.destinationComponentRef
```

Because ACC Interactions are intra-Application, this invariant prevents cross-Application Policy Rules.

The Rule does not carry a duplicate `InteractionRef` solely to recover meaning already available from `revisionRef`.

## Child entity — RuleChange

A `RuleChange` is one deliberate attempt to establish or change the traffic revision of a Policy Rule.

```text
RuleChange {
    ruleChangeId
    revisionRef
    origin: Manual | EvidenceDerived
    processConnectivityNeedRef
    businessJustification
    evidenceProvenance[]
    approvalBasis: ApprovalBasisSnapshot
    sourceDecision?
    destinationDecision?
    state: Pending | Approved | Rejected
    submittedAt
    submittedBy
}
```

`RuleChange` has identity because two attempts may request the same revision at different times, under different approval/business/evidence bases, and must remain distinguishable historically.

It is a child entity of `PolicyRule`, not a second Aggregate Root and not a separate Policy/Proposal lifecycle owner.

A retry of one already-established submission must not create a second semantic change attempt merely because transport was retried; exact idempotency-key realization is Architecture/Implementation work.

### Submission boundary

A durable `RuleChange` represents a formally submitted governance attempt.

A `RecognizedAccessCandidate` from evidence correlation is a non-authoritative input value and need not have durable entity identity. It may pre-populate/propose:

```text
sourceComponentDeploymentRef
destinationComponentDeploymentRef
revisionRef
evidenceProvenance
```

but formal submission still requires the accepted Process-backed Connectivity Need/business basis and current approval obligations.

Manual drafts before formal submission likewise need not be domain entities unless later product behavior requires durable drafts.

## Approval basis

At RuleChange submission, Access Policy resolves current governance obligations from published owner truth:

```text
source/destination ComponentDeployment
    -> ResourceRef
    -> RC effective ResourceScopeAffiliation

actor + action + ResponsibilityScopeRef + time
    -> AM EffectiveAuthority
```

For MVP, each side must resolve to exactly one distinct applicable Responsibility Scope.

```text
ApprovalBasisSnapshot {
    sourceResponsibilityScopeRef
    destinationResponsibilityScopeRef
    resolvedAt
    upstreamProvenance[]
}
```

Zero or several applicable distinct scopes on either side is unresolved and the change cannot be submitted/authorized through the first MVP path.

The snapshot preserves the decision basis without copying ownership of RC/AM private state.

## ApprovalDecision value

Each RuleChange can hold at most one terminal decision per required side:

```text
ApprovalDecision {
    side: Source | Destination
    result: Approved | Rejected
    actorRef
    decidedAt
    authorityEvidenceRef
    provenanceRef
}
```

AM authority is checked for the relevant action/scope/time. Resource responsibility/contact metadata is not authority.

A rejection makes that RuleChange terminal `Rejected` and never creates a deny Policy Rule.

## Change activation

A RuleChange may become `Approved` and update `effectiveRevisionRef` only when:

1. both required sides are Approved;
2. the approved basis still materially matches current source/destination obligations;
3. endpoint/revision compatibility still holds;
4. the Rule is Active;
5. the change is still applicable to the Rule's current state.

When approved:

```text
PolicyRule.effectiveRevisionRef = RuleChange.revisionRef
RuleChange.state = Approved
```

The same `PolicyRuleId` is retained.

Pending or Rejected changes never modify `effectiveRevisionRef`.

### First authorization

For a new Rule:

```text
PolicyRule.effectiveRevisionRef = null
RuleChange(R1) = Pending
```

After both approvals:

```text
PolicyRule.effectiveRevisionRef = R1
RuleChange(R1) = Approved
```

If rejected, the Rule remains durable and non-effective with the rejected historical attempt preserved.

### Revision change

For an effective Rule on `R1`:

```text
PolicyRule.effectiveRevisionRef = R1
RuleChange(R2) = Pending
```

While Pending or after Rejection, `R1` remains effective.

Only approval of the applicable R2 change moves the same Rule to `R2`.

## Concurrent/pending change boundary

The first MVP allows at most one `Pending` RuleChange per Active PolicyRule.

This prevents two independently approved pending revisions from requiring an unaccepted conflict-resolution/ordering rule. A new change may be submitted after the existing Pending change reaches a terminal outcome.

This is an MVP domain boundary, not a database-locking prescription.

## Current authorization / withdrawal

`effectiveRevisionRef != null` means the Rule currently contributes semantic access.

Withdrawal clears current effectiveness without deleting the Rule or rewriting its approved/rejected history:

```text
WithdrawPolicyRule
    -> effectiveRevisionRef = null
    -> append AuthorizationWithdrawal record/provenance
```

Withdrawal may result from an authorized side withdrawing consent or from an accepted obligation-change rule when current scope facts no longer satisfy the basis under which access is effective.

Old approved RuleChanges cannot silently restore `effectiveRevisionRef` after withdrawal.

Reauthorization requires a new RuleChange under then-current obligations, even when it proposes the same immutable revision as a previously approved change.

## Authorization history

The Rule preserves immutable explainability records sufficient to show:

- which RuleChange established each effective revision;
- which approval basis and side decisions supported it;
- why/when current effectiveness was withdrawn;
- evidence/business provenance associated with each attempt.

Exact persistence shape may be normalized tables, event records or another architecture mechanism; Tactical DDD requires the semantic history, not one storage form.

## Lifecycle

Aggregate lifecycle is distinct from effective-policy state:

```text
Active -> Retired
```

An Active Rule may be effective or non-effective. `effectiveRevisionRef = null` does not by itself mean Retired.

A Retired Rule remains historically addressable and accepts no new RuleChanges. There is no normal semantic hard delete or reactivation of a Retired Rule in the first MVP.

Withdrawal is not retirement.

## Minimal semantic operations

```text
SubmitInitialRuleChange
SubmitRuleChange
RecordApprovalDecision
ApproveApplicableRuleChange
WithdrawCurrentAuthorization
RetirePolicyRule
```

Names express domain meaning, not frozen API command names.

`SubmitInitialRuleChange` creates/reuses the one Rule for the directed pair and records its first submitted change.

`SubmitRuleChange` requires no other Pending change for that Rule.

`RecordApprovalDecision` preserves actor/time/authority provenance and never rewrites an earlier terminal decision.

`ApproveApplicableRuleChange` updates current effective revision only after all current semantic conditions hold.

## Published current-policy contract

Downstream consumers do not need proposal/approval internals. Access Policy publishes current effective Rule meaning equivalent to:

```text
EffectivePolicyRule {
    policyRuleRef
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    revisionRef
    currentAuthorizationProvenance
}
```

Only Rules with non-null current effective revision participate.

Pending/rejected changes remain queryable/explainable inside policy/governance views but do not appear as current effective policy.

## Evidence recognition handoff

`RecognizedAccessCandidate` is a derived value, not AP authoritative state until formally submitted:

```text
RecognizedAccessCandidate {
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    revisionRef
    evidenceProvenance[]
}
```

Access Policy validates it exactly as a manual proposal input. Evidence origin affects provenance, not authorization standards.

## MVP invariants

1. One stable PolicyRule identity exists per non-Retired directed ComponentDeployment pair.
2. Rule endpoints are immutable for Rule identity.
3. RevisionRef is proposed/effective state, not Rule identity.
4. Exact revision resolves Interaction/endpoints; duplicate InteractionRef is unnecessary in the Rule.
5. At most one Pending RuleChange exists per Rule in the first MVP.
6. Pending/rejected changes never overwrite current effective revision.
7. RuleChange identity distinguishes separate governance attempts, including repeated attempts for the same revision.
8. Both current side obligations must approve before activation.
9. MVP obligation resolution requires exactly one distinct Responsibility Scope per side.
10. Historical approvals cannot silently reactivate withdrawn current authorization.
11. Evidence-derived and manual changes follow the same authorization rules.
12. Evidence is provenance/input, not authorization.
13. Resource AddressSpace change does not redefine Rule identity.
14. Different ComponentDeployment on either side means a different concrete Rule subject.
15. Retired Rules remain historical and accept no new changes.
16. Technical materialization failure is distinct from semantic Rule effectiveness.

## Deliberately deferred

- several simultaneous Pending changes and conflict/ordering semantics;
- generalized overlapping Responsibility Scope approval algebra;
- partial consent reuse after obligation changes;
- time-bounded current authorization beyond explicit change/withdrawal facts;
- delegation/escalation/quorum workflows;
- durable pre-submission manual drafts;
- exact persistence/event-store representation;
- REST/API payloads, queues, retries, locks/version fields.

## Tactical coherence result

The target Access Policy lifecycle now has one authoritative owner and one aggregate root per concrete connection:

- PolicyRule exists before first approval and survives rejection/withdrawal for history;
- RuleChange is a child entity for distinct approval attempts, not a parallel proposal aggregate;
- current effective revision and pending history coexist safely;
- PolicyRuleId is AP-owned identity and downstream uses opaque PolicyRuleRef;
- revision changes preserve Rule identity;
- bilateral governance is internal to the same lifecycle rather than duplicated through AG -> AP authorization handoff.
