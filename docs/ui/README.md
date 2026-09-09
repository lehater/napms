# NAPMS Web UI implementation handoff

## Purpose

Translate the accepted product/UX requirements in `docs/requirements/web-ui-requirements.md` into implementation-oriented visual and interaction guidance.

This directory does not own domain semantics. If examples or labels here conflict with canonical requirements/domain truth, the canonical layer wins.

## Product-class reference

NAPMS is designed as a desktop-first professional network/infrastructure operations application.

NetBox is an accepted **class-of-product UX reference** for:
- sustained desktop use by technical operators;
- dense object tables;
- explicit filtering/search/pagination;
- bookmarkable object detail pages;
- persistent application navigation;
- compact forms/property views;
- responsive compatibility without turning the product into a mobile-first application.

This is not a visual clone, dependency or information-architecture template. NAPMS keeps its own Requirement -> Decision -> Access Policy workflows and its own design system.

## Accepted direction

- desktop-first operational/control-plane UI;
- primary quality baseline at 1440px-class desktop, fully usable from 1280px;
- dark navy persistent desktop sidebar + topbar;
- off-canvas/collapsible navigation below desktop rather than a separate mobile navigation taxonomy;
- light working area;
- blue primary accent;
- dense operational tables/forms/detail pages over decorative dashboard cards;
- wide data regions use bounded horizontal overflow rather than expanding the whole document;
- React + TypeScript + Tailwind CSS + shadcn/ui;
- Tabler-like visual language without a heavyweight admin-theme dependency;
- WCAG 2.2 AA and role/label-driven browser testing.

## Files

- `design-tokens.md` — color, typography, spacing, radius/density;
- `layout.md` — application shell, desktop baseline and responsive behavior;
- `components.md` — reusable component inventory;
- `screens.md` — accepted screen responsibilities;
- `interaction-rules.md` — list/form/loading/error/operator behavior;
- `implementation-plan.md` — UI build order and quality work;
- `references/napms-dashboard-reference.png` — original visual direction only.

The stored reference screenshot is a visual preview for composition, palette and density only. It is not a pixel/dimension source of truth, and its sample entities/statuses are not NAPMS domain truth.
