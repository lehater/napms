# Web source scope

Apply root `AGENTS.md` first.

## Responsibility

`web/` is the React outer adapter for accepted NAPMS application use cases. It presents backend-owned business truth; it does not create alternate domain, authority or lifecycle semantics.

## Working set

For one Web task:
1. recover the active plan and selected Skill;
2. read only the relevant accepted requirement plus the matching `docs/ui/` guidance;
3. for UI/layout work, read `docs/ui/design-system.md` and `docs/ui/component-composition.md`;
4. inspect the feature-local page/components and only the API boundary used by that feature;
5. avoid repo-wide UI/API scans unless the task is explicitly cross-cutting.

## Structure

- group code by feature/use case;
- treat `src/design-system/` as the durable owner of generic visual primitives, reusable controls, layout and product UI patterns;
- treat `src/components/ui/` as transitional existing generic controls to migrate when touched and ownership is clear;
- keep domain-to-visual mapping and reusable domain presentation under the owning feature's `components/`;
- keep feature pages focused on screen/use-case orchestration and composition;
- compose feature pages from existing design-system patterns before introducing page-local geometry/styling;
- page-root arbitrary `max-width` is not allowed for operational/data workspaces; use semantic constrained layouts only for forms, dialogs or readable prose;
- do not introduce raw color literals in feature code when a semantic design token exists;
- do not recreate shared buttons, inputs, tables, status visuals, tags or loading/error/empty states locally;
- keep transport DTO/request mapping at the frontend API boundary;
- extend shared patterns only after demonstrated reusable need; avoid giant universal page components;
- backend Authority Management remains authoritative for visibility/action admission;
- never invent placeholder business state to complete a screen.

## Validation

Run `npm run build` (or `make web-check` from the repository root) for Web changes.
