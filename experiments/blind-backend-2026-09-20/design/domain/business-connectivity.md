# Tactical domain — Business Connectivity

Status: ACCEPTED candidate

## Aggregate: BusinessProcess

Identity: `ProcessRef`.

State:
- name/description;
- responsibleOrganizationRef?;
- importance/criticality fields only when explicitly supplied;
- ConnectivityNeed children or references.

## Entity/Aggregate child: ConnectivityNeed

Identity: `NeedRef`.

State:
- InteractionRef;
- description/business basis;
- status ACTIVE | RETIRED;
- createdAt/retiredAt;
- provenance.

Invariants:
- Need references reusable Interaction meaning, not address/ResourceEndpoint/Deployment.
- Need does not grant access permission.
- one Process may own many Needs; one Interaction may be required by many Processes.
- retiring a Need preserves history and does not rewrite historical requests/decisions.
- criticality has no implicit propagation algorithm.

Operations:
- RegisterProcess
- DeclareNeed
- UpdateNeedDescription
- RetireNeed
- ReadNeedCurrent/History

## Consistency boundary

Process/Need mutation is atomic within one BusinessProcess aggregate version.
