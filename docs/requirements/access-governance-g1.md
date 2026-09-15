# Access Governance behavior — G1 Requirements Passport

Status: `G1 revalidated for concrete Component deployments and proposal/change behavior 2026-09-16`.

This file owns observable governance behavior. It does not define a Bounded Context boundary; current domain ownership is defined in `docs/domain/strategic-model.md` and `docs/domain/access-policy/tactical-model.md`.

## Observable requirements

1. The system shall support proposing access between one concrete source Component Deployment and one concrete destination Component Deployment using one exact immutable Interaction Contract Revision.
2. The selected source and destination Component Deployments shall realize the source and destination Components of that revision's owning Interaction; mismatched endpoints are not selectable.
3. Because an Interaction is defined only inside one Application, a proposed governed connection cannot join Components from different Applications.
4. A proposal/change shall preserve the exact revision being requested, its provenance and any business justification available at submission/decision time; later changes shall not rewrite historical decisions.
5. A deliberate human-submitted access change shall have a Process-backed Connectivity Need at submission time.
6. Recognition of observed/brownfield traffic may produce an access candidate before Process/Need attribution is known; the system shall not fabricate a Process or Need merely to recognize the candidate.
7. Evidence-derived recognition is not authorization. An evidence-derived candidate follows the same governance requirements as manually proposed access before it can affect effective policy.
8. Change initiation authority is distinct from approval authority.
9. Ordinary authorization requires independent source-side and destination-side approval obligations; overall acceptance requires both.
10. Either required side may reject a pending change.
11. Either authorized side may later withdraw its current consent without approval from the other side.
12. Rejection and withdrawal are distinct; neither rewrites historical valid decisions.
13. Old approved attempts cannot silently restore withdrawn consent.
14. Approval/withdraw authority is evaluated through Authority Management and is not inferred from Resource owner/administrator/responsibility metadata.
15. Rejected changes create no semantic deny Policy Rule.
16. A change proposing another Interaction Contract Revision for an already effective concrete source/destination Component Deployment pair shall not replace the current revision while that change is pending or rejected.
17. Only an accepted applicable change may move effective policy for that pair to the approved revision.
18. A second Component Deployment of the same Component is a different concrete access endpoint and may require a different change/approval basis/Policy Rule from another deployment instance.
19. Current Resource address changes do not by themselves change which Component Deployment is governed; they change downstream technical realization.
20. A Resource replacement represented by a different Component Deployment is a different concrete access endpoint for governance.
21. Current effective policy shall change only from explicit accepted/withdrawn governance outcomes; pending or rejected history shall never be interpreted as current effective access.
22. Current approval obligations shall be derived from the responsibility/scope facts applicable to the concrete source and destination Component Deployment Resources.
23. If either side resolves to zero or more than one distinct applicable Responsibility Scope in the MVP, approval obligations are unresolved and the change cannot become authorized; the product fails closed rather than choosing a scope by precedence.
24. Historical proposals/change attempts, approvals, rejections, withdrawals and evidence/business provenance remain explainable after current policy changes.

## Proposed versus effective access

The product shall preserve these two truths independently:

```text
currently effective access
!=
proposed access change
```

For an already effective concrete connection, a new revision may be proposed while the current revision remains effective. Rejecting the proposal leaves current effective policy unchanged. Approving it may change the effective revision without losing history of the earlier decision.

## Evidence-derived candidate boundary

`TrafficDerived` or other applicable technical evidence may be interpreted by recognition/correlation. When source/destination addresses can be correlated unambiguously to concrete Component Deployments and exact ACC traffic semantics, the product may surface an access candidate.

```text
Technical Access Evidence
    -> recognition/correlation
    -> source Component Deployment
    -> destination Component Deployment
    -> exact Interaction Contract Revision
    -> access candidate
    -> normal governance
```

Recording evidence alone never grants access, creates effective policy or bypasses Process/Need requirements for deliberate submission.

## Concrete governed access meaning

The concrete connection is the directed Component Deployment pair. The exact Interaction Contract Revision is the proposed/current traffic semantics for that connection; changing revision is a proposed change to the same concrete connection rather than automatically a different endpoint pair.

## G1 checkpoint result

The affected product behavior is accepted:

- governance operates on concrete Component Deployment endpoints;
- the exact immutable revision defines proposed/effective traffic semantics without requiring a duplicate Interaction reference;
- pending/rejected revision changes do not replace current effective access;
- evidence-derived candidates may enter the same governance path without evidence becoming authorization;
- deliberate submission requires Process-backed business justification;
- governance fails closed when approval obligations cannot be resolved;
- historical governance/provenance remains explainable.

Subsequent S2 convergence placed this lifecycle inside the Access Policy Bounded Context and modelled each formal attempt as a `RuleChange` child of `PolicyRule`. Those are domain decisions, not additional G1 behavior. No implementation authorization is implied.
