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
- treat `src/design-system/tokens.css` as the single owner of reusable visual constants: palette, semantic state colors, typography micro-sizes, control/surface geometry, page-width presets, table geometry and shadows;
- feature code may compose layout (`grid`, `flex`, gaps, responsive arrangement), but must not own raw palette values, duplicate reusable visual measurements, local page-width constants, numeric table-width contracts, or independent radius/shadow definitions;
- page width is selected semantically through `PageWorkspace` (`fluid`, `content`, `narrow`), not by feature-local fixed `max-width` values;
- table minimum width is selected semantically through `DataTable` width presets (`compact`, `standard`, `wide`, `extra-wide`), with the actual values owned by tokens;
- `src/components/ui/` is compatibility-only: files there may delegate to design-system components but must not own independent visual implementation; do not add new generic components there;
- keep domain-to-visual mapping and reusable domain presentation under the owning feature's `components/`;
- keep feature pages focused on screen/use-case orchestration and composition;
- when semantic interaction presentation is shared across features, reuse it from the explicit semantic owner rather than duplicating it in a generic shared package;
- compose feature pages from existing design-system patterns before introducing page-local geometry/styling;
- do not introduce raw color literals or Tailwind palette colors in feature code; add/reuse a semantic token or design-system component instead;
- do not recreate shared buttons, inputs, tables, alerts, status visuals, tags or loading/error/empty states locally;
- keep transport DTO/request mapping at the frontend API boundary;
- extend shared patterns only after demonstrated reusable need; avoid giant universal page components;
- extract technical hooks only after equivalent lifecycle semantics are demonstrated by at least two consumers;
- backend Authority Management remains authoritative for visibility/action admission;
- never invent placeholder business state to complete a screen.

## Validation

Run `npm run build` (or `make web-check` from the repository root) for Web changes. The build includes the UI ownership-boundary check, which rejects feature-level legacy UI ownership, raw palette/design constants, local fixed page widths, numeric table-width contracts, and manual HTML tables.
