# Tactical domain — Business Connectivity

Status: ACCEPTED after Coding-Agent Challenge 02

## Aggregate: BusinessProcess

Identity: `ProcessRef`.

State:
- immutable non-empty name;
- immutable optional description;
- mutable `responsibleOrganization?: ResponsibleOrganization`;
- ConnectivityNeed children;
- aggregate version.

`ResponsibleOrganization` contains required non-empty displayName and optional opaque externalReference. It is descriptive attribution only, not authentication/authorization scope.

Operations:
- RegisterProcess
- SetResponsibleOrganization / ClearResponsibleOrganization
- DeclareNeed
- RetireNeed
- ReadProcess
- ReadNeedCurrent/History

## Entity: ConnectivityNeed

Identity: `NeedRef`, stable inside BusinessProcess lifecycle.

Immutable state:
- `interactionRef`;
- `participantComponentRef`;
- non-empty `businessBasis`;
- createdAt/provenance.

Mutable lifecycle:
- status ACTIVE | RETIRED;
- retiredAt when RETIRED.

Invariants:
- InteractionRef resolves to reusable Interaction meaning.
- participantComponentRef must equal either that Interaction's sourceComponentRef or destinationComponentRef.
- participantComponentRef is reusable Component identity, never Deployment/Resource/address identity.
- source-side and destination-side Needs for the same Interaction are independent and may coexist.
- Need does not grant connectivity permission.
- one Process may own many Needs; one Interaction may support many Needs from many Processes and participant sides.
- Need survives concrete Deployment/address replacement while the referenced Interaction/Component business meaning remains.
- retiring Need preserves history and never rewrites AccessRequest/decision/Rule provenance.
- RETIRED is terminal in selected MVP.
- business criticality/importance remains outside selected MVP until Product Requirements defines its representation/use.

Need business basis/participant/Interaction are immutable after declaration.

## Consistency boundary

Responsible-organization change, Need creation and Need retirement are atomic under one BusinessProcess aggregate version. Need creation validates Interaction + participant Component through Application Communication read contract; it writes only Business Connectivity state.
