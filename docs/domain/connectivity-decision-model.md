# Connectivity Decision Tactical Model

Status: `accepted I15 domain closure`.

Date: 2026-09-09.

## Purpose

Connectivity Decision owns the authoritative final answer to:

> may this exact proposed semantic connectivity be used as the permission fact for Access Policy materialization at this logical time?

It owns decision identity, final outcome, reason/provenance, validity and reconsideration history. It does not own the Access Rule, Connectivity Requirement, catalogue facts or actor authority.

## Aggregate

### ConnectivityDecision

One immutable final decision record:

```text
ConnectivityDecision
    decisionId
    subject = RuleSemanticIdentity
    governanceScope
    outcome = Allowed | NotAllowed
    validity = [validFrom, validUntil?)
    reason
    evidenceReferences[]
    provenance
    supersedesDecisionId?
```

### Decision identity

`DecisionId` is stable and distinct from the subject.

Multiple historical Decisions may exist for the same subject/scope. A new reconsideration creates a new Decision; it never edits an earlier outcome/reason/provenance.

### Decision subject

The subject is the exact Access Policy `RuleSemanticIdentity`:

```text
Source Component Deployment
+ Destination Component Deployment
+ immutable DCS revision
```

Identity-defining subject facts are immutable for one Decision.

### Decision Governance Scope

The first accepted model uses the proposal's accepted authority scope as the Decision Governance Scope.

The scope:
- is stable on the Decision;
- determines Authority Management checks for decision/read actions;
- is not caller-substitutable after the Decision is created;
- is metadata for governance and does not become part of RuleSemanticIdentity.

A distinct mapping between proposal scope and decision scope is not introduced without a concrete requirement.

## Outcome

Business outcome is exactly:

`Allowed | NotAllowed`

There is no `Pending`, `Approved`, `Rejected`, `Revoked` or `Unknown` Decision state in I15.

No effective Decision, inaccessible Decision, persistence uncertainty or conflicting current Decisions are application/integration uncertainty and fail closed. They are not new business outcomes.

## Validity

Decision validity is an offset-aware half-open interval:

`validFrom <= asOf < validUntil`

`validUntil` may be absent.

Rules:
- `validFrom` and `validUntil`, when present, are offset-aware;
- if `validUntil` exists, `validFrom < validUntil`;
- Access Policy may consume a Decision only when it is effective at the proposal logical time;
- expiration does not rewrite the Decision;
- expiration or later supersession does not silently mutate an already materialized Access Rule.

Validity therefore governs **decision consumption**, not hidden cross-context Rule lifecycle.

## Reason

Every final Decision has:
- a non-empty stable `reasonCode`;
- a non-empty human-readable `reasonText`.

The reason explains the decision outcome at business level without copying ownership of external policy/catalogue/requirement facts into this context.

## Evidence references

A Decision may preserve zero-or-more source-qualified opaque references used in reaching the result.

Examples of reference kinds may include:
- Connectivity Requirement;
- security/risk/compliance policy fact;
- catalogue fact;
- external decision-support fact.

The referenced fact remains owned by its source context.

A Connectivity Requirement may be evidence for necessity. It never becomes authorization by itself:

`Required != Allowed`

## Decision provenance

Minimum provenance:
- deciding actor/principal ID;
- decision time;
- Authority Management authority reference;
- proposal/subject correlation sufficient to identify what was decided.

Decision time is business provenance. It does not replace validity.

## Participation mechanism

The semantic action is the same whether the deciding principal is:
- a human actor;
- a trusted service principal.

Authority Management determines whether that principal may perform `DecideConnectivity` for the scope/time.

The Decision domain does not encode UI workflow or principal type into outcome meaning.

## Authority actions

Minimum I15 actions:
- `DecideConnectivity`;
- `ReadConnectivityDecision`.

`ProposeConnectivity` never implies either action.

The first model requires one unambiguous effective `DecideConnectivity` authority. Quorum and separation-of-duties are not introduced without a concrete accepted rule.

## Reconsideration and supersession

A reconsideration creates a new immutable Decision.

When replacing a current Decision:
- same subject;
- same Decision Governance Scope;
- explicit `supersedesDecisionId` pointing to the immediately superseded Decision;
- historical records remain unchanged.

For one subject/scope/asOf, the domain must yield at most one current effective Decision. Multiple non-superseded effective Decisions are an invariant/persistence conflict and must fail closed.

## Selection for consumption

Input:

```text
subject
governanceScope
asOf
```

Output:

```text
one effective ConnectivityDecision
| None
| Unknown/Ambiguous application failure
```

Selection never manufactures `Allowed` from absence.

## Relationship to Access Rule Proposal

The proposal supplies:
- exact subject;
- accepted proposal governance scope;
- proposal-time correlation/provenance.

Connectivity Decision answers the permission question for that exact subject/scope.

Proposal authority proves only that the proposal may be submitted. It is not decision authority and is not the reason for Allowed.

## Relationship to Connectivity Requirement

Connectivity Requirement states what connectivity is needed.

A Decision may reference one or more Requirements as evidence, but:
- Requirement identity/lifecycle stays in Connectivity Requirements;
- a Requirement does not require a matching Decision to exist;
- a Decision does not mutate a Requirement;
- a Requirement does not imply Allowed.

## Relationship to Access Policy

For a valid proposal at logical time T:

```text
effective Allowed Decision
    -> Access Policy may materialize/resolve the Rule

effective NotAllowed Decision
    -> no new Rule materialization from that proposal

no trustworthy effective Decision
    -> fail closed
```

Access Policy stores enough Decision correlation for historical explainability.

A later superseding/expired Decision does not automatically change an existing Rule's Active/Inactive state. Automatic revocation/change-management requires a separate accepted requirement and explicit cross-context behavior.

## Invariants

1. DecisionId is stable and unique.
2. Subject and governance scope are immutable.
3. Outcome is final `Allowed | NotAllowed`.
4. Reason is mandatory.
5. Decision provenance is mandatory.
6. Validity is temporally valid.
7. Supersession is same-subject/same-scope and historical records are immutable.
8. At most one effective non-superseded Decision exists for one subject/scope/asOf.
9. Requirement evidence never becomes authorization.
10. Access Policy never owns Decision reasons/workflow.
