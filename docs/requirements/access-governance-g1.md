# Access Governance — G1 Requirements Passport

Status: `G1 revalidated for concrete Component deployments and proposal/change behavior 2026-09-16`.

## Observable requirements

1. The system shall support proposing access between one concrete source Component Deployment and one concrete destination Component Deployment using one exact immutable Interaction Contract Revision.
2. The selected source and destination Component Deployments shall realize the source and destination Components of that revision's owning Interaction; mismatched endpoints are not selectable.
3. Because an Interaction is defined only inside one Application, a proposed governed connection cannot join Components from different Applications.
4. A proposal/change shall preserve the exact revision being requested, its provenance and any business justification available at submission/decision time; later changes shall not rewrite historical decisions.
5. A deliberate human-submitted access request shall have a Process-backed Connectivity Need at submission time.
6. Recognition of observed/brownfield traffic may produce an access proposal/candidate before Process/Need attribution is known; the system shall not fabricate a Process or Need merely to recognize the candidate.
7. Evidence-derived recognition is not authorization. An evidence-derived proposal follows the same governance requirements as a manually created proposal before it can affect effective policy.
8. Request initiation authority is distinct from approval authority.
9. Ordinary authorization requires independent source-side and destination-side approval obligations; overall grant requires both.
10. Either required side may reject a pending proposal/request.
11. Either authorized side may later withdraw its current consent without approval from the other side.
12. Rejection and withdrawal are distinct; neither rewrites historical valid decisions.
13. Old approved requests or proposals cannot silently restore withdrawn consent.
14. Approval/revoke authority is evaluated through Authority Management and is not inferred from Resource Owner/Administrator/Responsibility metadata.
15. Rejected proposals/requests create no semantic deny Policy Rule.
16. A proposal changing only the Interaction Contract Revision for an already effective concrete source/destination Component Deployment pair shall not replace the currently effective revision while that proposal is pending or rejected.
17. Only an accepted authorization change may move the effective policy for that pair to the newly approved revision.
18. A second Component Deployment of the same Component is a different concrete access endpoint and may require a different proposal, approval basis and Policy Rule from another deployment instance.
19. Current Resource address changes do not by themselves change which Component Deployment is governed; they change downstream technical realization.
20. A Resource replacement that results in a different Component Deployment is a different concrete access endpoint for governance.
21. Access Policy consumes the accepted authorization outcome/current-policy change; it does not independently reconstruct bilateral approval decisions.
22. Current approval obligations shall be derived from the responsibility/scope facts applicable to the concrete source and destination Component Deployment Resources.
23. If either side resolves to zero or more than one distinct applicable Responsibility Scope in the MVP, approval obligations are unresolved and the proposal cannot become authorized; governance fails closed rather than choosing a scope by precedence.
24. Historical proposals/requests, approvals, rejections, withdrawals and evidence/business provenance remain explainable after current policy changes.

## Proposed/effective distinction

The product shall preserve these two truths independently:

```text
currently effective access
!=
proposed access change
```

For an already effective concrete connection, a new revision may be proposed while the current revision remains effective. Rejecting the proposal leaves current effective policy unchanged. Approving it may change the effective revision without losing the history of the earlier decision.

This requirement does not decide whether proposal/change history and current Policy Rule state are represented as one aggregate, two aggregates or two Bounded Contexts. That ownership/lifecycle question belongs to S2.

## Evidence-derived proposal boundary

`TrafficDerived` or imported/configured evidence may be interpreted by a recognition/reconciliation composition. When that interpretation can correlate source/destination addresses to concrete Component Deployments and match exact ACC traffic semantics, the product may surface a proposal/candidate for governance.

Conceptually:

```text
Technical Access Evidence
    -> recognition/correlation
    -> source Component Deployment
    -> destination Component Deployment
    -> exact Interaction Contract Revision
    -> access proposal/candidate
    -> normal governance
```

Recording evidence alone never grants access, creates effective policy or bypasses Process/Need requirements for deliberate submission.

## Current governed access meaning

The concrete governed connection is identified from the directed Component Deployment pair. The exact Interaction Contract Revision is the requested/current traffic semantics for that connection; a traffic revision change is a proposed change to the same concrete connection rather than automatically a different endpoint pair.

The final Tactical identity/sameness representation is intentionally left to S2.

## G1 checkpoint result

The affected product behavior is accepted for S2 re-entry:

- governance operates on concrete Component Deployment endpoints;
- the exact immutable revision defines proposed/effective traffic semantics without requiring a duplicate Interaction reference;
- pending/rejected revision changes do not replace current effective access;
- evidence-derived candidates may enter the same governance path without evidence becoming authorization;
- deliberate submission still requires Process-backed business justification;
- governance fails closed when current approval obligations cannot be resolved;
- historical governance/provenance remains explainable.

No implementation authorization is implied. Aggregate boundaries, proposal/change-request identity, Policy Rule identity, and the final AG/AP strategic split remain S2 work.
