# Application Communication Catalogue — Target Domain Model

Status: `S2 affected-edge revalidated; target Tactical model aligned 2026-09-15`.

Canonical MVP Tactical model: `target-tactical-model.md`.

Earlier ACC-owned `ComponentDeployment`, Resource binding and `DirectedInteractionIdentity` semantics are superseded by the Application Deployment boundary decision.

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
- self-interaction is valid;
- at most one Interaction exists for one directed Component pair;
- reverse direction is a different Interaction;
- endpoints are immutable;
- traffic changes preserve Interaction identity but create a new immutable contract revision.

### InteractionContractRevision

Immutable decision-relevant traffic snapshot for one Interaction.

Downstream governance keys on `InteractionContractRevisionRef`, so a material traffic change creates a new revision identity while old revisions remain historically resolvable.

The revision contains the complete atomic set of vendor-neutral traffic alternatives. Consumers may not authorize/materialize only one preferred subset of a revision.

The target does **not** require a rich revision workflow, version-number scheme, supersession state machine or independently editable revision aggregate for MVP. Those are deferred unless a concrete product journey requires them.

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

AD consumes Application/Component identity and owns deployment/placement.

AG/AP use the exact immutable contract revision in governed-subject identity.

RPM resolves that revision and preserves its complete traffic semantics.

## Resource realization semantics

None belong to ACC:

```text
ACC Interaction/Component semantics
+ AD ComponentPlacement -> ResourceRef
+ RC Resource -> effective HostAddress | Prefix
```

Address/placement changes do not alter ACC Interaction or contract-revision identity.

## Cross-context rule

Consumers treat published references as opaque semantic identities rather than relational foreign keys into ACC storage.

## Deliberately deferred beyond MVP

- revision numbering/version-string presentation;
- draft/publish/review workflow for catalogue revisions;
- richer lifecycle states;
- persistence/repository structure;
- migration from the implemented legacy ApplicationDeployment / DeploymentInteraction shape;
- richer communication-contract semantics not required by the first end-to-end scenario.

Endpoint selection is not an ACC deferred question: the current target deliberately has no endpoint model.
