# Application Catalogue target HTTP contract

Status: `I31 M3 implementation contract`.

Date: 2026-09-11.

## Purpose

Expose the accepted Application Definition / Application Deployment target through authenticated task-oriented HTTP while keeping compatibility Component Deployment and DCS identities backend-only.

This contract coexists with the I27 catalogue routes until the Web switches to the target information architecture in WP-4.

## Trust and identity boundary

The runtime supplies:
- authenticated `actor_id` from the server-side session;
- mutation `effective_time` from the server clock;
- internal compatibility Component Deployment and DCS identities.

Mutation requests supply an `Idempotency-Key` and, for updates/retirement, `expectedVersion`.

Target request/response DTOs use only target catalogue identities:
- `applicationId` for Application Definition;
- `componentId`;
- `interactionDefinitionId`;
- `applicationDeploymentId`;
- `deploymentInteractionId`;
- `bindingReference` for temporal membership maintenance.

`componentDeploymentId` and `dcsContractRevisionId` are not target authoring concepts and are not exposed by these routes.

## Bounded reads

All potentially unbounded reads are server-backed. `pageSize` is bounded to `1..200`; responses return exact `total` and never require the client to load the whole catalogue to calculate counts.

Definition working set:
- `GET /api/v1/catalogues/application-definitions`
- `GET /api/v1/catalogues/application-definitions/{applicationId}`
- `GET /api/v1/catalogues/application-definitions/{applicationId}/components`
- `GET /api/v1/catalogues/application-definitions/{applicationId}/interactions`
- `GET /api/v1/catalogues/application-definitions/{applicationId}/deployments`

Deployment working set:
- `GET /api/v1/catalogues/application-deployments`
- `GET /api/v1/catalogues/application-deployments/{applicationDeploymentId}`
- `GET /api/v1/catalogues/application-deployments/{applicationDeploymentId}/available-interactions`
- `GET /api/v1/catalogues/application-deployments/{applicationDeploymentId}/connectivity`
- `GET /api/v1/catalogues/deployment-interactions/{deploymentInteractionId}/resources/{side}`

Supported filters/sorts correspond to the accepted UI fields. `available-interactions` is a server-side difference projection: it returns Active Interaction Definitions of the Deployment's Definition that are not already selected by an Active Deployment Interaction.

## Temporal projection

Deployment connectivity Resource counts and Resource-set membership are effective-time projections.

Both routes accept optional offset-aware `asOf`. When omitted, the runtime supplies one server-clock instant. That same instant is used for all effective membership/count calculations in the response.

Resource-set rows expose:
- `bindingReference`;
- `bindingVersion`;
- `resourceReference`;
- Resource display name when available;
- effective Responsibility Scope references;
- membership `validFrom` / `validTo`.

Responsibility Scope display/filter enrichment is a query-only composition of ACC membership and RC-owned Resource facts. It does not transfer lifecycle or mutation ownership between bounded contexts. Resource Type is not exposed because the accepted Resource Catalogue model has no such fact.

## Target mutation tasks

Definition and Component:
- `POST /api/v1/catalogues/application-definitions`
- `POST /api/v1/catalogues/application-definitions/{applicationId}/metadata`
- `POST /api/v1/catalogues/application-definitions/{applicationId}/components`
- `POST /api/v1/catalogues/application-components/{componentId}/metadata`

Interaction Definition:
- `POST /api/v1/catalogues/application-definitions/{applicationId}/interactions`
- `POST /api/v1/catalogues/interaction-definitions/{interactionDefinitionId}/endpoints`
- `POST /api/v1/catalogues/interaction-definitions/{interactionDefinitionId}/traffic`

Application Deployment and selection:
- `POST /api/v1/catalogues/application-deployments`
- `POST /api/v1/catalogues/application-deployments/{applicationDeploymentId}/context`
- `POST /api/v1/catalogues/application-deployments/{applicationDeploymentId}/interactions`

Interaction-scoped Resource membership:
- `POST /api/v1/catalogues/deployment-interactions/{deploymentInteractionId}/resource-bindings`
- `POST /api/v1/catalogues/deployment-interactions/{deploymentInteractionId}/resource-bindings/{bindingReference}/end`

Traffic is authored only on Interaction Definition. Deployment selection never accepts traffic overrides.

## Retirement and dependency explanation

Terminal retirement commands:
- `POST /api/v1/catalogues/application-definitions/{id}/retire`
- `POST /api/v1/catalogues/application-components/{id}/retire`
- `POST /api/v1/catalogues/interaction-definitions/{id}/retire`
- `POST /api/v1/catalogues/application-deployments/{id}/retire`
- `POST /api/v1/catalogues/deployment-interactions/{id}/retire`

Dependency projection:
- `GET /api/v1/catalogues/retirement-dependencies/{subjectKind}/{subjectId}` returns non-zero groups with exact `count` and a bounded preview;
- `GET /api/v1/catalogues/retirement-dependencies/{subjectKind}/{subjectId}/{dependencyKind}` returns one exact server-paged dependency group.

Peer dependency semantics remain owner-defined:
- Connectivity Requirements decides Active/effective Requirement applicability;
- Connectivity Decision decides current/effective non-superseded Decision state;
- Access Policy decides active/effective Rule state;
- ACC decides its local structural, Resource-binding and legacy coexistence dependencies.

Blocked mutations return `409 CatalogueDependencyBlocked` with grouped exact counts and bounded previews. No hard-delete route exists.

## Error semantics

Expected transport mappings:
- unauthenticated -> `401 AuthenticationRequired`;
- authority denied -> `403 CatalogueAuthorityDenied`;
- missing subject -> `404 CatalogueSubjectNotFound`;
- dependency, parent-state, concurrency, duplicate-selection or idempotency conflict -> `409` with a stable symbolic code;
- invalid target input/time/sort -> `422`;
- persistence unavailable/unknown -> `503`.

Framework exception names, SQL details, compatibility IDs and raw peer persistence records are never public.
