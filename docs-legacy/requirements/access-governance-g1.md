# Access Governance behavior — G1 Requirements Passport

Status: `G1 revalidated for formal policy-decision semantics 2026-09-16`.

This file owns observable governance behavior. It does not define a Bounded Context boundary; current domain ownership is defined in `docs/domain/strategic-model.md` and `docs/domain/access-policy/tactical-model.md`.

## Observable requirements

1. The system shall support proposing access between one concrete source Component Deployment and one concrete destination Component Deployment using one exact immutable Interaction Contract Revision.
2. The selected source and destination Component Deployments shall realize the source and destination Components of that revision's owning Interaction; mismatched endpoints are not selectable.
3. Because an Interaction is defined only inside one Application, a proposed governed connection cannot join Components from different Applications.
4. A proposal/change shall preserve the exact revision being requested, its provenance and any business justification available at submission/decision time; later changes shall not rewrite historical decisions.
5. A deliberate human-submitted access change shall have a Process-backed Connectivity Need at submission time.
6. Recognition of observed/brownfield traffic may produce an access candidate before Process/Need attribution is known; the system shall not fabricate a Process or Need merely to recognize the candidate.
7. Evidence-derived recognition is not authorization. An evidence-derived candidate follows the same formal decision path as manually proposed access before it can affect effective policy.
8. One submitted policy change has one formal decision state: `Pending`, `Accepted` or `Rejected`.
9. A `Pending` change does not alter current effective policy.
10. A `Rejected` change does not alter current effective policy and creates no semantic deny Policy Rule.
11. Only an `Accepted` applicable change may establish or change the effective Interaction Contract Revision for the concrete endpoint pair.
12. The MVP shall not require a built-in source-side/destination-side approval workflow, approval quorum, approval ordering, Responsibility Scope resolution or other customer-specific approval procedure merely to decide a change.
13. The procedure by which an organization reaches the formal `Accepted` or `Rejected` outcome may be external, manual, integrated or customer-specific and is outside the MVP domain baseline.
14. Authority to propose, decide or withdraw a policy change may be evaluated through Authority Management as protected actions, but such action authority is distinct from modelling the organization's approval procedure.
15. A currently effective Rule may be explicitly withdrawn by an actor admitted to the applicable withdrawal action; withdrawal removes current effectiveness without rewriting proposal/decision history.
16. Old accepted changes cannot silently restore a withdrawn Rule; re-establishing access requires a new explicit accepted change.
17. A change proposing another Interaction Contract Revision for an already effective concrete source/destination Component Deployment pair shall not replace the current revision while that change is Pending or Rejected.
18. A second Component Deployment of the same Component is a different concrete access endpoint and may require a different Rule and decision from another deployment instance.
19. Current Resource address changes do not by themselves change which Component Deployment is governed; they change downstream technical realization.
20. A Resource replacement represented by a different Component Deployment is a different concrete access endpoint for governance.
21. Historical proposals/change attempts, formal decisions, withdrawals and evidence/business provenance remain explainable after current policy changes.

## Proposed versus effective access

The product shall preserve these two truths independently:

```text
currently effective access
!=
proposed access change
```

For an already effective concrete connection, a new revision may be proposed while the current revision remains effective. Rejecting the proposal leaves current effective policy unchanged. Accepting it may change the effective revision without losing history of the earlier decision.

## Formal decision boundary

The MVP deliberately models only the outcome required by Access Policy:

```text
RuleChange
    Pending
      -> Accepted
      -> Rejected
```

The system may protect the transition with actor/action authority and preserve decision provenance, but it does not prescribe how many approvers exist, which organizational sides participate, which external ticket/workflow produced the outcome, or how a customer structures approval policy.

An external workflow may therefore produce a final decision and invoke the same Access Policy decision capability as an in-product manual decision, provided the caller has the required action authority.

## Evidence-derived candidate boundary

`TrafficDerived` or other applicable technical evidence may be interpreted by recognition/correlation. When source/destination addresses can be correlated unambiguously to concrete Component Deployments and exact ACC traffic semantics, the product may surface an access candidate.

```text
Technical Access Evidence
    -> recognition/correlation
    -> source Component Deployment
    -> destination Component Deployment
    -> exact Interaction Contract Revision
    -> access candidate
    -> normal RuleChange decision
```

Recording evidence alone never grants access, creates effective policy or bypasses Process/Need requirements for deliberate submission.

## Concrete governed access meaning

The concrete connection is the directed Component Deployment pair. The exact Interaction Contract Revision is the proposed/current traffic semantics for that connection; changing revision is a proposed change to the same concrete connection rather than automatically a different endpoint pair.

## G1 checkpoint result

`G1 PASS` for the revalidated formal-decision behavior:

- governance operates on concrete Component Deployment endpoints;
- the exact immutable revision defines proposed/effective traffic semantics without requiring a duplicate Interaction reference;
- one formal `Pending | Accepted | Rejected` change decision is sufficient for the MVP;
- customer-specific bilateral/quorum/workflow approval procedures are not part of the baseline domain model;
- action authority and decision provenance remain supported without modelling the external procedure;
- pending/rejected revision changes do not replace current effective access;
- evidence-derived candidates may enter the same decision path without evidence becoming authorization;
- deliberate submission requires Process-backed business justification;
- historical decision/provenance remains explainable.

No implementation authorization is implied.
