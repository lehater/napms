# Application Catalogue Target Migration Roadmap

Status: `I31 complete and absorbed`.

Date: 2026-09-11.

## Purpose

Record the completed I31 migration from the I27 Application-side catalogue model to the accepted Application Definition / Application Deployment model while preserving existing Connectivity Requirement, Connectivity Decision, Access Rule and policy-export truth.

Current runtime truth is summarized in `docs/engineering/current-state.md`. Current ACC Tactical DDD is `docs/domain/application-communication-catalogue/tactical-model.md`. Product and architecture contracts remain in `docs/requirements/application-catalogue-target.md`, `docs/architecture/application-catalogue-target-boundary.md`, ADR-012 and ADR-013.

## Completion summary

All ordered stages are complete:

| Stage | Outcome |
| --- | --- |
| M0 | compatibility projection, edit semantics, metadata/context ownership and retirement dependency contract closed in PR #58 |
| M1 | target Domain/Application entities, invariants, ports and compatibility contracts implemented in PR #59 |
| M2 | additive PostgreSQL persistence and per-Deployment-Interaction compatibility projection implemented in PR #60 |
| M3 | bounded target HTTP/read models, task commands and dependency drill-downs implemented in PR #61 |
| M4 | Definitions/Deployments Web IA, target authoring/editing, Deployment connectivity and Resource membership implemented in PR #62 |
| M5 | target-authored downstream acceptance, deterministic screenshot regression and canonical/current-state absorption completed in PR #63 |

## Current model

```text
Application Definition
  -> Components
  -> Interaction Definitions

Application Deployment
  -> Application Definition
  -> Company / Environment / Scope context
  -> selected Deployment Interactions

Deployment Interaction
  -> Interaction Definition
  -> Source Resource set
  -> Destination Resource set
  -> internal compatibility projection
      -> source compatibility ComponentDeployment
      -> destination compatibility ComponentDeployment
      -> immutable current DcsRevision
      -> existing DirectedInteractionIdentity
```

Compatibility Component Deployment identities remain internal implementation identities, unique per Deployment Interaction side and stable for that Deployment Interaction lifetime. New Application authoring does not expose them as concepts the user must understand.

## Preserved semantics

I31 did not perform a cross-context identity migration. Existing downstream Requirement, Decision, Rule and export records continue to use the stable directed interaction triple they already own/consume.

Interaction Definition traffic is current reusable ACC intent. Permitted traffic edits create new immutable DCS snapshots for active Deployment Interactions while preserving earlier snapshots and historical downstream references. Unsafe edits and retirements fail closed on explicit owner-reported active/effective dependencies.

Existing pre-I31 Component Deployments, DCS revisions and Deployment Resource Bindings remain valid legacy ACC/downstream truth. They are not synthesized into Application Deployments because Company/Environment/Scope and target interaction ownership cannot be inferred safely.

## Product result

The current Application Catalogue supports:

- `Applications -> Definitions | Deployments` bounded working sets;
- Definition Overview / Components / Interactions / Deployments;
- Application Deployment with Company/Environment/Scope context;
- selection of any subset of Definition interactions;
- interaction-scoped Source/Destination Resource membership;
- bounded server-side paging/search/filter/sort and dependency drill-downs;
- terminal retirement with no hard-delete path;
- target-authored interaction consumption through existing Connectivity / Requirement / Decision / Access Policy behavior.

## Acceptance evidence

J01 creates target Application Catalogue truth, binds Resources to a Deployment Interaction, creates a Connectivity Requirement through the target-authored compatibility interaction, records an Allowed final Decision and materializes the resulting Access Rule. J03 remains an independent regression over the existing downstream/demo path.

Representative Application layouts are protected by deterministic pixel-derived screenshot fingerprints for:

- Definitions list;
- Definition Interactions;
- Deployment Connectivity.

The final implementation head before documentation absorption passed Core, PostgreSQL persistence, Web, Harness, Docker local runtime and Browser journey gates. The final documentation head is revalidated before integration.

## Deferred candidates

I31 intentionally does not introduce:

- Application Definition versioning;
- Deployment-specific endpoint/traffic overrides;
- automatic semantic migration of legacy Component Deployments into Application Deployments;
- Company/Organization/Person/Team/Responsibility Scope aggregate ownership;
- Resource type inference from technical realization;
- generic CMDB/custom-field behavior;
- hard delete.

Any such expansion requires a new accepted requirement/domain change.
