# Web source scope

Apply root `AGENTS.md` first.

## Responsibility

`web/` is the React outer adapter for accepted NAPMS application use cases. It presents backend-owned business truth and must not create alternate domain, authority or lifecycle semantics.

## Task working set

For one Web task:
1. follow task-first routing from root; load the active capsule only when current execution/gate/implementation authorization constrains the task;
2. read the relevant accepted requirement plus matching `docs/ui/` guidance;
3. for reusable UI/layout work, read `docs/ui/design-system.md` and `docs/ui/component-composition.md`;
4. inspect the feature-local page/components and only the API boundary used by that feature;
5. expand beyond that set only for a concrete cross-cutting dependency or contradiction.

## Structure and ownership

- group code by feature/use case;
- `src/design-system/` owns generic visual primitives, reusable controls, layout patterns and visual tokens;
- feature code composes those primitives and owns domain-to-visual mapping for its use case;
- extend shared patterns only after demonstrated reusable need; avoid giant universal page components and speculative shared hooks;
- keep transport DTO/request mapping at the frontend API boundary;
- backend Authority Management remains authoritative for visibility/action admission;
- never invent placeholder business state to complete a screen.

Mechanical styling/ownership constraints that can be checked deterministically belong to the Web build/checker rather than being duplicated here. `docs/ui/design-system.md` and `docs/ui/component-composition.md` own the human-readable design contracts.

## Validation

Run `npm run build` (or `make web-check` from the repository root) for Web changes. The build includes the UI ownership-boundary checks; inspect the checker failure instead of restating its full rule set in `AGENTS.md`.
