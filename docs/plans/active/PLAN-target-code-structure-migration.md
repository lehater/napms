# PLAN — Target Code Structure Migration

Status: `active`

## Goal

Move NAPMS to the accepted final physical taxonomy without product/domain semantic change:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/

web/src/
  app/
  features/
  components/ui/
  lib/
```

## Inputs

- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`
- `docs/decisions/ADR-014-target-code-structure-taxonomy.md`

## Execution order

```text
M1 backend repository boundary
-> M2 bounded contexts + final Clean layers
-> M3 workflows + remove generic composition
-> M4 platform consolidation
-> M5 capability-oriented internals where justified
-> M6 Web final locality
-> M7 compatibility purge + final enforcement
```

## Completed milestones

- M1 — complete in `f0e281e`.
- M2 — complete in PR #74, squash merge `91eb009c2338697458ba3874836c93cc044f753a`.
- M3 — complete in PR #75, squash merge `18787e3f790368dec8d57078b47c7b6454e85b5d`.
- M4 — complete in PR #76, squash merge `a2caf39587c111fe97341686ff92fbeb9d30599d`; post-merge CI path-filter correction complete in PR #77, squash merge `10182694590b6b851d35b9594ecc03823cee811f`.
- M5 — complete in PR #78, squash merge `3bd5525061a382b77d6298ea5d607bd7f2f63179`; Application Catalogue grouped into `curation / discovery / target`, Resource Catalogue deliberately left unsplit, all required hosted gates passed.

## M6 — Web final locality

Status: `M6 implementation complete; awaiting architectural review` on branch `refactor/m6-web-locality`.

Goal: make the frontend feature-local without creating a new generic shared semantic layer.

Final source shape:

```text
web/src/
  app/
    main.tsx
    App.tsx
    routing.ts
    AppShell.tsx
    index.css
  features/<feature>/
    api/          # only when the feature has HTTP/request mapping
    model/        # only when the feature has owned shared types/pure model helpers
    components/   # feature-owned reusable UI
    pages/        # routable feature pages
  components/
    ui/           # genuinely shared visual primitives only
  lib/
    api.ts        # shared transport + ApiError only
    datetime.ts
  vite-env.d.ts
```

Create only feature subdirectories that have actual contents.

### Accepted root ownership

- `App.tsx` -> `app/App.tsx`.
- hash route parsing/types/navigation -> `app/routing.ts`.
- `components/layout/AppShell.tsx` -> `app/AppShell.tsx`.
- `main.tsx` and global `index.css` -> `app/`; update `web/index.html` entrypoint.
- root `api.ts` is deleted, not moved or replaced by another barrel.
- `components/catalogue/CatalogueIdentity.tsx` -> `features/catalogues/components/CatalogueIdentity.tsx`.
- after M6, root `components/` contains only `ui/`.

### Accepted API/model ownership

Shared technical HTTP transport and `ApiError` stay in `lib/api.ts`. Feature code imports them directly; no root API facade remains.

Authentication/session:
- `Actor` -> `features/auth/model/actor.ts`;
- `login/getSession/logout` -> `features/auth/api/session.ts`;
- `LoginPage.tsx` -> `features/auth/pages/LoginPage.tsx`.

Catalogue interaction/presentation model:
- `PortConstraintDto`, `TrafficAlternativeDto`, `CataloguePresentation`, `ProposalInteraction`, and `ProposalInteractionPage` -> `features/catalogues/model/interaction.ts`;
- target catalogue APIs reuse the same `PortConstraintDto` / `TrafficAlternativeDto` instead of keeping a second definition.

Access Rule model:
- `RuleDto` -> `features/rules/model/rule.ts`;
- rule API and proposal/policy consumers import it from the Rules owner.

Proposal feature:
- proposal request functions -> `features/proposals/api/index.ts`;
- `ProposalResult` -> `features/proposals/model/result.ts`;
- `ComposeConnectivityPage.tsx` -> `features/proposals/pages/ComposeConnectivityPage.tsx`.

The tiny `{ scope: string }` response DTO is intentionally kept local to each consuming feature API. Do not create a shared semantic `Scope`/DTO package merely to deduplicate that shape.

### Feature locality normalization

For every existing feature:
- `api.ts` -> `api/index.ts`;
- `model.ts` -> `model/index.ts`;
- `*Page.tsx` -> `pages/`;
- other feature-owned `.tsx` -> `components/`.

Catalogue-specific mapping:

```text
catalogueApi.ts                       -> api/catalogue.ts
resourceWorkspaceApi.ts               -> api/resourceWorkspace.ts
targetCatalogueApi.ts                 -> api/targetCatalogue.ts
targetCatalogueCommands.ts            -> api/targetCommands.ts
targetCatalogueDependencies.ts        -> api/targetDependencies.ts
targetDeploymentInteractionLifecycle.ts -> api/targetDeploymentInteractionLifecycle.ts
targetPresentation.ts                 -> model/targetPresentation.ts
```

All catalogue `*Page.tsx` files move to `pages/`; all remaining catalogue `.tsx` files move to `components/`.

Policy `PolicyViewControls.tsx` is a feature component; all other non-page feature UI follows the same rule.

### Guardrails

- no product/UI behavior change;
- no redesign of routing semantics or URLs;
- no new framework/router dependency;
- root/shared code must not contain feature DTOs or feature request functions;
- `lib/` remains technical only;
- cross-feature semantic reuse imports from the explicit owning feature, never from a new `shared/model` bucket;
- no compatibility barrel at `web/src/api.ts` or old feature paths;
- update all imports directly to final paths.

Add repository architecture enforcement for at least:
- `web/src` root contains only `app`, `features`, `components`, `lib`, `vite-env.d.ts`;
- root `components` contains only `ui`;
- root `api.ts`, root `App.tsx`, root `main.tsx`, root `index.css`, `components/layout`, and `components/catalogue` are absent;
- each feature root contains only the applicable `api / model / components / pages` directories;
- no frontend source imports `@/api`;
- `lib` does not import from `features` or `app`.

## Exit criteria

M6 closes when final Web locality is implemented without behavior change, architecture/locality guards pass, `make web-check`, repository checks relevant to the new guard, and affected browser journeys pass, and one final M6 PR passes all required hosted gates.

## Blockers

None.

## Next

Implement M6 in two atomic commits: first root app/API ownership cleanup, then complete feature directory normalization and enforcement. Run local gates, review the complete milestone, then open one M6 PR and run hosted gates once. Do not start M7 before M6 is squash-merged.
