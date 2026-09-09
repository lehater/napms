# NAPMS Web UI implementation guidance

## Purpose

This directory owns implementation-oriented presentation and interaction guidance for the Web outer adapter.

Canonical product behavior is owned by `docs/requirements/web-ui-requirements.md` and feature requirements such as `docs/requirements/scoped-connectivity-inventory.md`. Domain meaning/authority remains owned by domain/application contracts.

When UI guidance would need to restate a business lifecycle, authority rule, semantic identity or cross-context status meaning, link to the canonical owner instead.

## Visual/implementation direction

- desktop-first enterprise/control-plane UI;
- dark navy collapsible sidebar + light working area;
- dense operational tables/forms over decorative dashboard cards;
- readable catalogue labels first, stable IDs/DDD terms second;
- React + TypeScript + Tailwind CSS + shadcn/ui;
- accessibility target WCAG 2.2 AA;
- extract shared visual abstractions only after demonstrated reuse.

## Files

- `design-tokens.md` — color, typography, spacing and density.
- `layout.md` — shell, workspace layout and responsive behavior.
- `components.md` — reusable component responsibilities.
- `screens.md` — screen-level presentation responsibilities.
- `interaction-rules.md` — URL/tree-grid/form/loading/error interaction mechanics.
- `references/` — visual direction only.

Execution sequencing does not belong here. Current UI work is selected by `docs/plans/active/README.md` / the active plan and the durable roadmap in `docs/engineering/`.

Reference screenshots define composition/palette/density direction only. Their sample entities/statuses are not NAPMS truth.
