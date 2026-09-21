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

- group code by feature/use case;
- `src/design-system/` owns generic visual primitives, reusable controls, layout patterns and visual tokens;
- feature code composes those primitives and owns domain-to-visual mapping for its use case;
- extend shared patterns only after demonstrated reusable need; avoid giant universal page components and speculative shared hooks;
- keep transport DTO/request mapping at the frontend API boundary;
- backend Authority Management remains authoritative for visibility/action admission;
- never invent placeholder business state to complete a screen.

Mechanical styling/ownership constraints that can be checked deterministically belong to the Web build/checker rather than being duplicated here. Current human-interface, frontend-architecture and component-design contracts under `docs/contracts/ui/` and `docs/architecture/` own the design semantics; `docs-legacy/ui/` is migration evidence only.

## Validation

Run `npm run build` (or `make web-check` from the repository root) for Web changes. The build includes the UI ownership-boundary checks; inspect the checker failure instead of restating its full rule set in `AGENTS.md`.
