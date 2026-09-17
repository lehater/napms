# Business Connectivity — G1 Requirements Passport

Status: `G1 revalidation candidate accepted at observable-behavior level; BC boundary not decided`.

Date/source: stakeholder revalidation, 2026-09-14.

## Problem / outcome

Network access must be explainable by business purpose rather than only by IP addresses, ports or firewall rules. Deliberate access requests require structured business justification; observed brownfield traffic may be attributed later.

## Observable requirements

1. The system shall allow a Business Process to be identified and described as the business context that requires application connectivity.
2. The system shall associate organizational responsibility with a Business Process without assuming that the organizational unit is identical to a NAPMS Responsibility Scope.
3. The system shall support business importance/criticality information sufficient for downstream impact analysis; exact scoring and propagation rules remain unspecified.
4. The system shall represent a Connectivity Need independently from a concrete Access Request.
5. A Connectivity Need shall state that a Business Process requires an application-level Interaction from the perspective of a dependent participant/component role.
6. A Need shall not be identified by IP address, ResourceEndpoint or concrete Deployment.
7. One Process may have many Needs; the same Interaction may support Needs from many Processes.
8. A Need may survive IP changes, Resource address changes and concrete Deployment replacement while the business requirement remains the same.
9. One Need may lead to multiple concrete Access Requests over time or for different deployments.
10. A deliberate Access Request shall have a Process-backed Need at submission time.
11. Recognition of observed traffic shall be allowed before Process/Need attribution is known. The system shall not require a fabricated Process merely to recognize brownfield traffic.
12. Source and destination participants may contribute attribution independently; one user need not classify both sides.
13. A currently authorized access may later acquire additional Process/Need justification without requiring a duplicate Policy Rule solely for that justification.
14. Loss of a known Need shall not rewrite historical Requests or approvals.
15. Loss of all current known Needs for an authorization shall be distinguishable as a business-justification reconciliation condition. Automatic revocation is not required by this passport.

## Important negative requirements

- Business Process modelling does not imply a BPMN/workflow engine.
- Process hierarchy, subprocess/activity modelling and monetary valuation are not currently required.
- Process/Need is not proof of authorization.
- Observed traffic is not proof of Need.
- A destination-side Process is not mandatory merely because a source Process requests use of a shared service.
- Process criticality does not automatically propagate through an unspecified max/inheritance algorithm.

## Capability clues, not BC decisions

- Business Process Management
- Connectivity Need Management
- Business Attribution
- Business Impact / Justification Reconciliation

## G1 status

The product behavior above is coherent enough to proceed to later grouping/S2 work. Exact identities, aggregates, persistence, lifecycle state machines and context ownership remain intentionally open.
