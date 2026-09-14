# Application Catalogue Domain Target Requirements

Status: `G1 revalidated target behavior; S2/ADR update pending`.

Date: 2026-09-14.

Previous decision source: `../decisions/ADR-015-acc-component-deployment-and-atomic-interaction-contract.md`.
Domain model: `../domain/application-communication-catalogue/target-model.md`.

The 2026-09-14 stakeholder revalidation supersedes ADR-015 only where that ADR allows one ComponentDeployment to have zero or multiple effective Resource bindings. The ADR/domain model are downstream `DIRTY` artifacts and must be revalidated in S2 after G1 passes.

## Scope

These requirements define the Application Communication Catalogue target semantics needed by the current MVP authorization subject. Access Policy and Resource Catalogue internals remain outside ACC ownership.

## Requirements

ACC shall:

1. model an Application as a reusable definition containing Components;
2. model `ComponentDeployment` as the concrete deployment of one concrete Component on one concrete Resource;
3. require exactly one Resource reference when a ComponentDeployment is created;
4. keep the parent Component and bound Resource stable for that ComponentDeployment lifetime;
5. treat moving the Component to another Resource as a new concrete ComponentDeployment rather than silently rebinding the existing deployment;
6. treat the Resource reference as an opaque Resource Catalogue identifier; ResourceEndpoint/address realization remains Resource Catalogue truth and is not copied into ComponentDeployment identity fields;
7. allow Resource Endpoint additions/removals and address changes on the same Resource without changing the ComponentDeployment identity;
8. define each directed `InteractionDefinition` between a source Component and destination Component;
9. preserve decision-relevant interaction traffic as immutable `InteractionContractRevision` snapshots;
10. require each contract revision to contain one or more vendor-neutral traffic alternatives;
11. treat the complete set of traffic alternatives in one contract revision as one atomic communication contract;
12. forbid partial selection/authorization of traffic inside one contract revision;
13. require independently governed traffic subsets to be represented by separate Interaction Definitions;
14. publish a concrete deployed interaction as exactly:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
+ interactionContractRevisionRef
```

15. validate that source/destination deployments belong to the Components declared by the referenced Interaction Definition before publishing that subject;
16. preserve old immutable interaction contract revisions and references when traffic semantics change;
17. expose cross-context references as stable opaque IDs rather than require relational foreign keys across bounded-context persistence schemas.

## Deployment and Resource semantics

For MVP:

```text
ComponentDeployment -> exactly one Resource
```

The Resource association is mandatory because the authorization subject is a concrete deployed realization, not an abstract Component occurrence detached from infrastructure.

The Resource itself remains owned by Resource Catalogue. ACC stores only the stable external Resource reference needed to say where this concrete ComponentDeployment exists.

Technical realization below Resource level remains independent:

```text
ComponentDeployment
    -> Resource reference
        -> ResourceEndpoints
            -> current addresses/prefixes
```

Changing Endpoint/address realization therefore does not imply a new deployment or new authorization. Changing the Resource does.

## Not decided here

This requirement does not decide:

- whether a ComponentDeployment additionally binds to a specific Resource Endpoint;
- how endpoint selection varies by network context or NAT;
- Access Policy internal persistence/aggregate structure;
- Resource Catalogue internal endpoint/address structure;
- exact migration mechanics from the implemented I31 Application Deployment model or the previous ADR-015 zero/many Resource-binding model;
- final Application Catalogue UI changes;
- final aggregate/state-machine representation of ComponentDeployment replacement/retirement.

## Acceptance invariants

A conforming future implementation must prove at least:

- ComponentDeployment creation fails without exactly one valid Resource reference;
- one ComponentDeployment does not simultaneously represent deployments on multiple Resources;
- moving the Component to another Resource produces a different ComponentDeployment reference rather than mutating the existing authorization subject in place;
- Endpoint/address changes on the same Resource leave the ComponentDeployment reference unchanged;
- changing interaction traffic produces a new immutable contract revision rather than rewriting a referenced revision;
- a consumer cannot authorize only one traffic alternative from an atomic revision;
- an invalid source/destination deployment pair cannot be published as a Directed Interaction identity;
- the published interaction subject contains no ResourceEndpoint, IP address, protocol or port fields;
- no consumer persistence adapter requires a SQL foreign key into ACC-owned tables or Resource Catalogue tables.

## Downstream revalidation consequence

The following accepted artifacts are `DIRTY` where they depend on zero-or-many Resource bindings:

- `docs/decisions/ADR-015-acc-component-deployment-and-atomic-interaction-contract.md`;
- `docs/domain/application-communication-catalogue/target-model.md`;
- implementation/migration plans based on temporal `DeploymentResourceBinding` multiplicity.

They must be revalidated in S2/S4 as appropriate after this G1 requirement is accepted; they do not override the current requirement merely because they are more detailed.
