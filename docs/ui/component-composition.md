# Web UI Component Composition

Status: `accepted implementation guidance`.

Roadmap: `docs/engineering/web-ui-component-composition-roadmap.md`.

This document defines ownership and composition rules for reusable React UI in NAPMS. Product/domain semantics remain owned by canonical domain/requirements/architecture artifacts; visual tokens and detailed reference behavior remain owned by `docs/ui/design-system.md`.

## Purpose

Make a component's location communicate its responsibility and expected reuse boundary.

The target dependency/composition direction is:

```text
semantic tokens
  -> design-system primitives
    -> generic design-system components
      -> reusable product/UI patterns
        -> feature components
          -> feature pages
```

Higher layers compose lower layers. Generic layers do not depend on feature/domain semantics.

## Ownership

### Design-system primitives

Own the smallest stable visual/layout building blocks.

Inputs: generic content and visual props.

Outputs: token-based geometry/styling.

They do not know NAPMS domain vocabulary.

### Design-system components

Own reusable generic controls and focused visual components used across unrelated features.

Examples include buttons, inputs/selects, checkbox, table pieces, search input, tags, status indicators and loading/error/empty states.

A generic component may expose semantic visual tones such as positive/warning/critical/neutral. It must not expose business states such as `Allowed`, `Covered`, `Required`, `RetiredApplication`, or `NoFinalDecision`.

### Design-system layout

Own stable page/application geometry such as workspace and page-header structure.

### Design-system patterns

Own reusable compositions of generic components with stable interaction/layout semantics.

Examples may include catalogue toolbars/paging, dialog shells, detail sections/rows and inline-edit interaction after concrete reuse is demonstrated.

Patterns provide focused composition slots. They must not become universal prop-driven page/form/CRUD frameworks.

### Feature components

Own reusable presentation and domain-to-visual mapping within one feature.

A feature component may know feature DTO/view-model types and domain vocabulary. Examples include `DecisionStatus`, `PolicyStatus`, `RequirementAlignment`, endpoint presentation or application/deployment cards.

If another feature needs the same domain meaning, reuse it from the explicit semantic owner rather than copying it into a root shared namespace.

### Feature pages

Own screen-level/use-case orchestration:

- load/select screen data;
- coordinate feature actions;
- integrate routing/navigation;
- compose design-system patterns and feature components;
- map screen events to feature API/application actions.

Pages should not act as local component libraries. Page-local helper components are appropriate only when they are genuinely one-screen details with no stable independent responsibility.

## Extraction decision

Classify a candidate in this order:

1. Domain-specific meaning -> feature component.
2. Generic control/visual behavior useful across unrelated features -> design-system component.
3. Stable reusable composition of generic UI -> design-system pattern.
4. Pure technical React/helper behavior with no product semantics and genuine cross-feature reuse -> `lib/`.
5. One consumer or unstable responsibility -> keep local.

Reuse is demonstrated, not predicted. Prefer a second concrete consumer before extracting a composition pattern, except for an obviously stable primitive/control contract.

## Composition rules

- Prefer children/slots and small focused props over inheritance and large mode/variant matrices.
- Keep domain-to-tone mapping in feature code; render through generic status/tag primitives.
- Keep server-backed filtering, sorting and paging semantics with the feature/read model; generic UI patterns own presentation and interaction contracts only.
- Keep feature-specific forms as feature components even when they use a generic dialog shell.
- Extract technical hooks only when lifecycle, cancellation, error and refresh semantics are genuinely equivalent across at least two consumers.
- Do not build an ad-hoc server-state framework through generic hooks. If server-state orchestration becomes a broad concern, evaluate that architecture/dependency explicitly.

## Namespace rule

`web/src/design-system/` is the durable owner of generic visual primitives, components, layout and reusable product UI patterns.

`web/src/components/ui/` is existing transitional structure. During the component-composition migration, move a generic control to `design-system/components/` when its ownership is touched and clear. Migrate consumers directly; do not create compatibility facades or preserve two permanent generic UI namespaces.

## Quality signals

A healthy feature page reads primarily as orchestration and composition. Its JSX should expose the screen anatomy rather than reimplementing controls, badges, dialog frames or repeated sections.

Large file size alone does not require splitting. Split when a unit has an independent responsibility/change reason, is reused, or hides the page's screen-level composition.

## Anti-patterns

Avoid:

- page-local copies of buttons/inputs/status badges/tables/page states;
- a generic design-system component containing NAPMS domain vocabulary;
- a giant `EntityPage`, `CRUDPage`, `UniversalForm` or equivalent abstraction;
- root-level `shared/model` business types;
- hooks whose only purpose is to hide one page's state variables;
- speculative abstractions created before stable responsibility is understood;
- duplicated generic ownership between `components/ui` and `design-system/components`.

## Review checklist

For new or changed UI:

- Is the page limited to screen/use-case orchestration plus truly local details?
- Is reusable domain presentation under the owning feature's `components/`?
- Is generic visual behavior composed from the design system?
- Does any proposed shared component contain domain vocabulary that should remain feature-owned?
- Is an abstraction supported by demonstrated reuse or a stable primitive contract?
- Can the same result be achieved by composing smaller existing components instead of adding a universal mode-driven component?
- Are user-visible semantics preserved unless a separate accepted product change says otherwise?
