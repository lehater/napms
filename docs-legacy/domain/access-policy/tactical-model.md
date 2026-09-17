# Access Policy — target Tactical DDD model

Status: `S2 MVP Tactical model revalidated for formal decisions 2026-09-16`.

## Purpose

Own one durable Policy Rule lifecycle for a concrete directed Component Deployment pair, including proposed traffic-revision changes, one formal decision per change, current effective revision and withdrawal history.

The MVP deliberately does **not** model a customer-specific approval procedure. Source/destination approvers, Responsibility Scope-derived approval obligations, quorum and workflow ordering are outside the baseline domain.

Access Policy does not own Application/Component/Interaction meaning, Component Deployment truth, Resource realization, business Need truth or actor-authority policy. It consumes only the public semantic references/contracts needed to validate a submitted change. Authority checks, where configured for an application action, do not become approval-workflow entities inside this model.

## Aggregate root — PolicyRule

```text
PolicyRule {
    policyRuleId
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    lifecycle: Active | Retired
    effectiveRevisionRef?
    changes: RuleChange[]
    withdrawalHistory[]
}
```

`PolicyRule` exists before it necessarily contributes effective access. A newly submitted initial change may create an Active Rule with no `effectiveRevisionRef` while its first change is Pending or after that attempt is Rejected.

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

A `RuleChange` is one formally submitted attempt to establish or change the traffic revision of a Policy Rule.

```text
RuleChange {
    ruleChangeId
    revisionRef
    origin: Manual | EvidenceDerived
    processConnectivityNeedRef
    businessJustification
    evidenceProvenance[]
    state: Pending | Accepted | Rejected
    submittedAt
    submittedBy
    decidedAt?
    decidedBy?
    decisionProvenanceRef?
}
```

`RuleChange` has identity because two attempts may request the same revision at different times, with different business/evidence provenance, and must remain distinguishable historically.

It is a child entity of `PolicyRule`, not a second Aggregate Root and not a separate Proposal lifecycle owner.

A retry of one already-established submission must not create a second semantic change attempt merely because transport was retried; exact idempotency realization is Architecture/Implementation work.

### Submission boundary

A durable `RuleChange` represents a formally submitted policy-change attempt.

A `RecognizedAccessCandidate` from evidence correlation is a non-authoritative input value and need not have durable entity identity. It may pre-populate/propose:

```text
sourceComponentDeploymentRef
destinationComponentDeploymentRef
revisionRef
evidenceProvenance
```

but deliberate submission still requires the accepted Process-backed Connectivity Need/business basis.

Manual drafts before formal submission likewise need not be domain entities unless later product behavior requires durable drafts.

## Formal decision

The complete MVP decision model is:

```text
Pending -> Accepted
Pending -> Rejected
```

A decision records enough actor/time/provenance information to explain the formal outcome. It does not model how the organization reached that outcome.

There is no baseline domain concept for:

- source-side versus destination-side decisions;
- `ApprovalBasis` or approval-obligation snapshots;
- approval quorum/order;
- Responsibility Scope-derived approvers;
- CAB/ticket/workflow stages;
- external approval-system internals.

Those procedures may be implemented externally and hand AP the final formal outcome through an authorized application/integration action.

## Change activation

A Pending RuleChange may become `Accepted` and update `effectiveRevisionRef` only when:

1. endpoint/revision compatibility still holds;
2. the Rule is Active;
3. the change is still applicable to the Rule's current state;
4. the formal decision is Accepted.

When accepted:

```text
PolicyRule.effectiveRevisionRef = RuleChange.revisionRef
RuleChange.state = Accepted
```

The same `PolicyRuleId` is retained.

Pending or Rejected changes never modify `effectiveRevisionRef`.

### First authorization

For a new Rule:

```text
PolicyRule.effectiveRevisionRef = null
RuleChange(R1) = Pending
```

After acceptance:

```text
PolicyRule.effectiveRevisionRef = R1
RuleChange(R1) = Accepted
```

If rejected, the Rule remains durable and non-effective with the rejected historical attempt preserved.

### Revision change

For an effective Rule on `R1`:

```text
PolicyRule.effectiveRevisionRef = R1
RuleChange(R2) = Pending
```

While Pending or after Rejection, `R1` remains effective.

Only acceptance of the applicable R2 change moves the same Rule to `R2`.

## Concurrent/pending change boundary

The first MVP allows at most one `Pending` RuleChange per Active PolicyRule.

This prevents two pending revisions from requiring an unaccepted conflict-resolution/ordering rule. A new change may be submitted after the existing Pending change reaches a terminal outcome.

This is an MVP domain boundary, not a database-locking prescription.

## Current effectiveness / withdrawal

`effectiveRevisionRef != null` means the Rule currently contributes semantic access.

Withdrawal clears current effectiveness without deleting the Rule or rewriting change history:

```text
WithdrawPolicyRule
    -> effectiveRevisionRef = null
    -> append WithdrawalRecord
```

```text
WithdrawalRecord {
    withdrawnAt
    withdrawnBy
    provenanceRef?
}
```

The domain records the formal withdrawal fact; it does not model a customer-specific withdrawal approval procedure.

Old Accepted RuleChanges cannot silently restore `effectiveRevisionRef` after withdrawal. Re-establishing access requires a new RuleChange and a new explicit Accepted decision, even when it proposes the same immutable revision as a previously accepted change.

## Decision history

The Rule preserves immutable explainability sufficient to show:

- which RuleChange established each effective revision;
- the formal Accepted/Rejected outcome and its actor/time/provenance;
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
AcceptRuleChange
RejectRuleChange
WithdrawPolicyRule
RetirePolicyRule
```

Names express domain meaning, not frozen API command names.

`SubmitInitialRuleChange` creates/reuses the one Rule for the directed pair and records its first submitted change.

`SubmitRuleChange` requires no other Pending change for that Rule.

`AcceptRuleChange` records the formal decision and atomically advances current effective revision when the change remains applicable.

`RejectRuleChange` records the terminal formal rejection without changing current effective revision.

`WithdrawPolicyRule` clears current effectiveness and records the withdrawal fact without deleting history.

## Published current-policy contract

Downstream consumers do not need change-decision internals. Access Policy publishes current effective Rule meaning equivalent to:

```text
EffectivePolicyRule {
    policyRuleRef
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    revisionRef
    currentDecisionProvenance
}
```

Only Rules with non-null current effective revision participate.

Pending/Rejected changes remain queryable/explainable inside policy views but do not appear as current effective policy.

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

Access Policy validates it exactly as a manual proposal input. Evidence origin affects provenance, not decision semantics.

## MVP invariants

1. One stable PolicyRule identity exists per non-Retired directed ComponentDeployment pair.
2. Rule endpoints are immutable for Rule identity.
3. RevisionRef is proposed/effective state, not Rule identity.
4. Exact revision resolves Interaction/endpoints; duplicate InteractionRef is unnecessary in the Rule.
5. At most one Pending RuleChange exists per Rule in the first MVP.
6. Pending/Rejected changes never overwrite current effective revision.
7. RuleChange identity distinguishes separate formal attempts, including repeated attempts for the same revision.
8. One formal Accepted decision is sufficient to activate an applicable change; AP does not require bilateral approval entities.
9. Customer-specific approval procedures are outside the MVP domain baseline.
10. Historical Accepted changes cannot silently reactivate withdrawn current authorization.
11. Evidence-derived and manual changes follow the same formal decision lifecycle.
12. Evidence is provenance/input, not authorization.
13. Resource AddressSpace change does not redefine Rule identity.
14. Different ComponentDeployment on either side means a different concrete Rule subject.
15. Retired Rules remain historical and accept no new changes.
16. Technical materialization failure is distinct from semantic Rule effectiveness.

## Deliberately deferred

- customer-specific approval workflow modelling, including bilateral/quorum/order/stages;
- several simultaneous Pending changes and conflict/ordering semantics;
- time-bounded current authorization beyond explicit change/withdrawal facts;
- durable pre-submission manual drafts;
- exact persistence/event-store representation;
- REST/API payloads, queues, retries, locks/version fields.

## Tactical coherence result

The target Access Policy lifecycle has one authoritative owner and one aggregate root per concrete connection:

- PolicyRule exists before first acceptance and survives rejection/withdrawal for history;
- RuleChange is a child entity for distinct formal attempts, not a parallel Proposal aggregate;
- current effective revision and pending history coexist safely;
- PolicyRuleId is AP-owned identity and downstream uses opaque PolicyRuleRef;
- revision changes preserve Rule identity;
- one formal Accepted/Rejected outcome is sufficient for MVP;
- organizational approval procedure remains outside AP instead of being prematurely encoded into the domain.
