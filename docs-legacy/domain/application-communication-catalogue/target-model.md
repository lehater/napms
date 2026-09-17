# Application Communication Catalogue — Target Domain Model

Status: `S2 affected-edge revalidated; target Tactical model aligned 2026-09-16`.

Canonical MVP Tactical model: `target-tactical-model.md`.

ACC owns reusable Application/Component/Interaction meaning and immutable traffic-contract revisions. Concrete Component Deployment belongs to the separate Application Deployment context.

## MVP modelling rule

Model only domain semantics required for the minimal end-to-end happy path. Preserve stable identities and immutable decision-relevant communication contracts; defer richer workflows/version presentation/persistence concerns.

## Strategic shape

```text
ApplicationDefinition
  -> Component

ApplicationDefinition
  -> Interaction
      -> source Component
      -> destination Component
      -> current InteractionContractRevision

InteractionContractRevision
  -> immutable trafficAlternatives[1..N]
```

### ApplicationDefinition

Stable ACC-owned identity grouping Components and declared Interactions. It describes the application definition, not a deployment.

### Component

Stable ACC-owned application role inside exactly one ApplicationDefinition. Parent Application identity is immutable for the Component lifetime.

### Interaction

Stable ACC-owned directed communication template between two Components of the same ApplicationDefinition.

MVP invariants:

- both endpoints belong to the same ApplicationDefinition;
- cross-Application Interaction is invalid;
- self-interaction is valid;
- at most one Interaction exists for one directed Component pair;
- reverse direction is a different Interaction;
- endpoints are immutable;
- traffic changes preserve Interaction identity but create a new immutable contract revision.

### InteractionContractRevision

Immutable decision-relevant traffic snapshot for one Interaction.

A material traffic change creates a new revision identity while old revisions remain historically resolvable.

The revision contains the complete atomic set of vendor-neutral traffic alternatives. Consumers may not authorize/materialize only one preferred subset of a revision.

An exact revision reference also identifies its owning Interaction and therefore its source/destination Component definitions. Access Policy does not need to duplicate `InteractionRef` next to `revisionRef` solely to interpret one exact revision.

Changing the ACC-current revision does not silently change an existing Policy Rule. A Policy Rule remains on its currently effective exact revision until its own accepted change lifecycle advances it.

The target does **not** require a rich revision workflow, version-number scheme, supersession state machine or independently editable revision aggregate for MVP.

## Lifecycle baseline

Application/Component/Interaction keep the minimal retirement baseline where accepted dependency rules allow it. No richer state machine is introduced for the happy path.

Published InteractionContractRevisions are immutable historical contract truth and are not rewritten after downstream reference.

## Published semantic contracts

ACC publishes:

```text
ApplicationRef
ComponentRef
InteractionRef
InteractionContractRevisionRef
current Interaction contract revision
immutable revision resolution
```

Application Deployment consumes `ComponentRef` and owns concrete `ComponentDeployment(ComponentRef, ResourceRef)` truth.

Access Policy uses the exact immutable revision as proposed/current traffic semantics for one concrete ComponentDeployment pair.

Required Policy Materialization resolves that revision and preserves its complete traffic semantics.

Evidence Access Recognition may use public revision/Interaction meaning to correlate observed traffic but cannot create or modify ACC truth.

## Resource realization semantics

None belong to ACC:

```text
ACC Interaction/Component/revision semantics
+ AD concrete ComponentDeployment -> ResourceRef
+ RC Resource -> effective HostAddress | Prefix
```

Address/deployment changes do not alter ACC Interaction or contract-revision identity.

## Cross-context rule

Consumers treat published references as opaque semantic identities rather than relational foreign keys into ACC storage.

## Deliberately deferred beyond MVP

- revision numbering/version-string presentation;
- draft/publish/review workflow for catalogue revisions;
- richer lifecycle states;
- persistence/repository structure;
- migration from the implemented legacy ApplicationDeployment / DeploymentInteraction / compatibility ComponentDeployment shape;
- richer communication-contract semantics not required by the first end-to-end scenario.

Endpoint/network realization is not ACC ownership.
