# Web source scope

Apply root `AGENTS.md` first.

## Responsibility

`web/` is the React outer adapter for accepted NAPMS application use cases. It presents backend-owned business truth and must not create alternate domain, authority or lifecycle semantics.

## Task working set

For one Web task:
1. follow task-first routing from root; load the active capsule only when current execution/gate/implementation authorization constrains the task;
2. read the relevant accepted requirement plus the matching current UI contract under `docs/contracts/ui/`;
3. for cross-cutting frontend structure/composition work, read `docs/contracts/ui/mvp-human-interface.yaml`, `docs/architecture/mvp-frontend-architecture.yaml`, and `docs/architecture/mvp-frontend-component-design.yaml`;
4. for verification/implementation work, read the matching current frontend plan under `docs/plans/mvp-frontend-*.yaml`;
5. inspect the feature-local page/components and only the API boundary used by that feature;
6. expand beyond that set only for a concrete cross-cutting dependency or contradiction.

## Structure and ownership

- group product/application code by feature/use case;
- feature-local application modules own query/command orchestration and transport-to-Screen-Model mapping;
- feature rendering imports only the provider-neutral `src/presentation/` facade for accepted presentation patterns;
- `src/presentation/providers/mui/` owns MUI-specific theme, shell and pattern realization; only this provider implementation imports MUI;
- the legacy `src/design-system/` presentation layer has been removed; feature rendering must stay behind the provider-neutral facade;
- canonical visual tokens remain in `docs/contracts/ui/mvp-design-tokens.json` and are generated into the selected provider's theme-token artifact; generated provider tokens are implementation artifacts, not a second authority;
- extend provider-neutral presentation patterns only after demonstrated reusable need; do not mirror the MUI component API behind wrappers;
- keep transport DTO/request mapping at the frontend API boundary;
- backend Authority Management remains authoritative for visibility/action admission;
- never invent placeholder business state to complete a screen.

Mechanical styling/ownership constraints that can be checked deterministically belong to the Web build/checker rather than being duplicated here. Current human-interface, frontend-architecture and component-design contracts under `docs/contracts/ui/` and `docs/architecture/` own the design semantics; `docs-legacy/ui/` is migration evidence only.

## Validation

Run `npm run build` (or `make web-check` from the repository root) for Web changes. The build includes the UI ownership-boundary checks; inspect the checker failure instead of restating its full rule set in `AGENTS.md`.
