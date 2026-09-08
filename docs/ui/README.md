# NAPMS Web UI implementation handoff

## Purpose

Translate the accepted product/UX requirements in `docs/requirements/web-ui-requirements.md` into implementation-oriented visual and interaction guidance.

This directory does not own domain semantics. If examples or labels here conflict with canonical requirements/domain truth, the canonical layer wins.

## Accepted direction

- desktop-first enterprise/control-plane UI;
- dark navy collapsible sidebar + topbar;
- light working area;
- blue primary accent;
- dense operational tables/forms over decorative dashboard cards;
- React + TypeScript + Tailwind CSS + shadcn/ui;
- Tabler-like visual language without a heavyweight admin-theme dependency.

## First useful vertical slice

```text
Login
  -> Compose Connectivity
  -> ConnectivityDecision result
  -> Allowed: Access Rule summary/details
```

Approval workflow and persistent generic Access Request lifecycle are deliberately outside I8.

## Files

- `design-tokens.md` — color, typography, spacing, radius/density;
- `layout.md` — application shell and responsive behavior;
- `components.md` — reusable component inventory;
- `screens.md` — accepted screen responsibilities;
- `interaction-rules.md` — list/form/loading/error behavior;
- `implementation-plan.md` — UI build order;
- `references/napms-dashboard-reference.png` — visual direction only.

The reference screenshot stored in the repository is a scaled visual preview for composition, palette and density only. It is not a pixel/dimension source of truth, and its sample entities/statuses are not NAPMS domain truth.
