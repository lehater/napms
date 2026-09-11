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

Status: `implementation and architectural review complete; final hosted PR gates pending` on branch `refactor/m6-web-locality`.

Final source shape:

```text
web/src/
  app/
  features/<feature>/
    api/          # when present
    model/        # when present
    components/   # when present
    pages/        # when present
  components/
    ui/
  lib/
  vite-env.d.ts
```

Accepted ownership:
- application bootstrap, hash routing, shell and global CSS live under `app/`;
- root `api.ts` is deleted rather than replaced by another barrel;
- `lib/api.ts` owns only shared HTTP transport and `ApiError`;
- auth session/API/model are feature-local under `features/auth`;
- catalogue interaction/presentation DTOs are owned by `features/catalogues/model`;
- `RuleDto` is owned by `features/rules/model`;
- proposal API/result/page are owned by `features/proposals`;
- catalogue-specific reusable UI is under `features/catalogues/components`;
- root `components/` contains only shared visual primitives in `ui/`;
- cross-feature semantic reuse imports from the explicit owning feature; there is no generic shared semantic model package.

Architecture review confirms:
- `web/src` root contains only `app`, `features`, `components`, `lib`, and `vite-env.d.ts`;
- root `components` contains only `ui`;
- legacy root `api.ts`, `App.tsx`, `main.tsx`, `index.css`, `components/layout`, and `components/catalogue` are absent;
- feature roots contain only applicable `api / model / components / pages` directories;
- frontend source no longer imports `@/api`;
- `lib/` does not depend on `app/` or `features/`;
- routing URLs and product/UI behavior remain unchanged;
- the J03 browser change only waits for the existing debounce search HTTP response before selection and does not weaken journey assertions.

Validation evidence:
- `make web-check`: passed;
- architecture tests: 72 passed;
- `make test`: 815 passed, 141 deselected;
- `make harness-check`: passed;
- `make knowledge-check`: passed;
- local Docker browser journeys: 3 passed.

## Exit criteria

M6 closes when the reviewed Web locality remains behavior-preserving and one final M6 PR passes all required hosted gates.

## Blockers

None.

## Next

Open one M6 milestone PR, mark it ready once, run the required hosted gates, and squash-merge if all pass. Do not start M7 before M6 is merged.
