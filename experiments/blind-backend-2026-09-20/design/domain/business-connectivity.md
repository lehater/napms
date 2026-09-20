# Tactical domain — Business Connectivity

Status: ACCEPTED candidate after Coding-Agent Challenge 01

## Aggregate: BusinessProcess

Identity: `ProcessRef`.

State:
- immutable non-empty `name`;
- immutable optional `description`;
- mutable `responsibleOrganization?: ResponsibleOrganization`;
- ConnectivityNeed children.

`ResponsibleOrganization` is a descriptive business-attribution value containing:
- required non-empty displayName;
- optional opaque externalReference.

It is not an authentication principal, authorization scope, or separately owned organizational master-data model.

Operations:
- RegisterProcess
- SetResponsibleOrganization / ClearResponsibleOrganization
- DeclareNeed
- RetireNeed
- ReadProcess
- ReadNeedCurrent/History

Process name/description are immutable in the selected MVP.

## Entity: ConnectivityNeed

Identity: `NeedRef`, stable inside its BusinessProcess lifecycle.

State:
- InteractionRef;
- immutable non-empty businessBasis;
- status ACTIVE | RETIRED;
- createdAt/retiredAt;
- provenance.

Invariants:
- Need references reusable Interaction meaning, not address/ResourceEndpoint/Deployment.
- Need does not grant access permission.
- one Process may own many Needs; one Interaction may be required by many Processes.
- retiring a Need preserves history and does not rewrite historical requests/decisions.
- a RETIRED Need cannot become ACTIVE again in the selected MVP.
- business importance/criticality is deliberately absent until Product Requirements defines its representation and use.

No Need description/basis edit is part of the selected MVP after creation.

## Consistency boundary

Process organization change, Need creation and Need retirement are atomic within one BusinessProcess aggregate version. The version guards all child mutation to prevent lost updates.
