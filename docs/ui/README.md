# NAPMS Web UI implementation handoff

## Purpose

Translate docs/requirements/web-ui-requirements.md and docs/requirements/scoped-connectivity-inventory.md into implementation-oriented visual and interaction guidance.

This directory does not own domain semantics. Canonical requirements/domain truth wins on conflict.

## Accepted direction

- desktop-first enterprise/control-plane UI;
- Connectivity is the primary post-login workspace;
- selected responsibility scope is prominent global/workspace context;
- resource-centric hierarchical tree-grid is the first overview;
- dark navy collapsible sidebar + light working area;
- dense operational tables/forms over decorative dashboard cards;
- readable catalogue labels first, stable IDs/DDD terms second;
- React + TypeScript + Tailwind CSS + shadcn/ui;
- Tabler-like visual language without a heavyweight admin-theme dependency.

## Product mental model

    Scope
      -> Resources
      -> Component Deployments
      -> Connectivity
          -> Need
          -> Decision
          -> Policy
          -> Realization later

Bounded contexts remain implementation/domain ownership boundaries, not primary user navigation.

## Next useful vertical slice

    Login
      -> Connectivity
      -> choose/default responsibility scope
      -> inspect local Resource / Component connectivity
      -> inspect remote side
      -> open relationship details
      -> Add connectivity from a local Component

A durable Waiting/Under review state is excluded until I16A/I16B accepts decision-process semantics.

## Files

- design-tokens.md — color, typography, spacing, density;
- layout.md — shell, scope context, sidebar and responsive behavior;
- components.md — reusable component inventory;
- screens.md — current screen responsibilities;
- interaction-rules.md — tree-grid/list/form/loading/error behavior;
- implementation-plan.md — UI build order;
- references/ — visual direction only.

Reference screenshots define composition/palette/density direction only. Their sample entities/statuses are not NAPMS truth.
