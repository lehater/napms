# Application Catalogue Target Migration Roadmap

Status: `I31 M0 contract closed; final gate pending`.

Date: 2026-09-10.

## Purpose

Migrate the implemented I27 Application Communication Catalogue to the accepted Application Definition / Application Deployment target without rewriting existing Connectivity Requirement, Connectivity Decision, Access Rule or policy-export truth.

Canonical target and M0 closure:
- `docs/decisions/ADR-012-application-definition-deployment-model.md`;
- `docs/decisions/ADR-013-i31-application-catalogue-compatibility-and-reference-semantics.md`;
- `docs/domain/application-communication-catalogue/target-tactical-model.md`;
- `docs/requirements/application-catalogue-target.md`;
- `docs/architecture/application-catalogue-target-boundary.md`;
- `docs/ui/application-catalogue-target.md`;
- `docs/ui/application-catalogue-wireframes.md`.

Current runtime truth remains the I27 implementation until the relevant I31 stage is implemented and absorbed.

## Current-to-target gap

| Layer | Current runtime | Target / selected migration consequence |
| --- | --- | --- |
| Domain identity | `Application -> Component -> ComponentDeployment`; downstream identity is `(sourceComponentDeploymentId, destinationComponentDeploymentId, dcsRevisionId)` | Application Definition retains existing Application ID; Application Deployment / Deployment Interaction are new target identities; each Deployment Interaction projects internally to unique stable compatibility Component Deployment sides plus current immutable DCS revision |
| Interaction semantics | immutable DCS authored between Component Deployments | Interaction Definition is current reusable Component-to-Component traffic intent; endpoint edit is blocked by Active selections; permitted traffic edit creates new DCS snapshots for all Active selections and is blocked by active/effective downstream references |
| Resource binding | temporal binding belongs to Component Deployment | target binding belongs to one Deployment Interaction side and projects to that interaction's unique compatibility Component Deployment side |
| Deployment context | Component Deployment has optional display name only | Application Deployment owns required Company external reference, Environment label and external Responsibility Scope reference; these are context/correlation values, not identity/authority |
| Definition metadata | Application/Component have display name only | Application gains optional description/domain/owner reference; Component gains optional type/description; classifications remain descriptive and open-ended |
| Lifecycle | Active -> Retired with structural I27 blockers | target entities use terminal Active -> Retired; no hard delete; active Resource/downstream/legacy references block relevant operations and are exposed as grouped dependency counts/drill-down |
| Read API | list plus full nested Application workspace | bounded Definition/Deployment/Component/Interaction/Resource/dependency projections with server paging/search/filter/stable sort and totals where required |
| API write model | Component Deployment/DCS/binding commands | target task commands operate on Interaction Definition, Application Deployment, Deployment Interaction and interaction-side Resource binding; compatibility IDs remain backend-only |
| Web IA | monolithic card tree with lifecycle/version/internal IDs | accepted Definitions/Deployments IA, Definition tabs, dense Deployment connectivity table and count drill-downs |
| Acceptance | J01 asserts old deployment/DCS authoring | target J01 plus compatibility proof through unchanged downstream Connectivity/Decision/Access Policy semantics |

## Selected compatibility strategy

```text
Application Definition (existing Application ID)
  -> Component
  -> Interaction Definition

Application Deployment
  -> Deployment Interaction
      -> Interaction Definition
      -> source-side Resource bindings
      -> destination-side Resource bindings
      -> internal compatibility projection
          -> source compatibility ComponentDeployment
          -> destination compatibility ComponentDeployment
          -> current immutable DcsRevision
          -> existing DirectedInteractionIdentity triple
```

Compatibility Component Deployment identities are unique per Deployment Interaction side and stable for that Deployment Interaction lifetime. This preserves interaction-scoped Resource sets while leaving downstream identity types unchanged.

Target side Resource membership is realized through existing temporal Deployment Resource Binding rows attached to the appropriate compatibility side. Target code owns the stronger side/deployment-interaction meaning.

Compatibility identities are internal. New target Web/API authoring does not ask users to understand or assemble Component Deployment/DCS IDs.

## Interaction edit strategy

Source/destination Component replacement is allowed only while an Interaction Definition has no Active Deployment Interaction selection. Otherwise replacement uses a new Interaction Definition and explicit selection replacement.

Traffic edit never rewrites a DCS revision. It is blocked when any affected current compatibility triple has an owner-reported active/effective Connectivity Requirement, effective/final Connectivity Decision or active/effective Access Rule. When admitted, the edit creates a new immutable DCS revision for every Active selection and advances all of them atomically to the new current traffic snapshot.

Historical DCS/downstream references remain unchanged.

## Metadata/context strategy

No Company/Organization/Party/Scope registry is introduced for I31.

- Application `description` and `domain`: ACC descriptive metadata.
- Application `ownerReference`: external responsible-party/team correlation.
- Component `type` and `description`: ACC descriptive metadata; type is not a closed enum.
- Deployment `companyReference`: external correlation.
- Deployment `environment`: ACC-owned descriptive context label, not Network Environment Operations identity.
- Deployment `scopeReference`: external Responsibility Scope correlation using the existing ADR-011 concept.

These values do not define stable identity or grant authority.

## Retirement dependency strategy

Retirement is terminal and non-cascading. Active dependants are cleared first.

The target application/read contract groups non-zero blockers into bounded drill-down categories including Components, Interactions, Application Deployments, Deployment Interactions, Resource Bindings, Connectivity Requirements, Connectivity Decisions, Access Rules and legacy Component Deployments.

Peer contexts remain authoritative for whether their references are active/effective; ACC consumes explicit dependency ports and does not infer peer lifecycle from persistence.

## Legacy coexistence

Existing pre-I31 Component Deployments, DCS revisions and bindings remain valid legacy ACC/downstream truth. They are not promoted automatically into target Deployments or Interaction Definitions because Company/Environment/Scope and target interaction ownership cannot be inferred safely.

Existing Application and Component IDs may be reused as target Definition/Component IDs. Active legacy Component Deployments remain an explicit Component-retirement dependency and continue through a compatibility/maintenance path until explicitly retired or migrated with sufficient business input.

No legacy display name is used to invent target domain meaning.

## Ordered stages

| Stage | Outcome | Main gate |
| --- | --- | --- |
| M0 — contract closure | **closed in PR #58 pending final hosted gate**: compatibility projection, metadata/context ownership, edit semantics and retirement dependencies canonicalized | `knowledge-check` + `harness-check` |
| M1 — domain/application | target entities, invariants, commands, query/dependency ports and compatibility-projection contracts without transport/persistence coupling | domain/application tests + architecture/core gate |
| M2 — persistence/projection | additive PostgreSQL schema persists target entities/mapping while preserving all legacy IDs/facts | migration replay + PostgreSQL integration + compatibility projection tests |
| M3 — HTTP/read models | bounded target command/read APIs with server paging/search/filter/sort and structured dependencies | HTTP contract/security/integration tests |
| M4 — Web target | accepted Definitions/Deployments IA, Definition tabs, Deployment connectivity table and count drill-downs | `make web-check` + deterministic browser target journey |
| M5 — compatibility acceptance/absorption | target-authored data works through Connectivity/Decision/Access Policy; representative screenshot regressions protect layout; current-state docs absorbed | J01 replacement + downstream regressions + Docker/hosted gates |

Each stage is one coherent semantic integration stage and uses its own draft PR/squash merge.

## M0 resolution record

All previous M0 P0 choices are closed by ADR-013 and the target Tactical DDD:

1. downstream compatibility identity — accepted internal per-Deployment-Interaction side projection;
2. Interaction edit boundary — endpoints blocked by Active selections; traffic changes create new immutable snapshots and fail closed on active/effective downstream dependencies;
3. Application metadata — descriptive domain/description plus external owner correlation;
4. Component metadata — descriptive open type/description;
5. Deployment context — external Company/Responsibility Scope references plus descriptive Environment label, none used as identity/authority;
6. retirement dependencies — explicit structural, Resource, downstream and legacy blocker classes with server-derived grouped counts/drill-down.

M1 must not reopen these choices as implementation convenience. A newly discovered contradiction re-enters through `docs/process/domain-change-protocol.md`.

## API/read-model direction after M0

Prefer extending the existing catalogue boundary rather than creating a second parallel catalogue API. Existing `applicationId` remains the Definition identity.

Required capabilities are:
- paged Definition list with target columns/counts, filters, sort and total;
- Definition overview plus separately paged Components, Interaction Definitions and Deployments;
- paged global Application Deployment list;
- Application Deployment overview plus paged selected-interaction connectivity rows;
- paged/searchable/filterable Resource set for one Deployment Interaction side;
- task commands for Interaction Definition, Application Deployment, Deployment Interaction selection and side bindings;
- structured retirement/traffic-edit dependency discovery;
- compatibility Component Deployment/DCS identities kept behind ACC-owned ports/adapters.

Do not retain the current full nested Application workspace as the primary target read contract merely to minimize frontend changes.

## Web direction

The target Web adapter follows `docs/ui/application-catalogue-wireframes.md` for information architecture and actions:
- `Applications -> Definitions | Deployments`;
- dense bounded tables rather than card trees;
- no ordinary Status column/badge for Components or normal Retired rows;
- no user-facing optimistic-concurrency version or implementation UUID noise;
- one connectivity table per Application Deployment;
- Resource collections rendered as counts and opened through bounded drill-down tables;
- inherited traffic read-only in Deployment;
- no hard-delete path.

## Completion criterion

I31 is complete when an admitted user can create/edit an Application Definition, Components and Interaction Definitions, create an Application Deployment, select any subset of its interactions, curate source/destination Resource sets, and consume the resulting interaction through existing Connectivity/Decision/Access Policy semantics without changing historical downstream identities; the accepted target layout is protected by deterministic browser/screenshot regression evidence.
