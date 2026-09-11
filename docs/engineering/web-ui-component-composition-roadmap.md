# Web UI Component Composition Roadmap

Status: `planned`.

Tracking issue: #90.

## Purpose

Reduce Web UI change coupling by making component ownership and composition explicit.

The migration preserves accepted product semantics and user-visible behavior. Its responsibility is structural: pages become screen/use-case composition roots, reusable visual behavior moves to the narrowest stable owner, and feature semantics remain feature-owned.

## Current problem

The Web UI already has shared controls and a design system, but reuse stops too early. Several feature pages combine five responsibilities:

1. screen/use-case orchestration;
2. query and mutation state;
3. domain-to-visual mapping;
4. reusable layout/form/dialog/detail/list composition;
5. feature-specific presentation.

This produces large pages and repeated local implementations of status visuals, dialogs, detail rows, page sections, search/paging mechanics and mutation/error handling.

File size is evidence, not the decomposition rule. Extraction is justified by responsibility, change coupling and demonstrated reuse.

## Target layering

```text
semantic tokens
  -> design-system primitives
    -> generic design-system components
      -> reusable product/UI patterns
        -> feature components
          -> feature pages
```

### `design-system/primitives`

Responsibility: smallest visual/layout building blocks with stable generic contracts.

Examples: `Surface`.

Inputs: generic visual/content props.

Outputs: semantic-token-based geometry and styling.

Must not know NAPMS domain terms.

### `design-system/components`

Responsibility: reusable generic controls and focused visual components.

Examples: buttons/fields after consolidation, `Checkbox`, `DataTable`, `SearchInput`, `StatusIndicator`, `Tag`, shared page states.

A component belongs here when its contract is useful across unrelated features without domain vocabulary.

### `design-system/layout`

Responsibility: stable application/page geometry.

Examples: `PageWorkspace`, `PageHeader`.

### `design-system/patterns`

Responsibility: reusable compositions of design-system components that encode a product UI interaction/layout pattern but not feature/domain semantics.

Examples/candidates after demonstrated reuse:
- dialog shell with header/body/footer;
- detail workspace sections/rows/actions;
- catalogue/list toolbar + filter/view/pagination composition;
- inline-edit interaction;
- confirmation action presentation where the contract remains generic.

Patterns expose composition slots and focused behavior. They do not become giant universal page/form components.

### `features/<feature>/components`

Responsibility: reusable presentation and domain-to-visual mapping inside one feature boundary.

Examples:
- `NeedStatus`, `DecisionStatus`, `PolicyStatus`;
- `ConnectivityEndpoint`;
- requirement declaration form;
- application/component/deployment cards;
- resource responsibility/scope/history sections.

Feature components may use domain terminology and DTO/view-model types owned by that feature.

### `features/<feature>/pages`

Responsibility: screen-level orchestration.

A page may:
- select/load screen data;
- coordinate feature use cases;
- own route/navigation integration;
- compose design-system patterns and feature components;
- translate screen events into feature API/application actions.

A page should not define a local component library or duplicate shared geometry/control styling.

## Ownership decision rule

For every extraction candidate, classify it in this order:

1. **Domain-specific meaning?** Keep under `features/<owner>/components`.
2. **Generic visual/control behavior used across unrelated features?** Put under `design-system/components`.
3. **Reusable composition of generic components with stable interaction/layout semantics?** Put under `design-system/patterns`.
4. **Pure technical React/helper behavior with no product semantics?** Put under `lib/` only when truly cross-feature.
5. **Used once and unstable?** Keep local until a second concrete consumer or a clearly stable primitive contract appears.

The default is locality. Reuse is earned by stable responsibility, not anticipated by naming.

## Anti-abstraction rules

- Do not create a universal `Page`, `EntityPage`, `Form`, or `CRUD` component with broad mode/variant prop matrices.
- Prefer composition slots/children over inheritance and deeply conditional mega-components.
- Do not move NAPMS vocabulary into the generic design system.
- Do not introduce a generic `shared/model` or shared business-logic package.
- Do not extract hooks that merely hide one page's state. Extract only repeated technical mechanics with equivalent lifecycle/error semantics.
- Do not preserve duplicate namespaces through compatibility facades; migrate callers and remove the obsolete owner in the same coherent stage when practical.

## Candidate inventory

The first audit identified these high-value candidates.

### Generic/design-system candidates

- dialog shell and dialog sections/actions;
- detail row / section heading / panel composition;
- inline editing interaction;
- confirmation/destructive-action presentation;
- unified status visual mechanism;
- shared form error/action layout;
- list/catalogue search/filter/view/pagination composition where current `CataloguePage` abstractions already demonstrate reuse.

### Feature-owned candidates

`catalogues`:
- application identity/header;
- application component card;
- deployment card/editor;
- resource binding editor;
- resource detail overview/history/technical sections.

`connectivity`:
- need status;
- decision status;
- policy status;
- local/remote endpoint presentation;
- connectivity inventory row/table/filter composition.

`requirements`:
- requirement status/alignment presentation;
- requirement list/table;
- declaration form and interaction selector.

`decisions`:
- decision status/presentation;
- decision list/table;
- decision detail sections/actions.

### Technical reuse candidates

Evaluate only after component decomposition exposes genuinely identical mechanics:
- debounced value/search;
- async mutation state;
- paged query coordination.

Do not build a local replacement for a mature server-state library accidentally. If repeated server-state orchestration becomes substantial, make that dependency/architecture choice explicitly rather than growing ad-hoc hooks indefinitely.

## Target source structure

```text
web/src/
  app/
  design-system/
    primitives/
    components/
    layout/
    patterns/
      catalogue/
      detail/          # only if justified by concrete reuse
      dialog/          # only if justified by concrete reuse
  features/<feature>/
    api/
    model/
    components/
    pages/
  lib/
```

`components/ui/` is transitional current state, not a second permanent generic-component ownership model. Its components should be moved into `design-system/components/` when touched by the migration and when the resulting ownership is clear. Do not perform a blind directory move independent of consumer migration.

## Roadmap

### M0 — Canonicalize boundaries

Goal: make repository guidance unambiguous before code movement.

Changes:
- update `docs/architecture/code-structure.md` frontend taxonomy to include `design-system/`;
- extend `docs/ui/design-system.md` with component ownership/extraction rules;
- record this roadmap and tracking issue.

Exit criteria:
- architecture, Web agent guidance and UI design-system guidance agree on ownership.

### M1 — Establish reusable generic composition base

Goal: extract only already-demonstrated generic UI composition.

Candidate work:
- introduce a reusable dialog composition from existing create/edit dialogs;
- establish detail row/section/panel composition where at least two current detail screens match;
- converge duplicated status visual styling onto existing semantic status components;
- decide migration path from `components/ui/` into `design-system/components/`.

Validation:
- `make web-check`;
- affected browser/E2E checks;
- no product-semantic changes.

### M2 — Catalogue decomposition reference slice

Goal: use catalogue screens as the reference implementation for page/component boundaries.

Start with the highest-value pages:
- `ApplicationDetailsPage`;
- `ResourceDetailsPage`;
- `ResourcesPage` / `ApplicationsPage` where shared list/dialog patterns are demonstrated.

Expected result:
- page roots primarily orchestrate data/actions and compose extracted feature components;
- application/component/deployment/resource sections live in feature components;
- generic geometry comes from the design system.

Exit criterion: catalogue pages provide a repeatable example for other features without introducing catalogue-specific behavior into generic patterns.

### M3 — Connectivity decomposition

Goal: split `ConnectivityPage` and `RequestConnectivityPage` by presentation responsibility.

Expected feature components:
- status mappings;
- endpoint presentation;
- inventory filters/table/rows;
- request form sections.

Reuse generic patterns established in M1/M2 before creating new ones.

### M4 — Requirements decomposition

Goal: split list/detail/declaration responsibilities in Connectivity Requirements.

Expected feature components:
- requirement status/alignment;
- list/table/filter composition;
- declaration/interaction selection;
- detail sections/actions.

### M5 — Decisions decomposition

Goal: split Connectivity Decision list/detail pages using the same established boundaries.

Expected feature components:
- decision status;
- list/table/filter composition;
- detail sections/actions.

### M6 — Proven technical-state reuse

Goal: reduce repeated technical React mechanics only after M2-M5 expose equivalence.

Evaluate repeated patterns for:
- debounced search;
- async mutation state;
- paging/filter coordination.

Each extracted helper/hook must have at least two concrete consumers with equivalent semantics and tests where behavior is non-trivial.

### M7 — Enforcement and cleanup

Goal: prevent regression.

Changes:
- remove obsolete duplicated local/shared implementations;
- add architecture/static checks where boundaries can be mechanically enforced;
- add focused component tests for shared interaction contracts;
- retain/extend E2E coverage for user-visible behavior;
- update canonical docs to final state;
- close #90 only after all accepted migration stages are complete.

## PR strategy

Use one coherent migration stage per PR; do not submit a repository-wide mechanical rewrite.

Recommended sequence:
1. M1 generic composition base;
2. M2 catalogue reference decomposition;
3. M3 connectivity;
4. M4 requirements;
5. M5 decisions;
6. M6 technical reuse;
7. M7 enforcement/cleanup.

A stage may be split further when reviewability requires it, but each PR must leave callers on final ownership with no compatibility facade.

## Acceptance criteria

The migration is complete when:

- feature pages are primarily screen/use-case orchestration and composition;
- repeated generic controls/geometry have one design-system owner;
- domain-to-visual mapping is feature-owned;
- repeated feature presentation is under feature `components/`, not page-local helper components;
- `components/ui/` no longer competes with `design-system/components/` as a generic ownership namespace;
- shared hooks/helpers exist only for demonstrated technical reuse;
- no universal prop-driven page/form abstraction has replaced explicit composition;
- Web build and applicable E2E/visual guards pass;
- accepted product/domain behavior is unchanged unless separately approved.

## Execution gate

This roadmap defines order and boundaries, not automatic authorization to perform every stage at once. Select the next milestone as the active increment, implement it end-to-end, verify its value and boundary quality, then continue.
