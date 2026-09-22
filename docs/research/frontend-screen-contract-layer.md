# Frontend Screen Contract Layer — NAPMS research pilot

Status: RESEARCH  
Branch: `research/frontend-screen-contract-layer`

## Goal

Validate the smallest provider-neutral knowledge package that lets a coding agent realize a browser screen without inventing product capabilities from a presentation template.

Harness proposal: `lehater/harness/docs/research/frontend-screen-contract-layer-v1.md`.

## Findings

### P0 — screen inventory/presentation inheritance was mistaken for semantic closure

The existing `check_frontend_design_closure.py` proves that navigation workspaces, Screen/View entries and Presentation System patterns line up. It does not prove that a screen can actually obtain its data, invoke its actions, map backend outcomes, or realize a permitted presentation feature.

The new pilot checker imports Harness `frontend_screen_contracts.py` and proves those obligations for selected screens.

### P0 — Resource Catalogue had no modern canonical read contract

`RESOURCE-CATALOGUE` requires the user to locate/select a Resource, but the modern first-MVP OpenAPI had:

- `POST /v1/resources`;
- `GET /v1/resources/{resourceRef}`;

and no canonical list operation.

At the same time Screen/View Design selected `FILTER-BAR` and a search/filter region. Those capabilities came from presentation composition rather than accepted product/interface semantics.

The pilot adds only:

```text
GET /v1/resources
  -> ResourceCatalogueView
     -> items[]
        - resourceRef
        - displayName
        - authorityScopeRef
```

It intentionally does not add search, filtering, user-selectable sorting, pagination, bulk operations, edit or delete.

The existing legacy/pilot `/api/v1/catalogues/**` queries remain evidence of prior implementation. They are not silently promoted into the modern first-MVP interface contract.

### P0 — template capability inheritance needed a deny-by-default rule

Reusable CRUD/Dashboard templates commonly contain search, filtering, sorting, paging, bulk actions, edit/delete and demo routes/entities. A pattern/provider is now treated as an offer, not authority.

The Screen/View contract has:
- an allowed semantic capability set;
- backing for every allowed capability by read/command/navigation/local semantics;
- notable exclusions;
- pattern feature bindings.

Anything not explicitly bound is disabled.

### P1 — Screen/View model boundary was implicit

The existing Resource Detail contract mapped `ResourceView` fields, but Screen/View Design did not name a semantic model boundary. The pilot adds explicit models:

- `ResourceCatalogueScreenModel`;
- `ResourceDetailScreenModel`;
- `PolicyExportScreenModel`.

The executable adapter remains Component Design/implementation responsibility.

### P1 — error/state closure was not machine checked

The old Screen/View state list could contain states unsupported by the operation contract.

Example: `POLICY-EXPORT` declared `conflict`, while `materializeCurrentPolicy` has no `409` response. The pilot removes that state and maps COMPLETE/UNRESOLVED directly from `PolicyMaterializationResult.status`.

### P1 — rendered conformance was only prose

Each pilot screen now carries three proof families:
- contract;
- semantic state/behavior;
- rendered presentation conformance.

These are verification obligations, not screenshots as authority.

### P2 — full frontend semantic closure remains partial

The pilot intentionally proves only:
- `RESOURCE-CATALOGUE`;
- `RESOURCE-DETAIL`;
- `POLICY-EXPORT`.

The other six workspaces remain explicit in `coverage.semantic_contract_pilot.remaining`. The branch therefore does not pretend that all frontend subjects have been semantically closed.

## Target ownership

| Knowledge | Authority / owner | Producer | Consumer |
| --- | --- | --- | --- |
| Product capability | Product / Domain / Application | requirements/use-case/journey design | Interface Design |
| Query/read operation | INTERFACE-DESIGN | machine-interface contract | Screen/View + frontend adapter |
| Command operation | INTERFACE-DESIGN | machine-interface contract | Screen/View + frontend adapter |
| Human task/navigation semantics | INTERFACE-DESIGN | Human Interface Design | Screen/View |
| Semantic Screen/View Model | INTERFACE-DESIGN | Screen/View Design | frontend adapter/components |
| State/error mapping | INTERFACE-DESIGN | Screen/View Design | frontend feature controller |
| Permission meaning | SECURITY + INTERFACE-DESIGN | security/interface contracts | Screen/View/frontend |
| Presentation pattern vocabulary | INTERFACE-DESIGN | Presentation System | Screen/View |
| Provider/template feature activation | INTERFACE-DESIGN | Screen/View mapping | Component Design/implementation |
| Runtime/cache/aggregation placement | SYSTEM-ARCHITECTURE | frontend architecture | Component Design |
| DTO -> screen model transformation code | COMPONENT-DESIGN | API/feature adapter | presentation components |
| Rendered proof | VERIFICATION/TEST-DESIGN | verification/test design + implementation evidence | coverage/review |

No new Authority is required.

## Representation boundaries

```text
HTTP/backend DTO
  -> frontend query projection
  -> semantic Screen/View Model
  -> private component props
```

For simple Detail screens, the query projection may structurally resemble the transport DTO. It is still mapped into the screen semantic model so transport naming/optionality does not become UI authority.

## BFF decision for NAPMS

A separate deployable BFF is not justified by this pilot.

The current product has one browser interface and the missing Catalogue need can be solved by one read operation in the existing application/interface boundary. Resource Detail is already one direct query. Policy Export already returns an aggregate application result.

Use a dedicated screen-oriented read projection before a BFF when the existing application boundary can own the projection coherently.

Consider a BFF only when a distinct frontend-specific deployable boundary has material independent needs such as:
- different client channels with materially different data/latency constraints;
- repeated cross-service aggregation that should not live in the browser;
- protocol adaptation;
- independent frontend/backend release ownership;
- client-specific security mediation.

Do not move domain or authorization decisions into the BFF.

References:
- Microsoft Azure Architecture Center, Backends for Frontends: https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends
- Microsoft .NET Architecture, API gateway/client aggregation discussion: https://learn.microsoft.com/en-us/dotnet/architecture/microservices/architect-microservice-container-applications/direct-client-to-microservice-communication-versus-the-api-gateway-pattern

## Resource Detail experiment

Chain:

```text
Resource management use case
 -> getResource
 -> ResourceView
 -> ResourceDetailScreenModel
 -> DETAIL / DISCLOSURE / EDITOR mappings
 -> allowed mutations
 -> state/outcome mapping
 -> rendered conformance obligation
```

Result: existing API is sufficient. No BFF/read aggregate is needed.

## Resource Catalogue experiment

Chain:

```text
Locate/select Resource + start creation
 -> listResources + createResource
 -> ResourceCatalogueView
 -> ResourceCatalogueScreenModel
 -> CATALOGUE / STRUCTURED-LIST
 -> only open-resource + create-resource activated
 -> rendered conformance obligation
```

Result: one missing modern read projection was required. Search/filter/sort/etc. were not required.

## Dashboard-like experiment: Policy Export

`materializeCurrentPolicy` is already an application-level aggregate projection. Its result contains:
- completion status;
- evaluation time;
- selected scope;
- export authority evidence;
- rule provenance;
- non-effective rules;
- normalized rows;
- issues.

The Screen/View model consumes that aggregate result directly and maps it to OUTCOME + diagnostics/provenance regions.

Result: a separate dashboard query or BFF is unnecessary for the operation result. If a future passive dashboard needs independent cross-context metrics, it must receive its own accepted aggregate read projection instead of causing browser fan-out.

## Presentation baseline hypothesis

Harness can substantially simplify Presentation System when an external presentation baseline is intentionally adopted:

```text
version-pinned provider baseline
+ semantic pattern vocabulary
+ Screen/View feature bindings
+ project theme/overrides/deviations
+ rendered verification
```

It should not copy the provider's entire visual system into canonical project knowledge.

The current NAPMS frontend uses Tailwind/shadcn and this research branch does not change that implementation choice. A separate non-authoritative MUI provider experiment is recorded in `docs/research/mui-presentation-provider-experiment.yaml`.

Material UI currently documents a CRUD Dashboard template and a Dashboard template; the v9.4.0 template page describes the CRUD Dashboard as CRUD pages with a mobile-friendly, customizable sidebar. The provider experiment pins `v9.4.0` only as a research reference, not as an accepted NAPMS dependency.

Official sources:
- https://mui.com/material-ui/getting-started/templates/
- https://github.com/mui/material-ui/releases/tag/v9.4.0

## Minimal coding-agent package

For a proven screen the agent needs only:

1. Screen/View semantic contract;
2. accepted query/command operations and schemas;
3. semantic Screen/View model mapping;
4. presentation pattern mapping;
5. allowed/excluded capabilities;
6. presentation baseline/theme inheritance if one is accepted;
7. verification obligations.

Frontend Architecture and Component Design then tell the agent where transformation/state code belongs.

## Merge boundary

Harness changes can be merged independently after review because they are provider-neutral and covered by regressions.

NAPMS should merge:
- the minimal modern Resource Catalogue read contract if Product/Interface Design accepts it;
- the corrected Catalogue pattern semantics;
- the three proven screen semantic packages;
- the Harness-backed validator.

Do not merge an MUI dependency/template adoption from this research alone.

Before enabling full frontend completion gating in NAPMS, migrate or explicitly block the remaining six screens so Engineering Coverage cannot report complete from legacy Screen/View presence alone.
