# Application Catalogue Domain Target Requirements

Status: `accepted target; implementation pending`.

Date: 2026-09-12.

Decision: `../decisions/ADR-015-acc-component-deployment-and-atomic-interaction-contract.md`.
Domain model: `../domain/application-communication-catalogue/target-model.md`.

## Scope

These requirements define only the Application Communication Catalogue target semantics and its published identity boundary. Access Policy and Resource Catalogue internals are intentionally out of scope and will be reviewed separately.

## Requirements

ACC shall:

1. model an Application as a reusable definition containing Components;
2. model `ComponentDeployment` as the concrete deployment unit; an Application as a whole is not the deployment unit;
3. keep the parent Component of a Component Deployment immutable for the deployment lifetime;
4. relate a Component Deployment to zero or more Resource Catalogue Resources through separate temporal `DeploymentResourceBinding` facts;
5. treat Resource references as opaque external identifiers and keep Resource/Endpoint/address realization outside Component Deployment identity;
6. define each directed `InteractionDefinition` between a source Component and destination Component;
7. preserve decision-relevant interaction traffic as immutable `InteractionContractRevision` snapshots;
8. require each contract revision to contain one or more vendor-neutral traffic alternatives;
9. treat the complete set of traffic alternatives in one contract revision as one atomic communication contract;
10. forbid partial selection/authorization of traffic inside one contract revision;
11. require independently governed traffic subsets to be represented by separate Interaction Definitions;
12. publish a concrete deployed interaction as exactly:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
+ interactionContractRevisionRef
```

13. validate that source/destination deployments belong to the Components declared by the referenced Interaction Definition before publishing that subject;
14. preserve old immutable interaction contract revisions and references when traffic semantics change;
15. expose cross-context references as stable opaque IDs rather than require relational foreign keys across bounded-context persistence schemas.

## Not decided here

This requirement does not decide:

- whether a Component Deployment also binds to a specific Resource Endpoint;
- how endpoint selection varies by network context or NAT;
- Access Policy internal persistence/aggregate structure;
- Resource Catalogue internal endpoint/address structure;
- exact migration mechanics from the implemented I31 Application Deployment model;
- final Application Catalogue UI changes.

## Acceptance invariants

A conforming future implementation must prove at least:

- moving/adding/removing a Resource binding leaves the Component Deployment identity unchanged;
- a Component Deployment can have multiple effective Resource bindings;
- changing interaction traffic produces a new immutable contract revision rather than rewriting a referenced revision;
- a consumer cannot authorize only one traffic alternative from an atomic revision;
- an invalid source/destination deployment pair cannot be published as a Directed Interaction identity;
- the published subject contains no Resource, Endpoint, IP address, protocol or port fields;
- no consumer persistence adapter requires a SQL foreign key into ACC-owned tables.
