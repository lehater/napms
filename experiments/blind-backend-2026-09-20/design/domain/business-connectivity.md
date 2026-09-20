# Tactical domain — Business Connectivity

Status: ACCEPTED candidate

## Aggregate: BusinessProcess

Identity: `ProcessRef`.

State:
- name/description;
- responsibleOrganization?: ResponsibleOrganization;
- ConnectivityNeed children or references.

`ResponsibleOrganization` is a descriptive business-attribution value containing an opaque optional external reference and display name. It is not an authentication principal, authorization scope, or separately owned organizational master-data model.

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
- business importance/criticality is deliberately absent from this MVP model until Product Requirements defines its representation and use.

Operations:
- RegisterProcess
- UpdateProcessDescription
- SetResponsibleOrganization
- DeclareNeed
- UpdateNeedDescription
- RetireNeed
- ReadNeedCurrent/History

## Consistency boundary

Process/Need mutation is atomic within one BusinessProcess aggregate version.
