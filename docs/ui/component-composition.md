# Web UI Component Composition

This document defines current ownership and composition rules for reusable React UI in NAPMS. Product/domain semantics remain owned by requirements/domain/architecture artifacts; visual tokens and shared interaction rules are owned by `docs/ui/design-system.md`.

## Composition direction

```text
semantic tokens
  -> design-system primitives
    -> generic design-system components
      -> reusable UI patterns
        -> feature components
          -> feature pages
```

Higher layers compose lower layers. Generic layers do not depend on feature or domain semantics.

## Ownership

### Visual tokens

`web/src/design-system/tokens.css` owns reusable visual constants: palette and semantic-state colors, typography micro-sizes, radii, shadows, control/surface dimensions, page-width presets and table geometry.

Feature code may choose semantic presentation and screen layout but must not establish a parallel theme or geometry system.

### Design-system primitives and components

Primitives own the smallest stable visual/layout building blocks. Generic components own reusable controls and focused visual elements used across unrelated features.

They accept generic content and visual semantics and do not know NAPMS domain vocabulary. A generic component may expose tones such as positive/warning/critical/neutral; business states remain mapped in feature code.

### Design-system layout and patterns

Shared layout owns stable page/application geometry such as workspace and page-header structure. Reusable patterns own compositions with stable interaction/layout semantics such as catalogue toolbars, pagination, dialog shells and detail sections.

Patterns provide focused composition slots. They do not become universal prop-driven page/form/CRUD frameworks.

### Feature components

Feature components own reusable presentation and domain-to-visual mapping within one semantic feature. They may know feature DTO/view-model types and domain vocabulary.

When another feature needs the same domain meaning, reuse from the explicit semantic owner rather than copying the concept into a root shared namespace.

### Feature pages

Feature pages own screen/use-case orchestration:

- loading/selecting screen data;
- coordinating feature actions;
- routing/navigation integration;
- composing shared patterns and feature components;
- mapping screen events to feature API/application actions.

Pages are not local component libraries. Page-local helpers are appropriate only for genuinely one-screen details with no stable independent responsibility.

## Extraction decision

Classify a candidate in this order:

1. domain-specific meaning -> feature component;
2. generic control/visual behavior useful across unrelated features -> design-system component;
3. stable reusable composition of generic UI -> design-system pattern;
4. pure technical React/helper behavior with no product semantics and demonstrated cross-feature reuse -> `lib/`;
5. one consumer or unstable responsibility -> keep local.

Reuse is demonstrated, not predicted. Prefer a second concrete consumer before extracting a composition pattern, except for an obviously stable primitive/control contract.

## Composition rules

- Prefer children/slots and small focused props over inheritance and large mode/variant matrices.
- Keep domain-to-tone mapping in feature code; render through generic status/tag primitives.
- Keep visual constants in `tokens.css`; feature code does not own raw palette, fixed page widths or repeated geometry constants.
- Structural `grid`, `flex`, gaps and responsive arrangement may remain feature-local when they describe one screen rather than a reusable design-system rule.
- Keep server-backed filtering, sorting and paging semantics with the feature/read model; generic UI patterns own presentation and interaction only.
- Keep feature-specific forms as feature components even when they use a generic dialog shell.
- Extract technical hooks only when lifecycle, cancellation, error and refresh semantics are genuinely equivalent across consumers.
- Do not create an ad-hoc server-state framework through generic hooks.

## Namespace ownership

`web/src/design-system/` is the durable owner of generic visual primitives, components, layout and reusable UI patterns.

`web/src/features/<feature>/` owns feature-specific presentation and screen orchestration. `web/src/lib/` owns genuinely generic technical helpers. `web/src/components/` may contain reusable composition that is not a design-system primitive and does not own domain semantics.

No second generic visual ownership namespace is introduced alongside `web/src/design-system/`.

## Quality signals

A healthy feature page reads primarily as orchestration and composition. Its JSX exposes screen anatomy rather than reimplementing controls, badges, dialog frames or repeated sections.

Large file size alone does not require splitting. Split when a unit has an independent responsibility/change reason, is reused, or hides page-level composition.

## Anti-patterns

Avoid page-local copies of shared controls/page states, raw design constants in feature JSX, feature-owned fixed-width systems, domain vocabulary in generic design-system components, giant universal entity/CRUD/form abstractions, root-level shared business types, hooks that only hide one page's state variables, and speculative abstractions created before responsibility is understood.

## Review checklist

For new or changed UI, verify that page code stays at use-case orchestration, reusable domain presentation remains feature-owned, generic visuals come from the design system, tokens own reusable constants, shared components contain no accidental domain vocabulary, abstractions have demonstrated responsibility/reuse, and user-visible semantics are unchanged unless the owning requirement changes.
