# Business Connectivity requirements

## Purpose

Make network access explainable by business purpose rather than only by technical addresses, ports or firewall rules.

Business Connectivity owns the product semantics of Business Process, Connectivity Need and business justification/attribution used by governance and reconciliation.

## Requirements

1. The system identifies and describes a Business Process as the business context that requires application connectivity.
2. A Business Process may carry organizational responsibility and business importance/criticality information without implying that an organizational unit is a NAPMS Responsibility Scope.
3. A Connectivity Need exists independently from a concrete Access Request.
4. A Connectivity Need states that a Business Process requires an application-level Interaction from the perspective of a dependent participant/component role.
5. A Connectivity Need is not identified by IP address, Resource identity, address, placement or concrete ApplicationDeployment.
6. One Business Process may own many Connectivity Needs; the same Interaction may support Needs from many Processes.
7. A Connectivity Need may survive Resource/address changes and ApplicationDeployment replacement while the same business requirement remains.
8. One Connectivity Need may support multiple concrete Access Requests across deployments or over time.
9. A deliberate Access Request has a Process-backed Connectivity Need at submission time.
10. Observed technical communication may exist before Process/Need attribution is known. The system does not fabricate a Business Process merely to record or recognize technical evidence.
11. Source and destination participants may contribute business attribution independently; one actor need not classify both sides.
12. Current authorized access may acquire additional Process/Need justification without creating a duplicate Policy Rule solely for that justification.
13. Loss of a known Connectivity Need does not rewrite historical Requests, approvals or already recorded provenance.
14. Loss of all current known Connectivity Needs for an authorization is observable as a business-justification reconciliation condition; this requirement does not itself authorize automatic revocation.

## Current boundary

Business Process modelling is not a BPMN/workflow engine. The current contract does not define process hierarchy, subprocess/activity execution, monetary valuation, automatic criticality propagation or proof of authorization from business attribution.

A Process/Need expresses business purpose. Observed traffic is evidence rather than proof of Need, and a Need is justification rather than authorization.
