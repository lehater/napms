# Blind domain use-case contracts

Status: ACCEPTED candidate

## Resource Description

- Register Resource with stable ResourceRef and human-recognizable name.
- Register reusable Site records and reusable organizational ResponsibilityGroup records.
- Register logical ResourceEndpoint independently of address assignment.
- Set/change/remove current endpoint address realization while preserving prior values/time/provenance.
- Associate Site and Owner/Administrator ResponsibilityGroups with Resource.
- Read current Resource realization and basic history.
- Missing current address is a first-class unresolved state, not an empty/denied address.

## Application Communication

- Register Application and Components.
- Define a directed Interaction between one source Component and one destination Component.
- Define the complete minimal traffic semantics for one independently meaningful Interaction reason.
- Publish a new immutable InteractionRevision when decision-relevant traffic meaning changes; prior revisions remain resolvable for historical access intent.
- Read current Interaction and exact historical revision by reference.

## Application Deployment

- Register a concrete ComponentDeployment referencing one Component and one Resource.
- Read deployment identity, ComponentRef and ResourceRef without depending on Resource IP/address.
- Multiple deployments of one Component are distinct.
- MVP does not define in-place relocation or retirement of a Deployment; materially different placement is represented by a distinct Deployment unless future product input establishes another lifecycle.

## Business Connectivity

- Register/describe Business Process.
- Declare ConnectivityNeed from Process to one application Interaction.
- Associate optional business importance/criticality information without inventing propagation rules.
- Retire/end a Need while preserving historical justification.
- Read current and historical Need provenance.
- Need does not grant connectivity permission.

## Access Policy

- Submit a deliberate AccessRequest for one source ComponentDeployment, one destination ComponentDeployment and one exact InteractionRevision, backed by one current ConnectivityNeed for that Interaction.
- Reject a request when deployment/component directions do not match the referenced Interaction or when the required Need is not current at the submission transaction snapshot.
- Consume one final permission decision for the exact request: ALLOWED or DENIED.
- DENIED produces no PolicyRule.
- ALLOWED establishes/resolves one PolicyRule carrying the exact semantic subject and provenance.
- Change current PolicyRule effect between ACTIVE and INACTIVE without changing semantic subject or rewriting the decision provenance.
- Read current effective rules and historical request/decision/rule state.

## Policy Materialization composition

This is application behavior, not a domain-owner capability:

1. establish one server-owned current evaluation instant and one coherent database read snapshot;
2. select current ACTIVE PolicyRules from that snapshot;
3. resolve each exact InteractionRevision;
4. resolve source/destination Deployments to Resources;
5. resolve every current addressed endpoint of those Resources;
6. expand traffic semantics across required endpoint/traffic combinations without changing meaning;
7. preserve Rule/Need/decision/interaction/deployment/resource provenance;
8. if any required input is missing/ambiguous, return UNRESOLVED for the materialization rather than complete success.

Historical/time-travel policy export is not part of the selected MVP.
