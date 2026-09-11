# Web UI Component Composition Roadmap

Status: `implemented; final hosted gates pending`.

Tracking issue: #90.
Integration PR: #91.
Working branch: `docs/web-ui-component-composition-roadmap`.

## Purpose

Reduce Web UI change coupling by making component ownership and composition explicit while preserving accepted product semantics and user-visible behavior.

The migration makes pages screen/use-case composition roots, moves generic visual behavior to one design-system owner, keeps domain-to-visual mapping feature-owned, and extracts technical React mechanics only after demonstrated equivalent reuse.

## Target layering

```text
semantic tokens
  -> design-system primitives
    -> generic design-system components
      -> reusable product/UI patterns
        -> feature components
          -> feature pages
```

### Ownership

- `design-system/primitives` — smallest semantic-token-based visual/layout building blocks.
- `design-system/components` — generic controls and focused visual components with no NAPMS domain vocabulary.
- `design-system/layout` — stable application/page geometry.
- `design-system/patterns` — reusable generic compositions such as catalogue, dialog and detail interactions.
- `features/<feature>/components` — feature-owned presentation and domain-to-visual mapping.
- `features/<feature>/pages` — route/screen orchestration, loading/mutation coordination and composition.
- `lib/` — cross-feature technical helpers only after equivalent semantics are demonstrated.

`components/ui/` is compatibility-only. It may delegate to `design-system/components` for callers not yet mechanically migrated, but owns no independent generic UI implementation. New code must target the design system directly.

## Decision rules

Classify extraction candidates in this order:

1. Domain-specific meaning -> owning feature `components/`.
2. Generic visual/control behavior across unrelated features -> `design-system/components/`.
3. Reusable composition of generic UI with stable interaction/layout semantics -> `design-system/patterns/`.
4. Pure cross-feature technical React mechanics -> `lib/`, only after demonstrated equivalent lifecycle semantics.
5. Used once and unstable -> keep local.

Do not create universal CRUD/page/form abstractions, generic shared business models, or prop-driven mega-components. Reuse is earned by stable responsibility, not anticipated by naming.

## Executed migration

### M0 — Canonicalize boundaries — complete

- frontend architecture now explicitly recognizes `design-system/`;
- `docs/ui/component-composition.md` owns durable extraction/ownership rules;
- `web/AGENTS.md` routes future UI work through those rules;
- issue #90 and PR #91 track execution.

### M1 — Reusable generic composition base — complete

Added/established:

- design-system `Button`, `Field/Input/Select/Textarea` ownership;
- semantic `StatusBadge` with design tokens;
- reusable `Dialog` composition;
- reusable `DetailSection`, `DetailRow`, `DetailStack` composition;
- reusable `InlineTextEdit` pattern;
- compatibility-only legacy `components/ui` adapters delegating to design-system implementations.

The generic design system remains feature-semantic-free.

### M2 — Catalogue reference decomposition — complete

- `ApplicationsPage` and `ResourcesPage` compose reusable create dialogs and feature-owned status/data-state components;
- `ApplicationDetailsPage` delegates component/deployment/resource-binding presentation to `ApplicationComponentSection` and uses generic inline editing;
- `ResourceDetailsPage` uses generic detail composition and feature-owned resource overview/history/technical sections;
- catalogue-owned ACC interaction labels/selection are centralized under `features/catalogues/components` for semantic reuse by other features.

### M3 — Connectivity decomposition — complete

- Need/Decision/Policy mappings moved to feature-owned status components;
- endpoint/remote-side presentation moved to connectivity components;
- inventory row/detail/action presentation moved out of `ConnectivityPage`;
- request context and request form moved out of `RequestConnectivityPage`.

Pages retain screen/API orchestration.

### M4 — Requirements decomposition — complete

- requirement status/alignment mapping is feature-owned;
- requirement list/table presentation is extracted;
- declaration interaction/applicability presentation is extracted;
- requirement detail interaction/provenance/history sections use the generic detail pattern;
- shared ACC semantics reuse the catalogue owner rather than a generic shared model.

### M5 — Decisions decomposition — complete

- decision status, list/table and evidence presentation are feature-owned;
- decision list interaction selection reuses catalogue-owned ACC selection;
- decision detail subject/reason/evidence/provenance/supersession sections use generic detail composition;
- replacement Decision form reuses feature-owned evidence fields while the page retains mutation orchestration.

### M6 — Proven technical-state reuse — complete

`useDebouncedValue` was extracted only after equivalent debounce behavior was demonstrated in multiple catalogue screens. It has concrete consumers in Applications and Resources.

Async query/mutation/paging state was deliberately not generalized: current screens have materially different refresh, authority, error and mutation semantics. A local React Query replacement was not introduced.

### M7 — Enforcement and cleanup — implemented; final gates pending

- design-system semantic unknown-state tokens added;
- `web/scripts/check-ui-boundaries.mjs` enforces that the design system cannot depend on feature semantics or legacy UI ownership, and that compatibility UI files only delegate inward;
- Web `build`/`check` include the boundary check;
- `web.yml` and `harness.yml` now support the repository's documented `Ready for review` final-gate workflow without running hosted checks on ordinary draft-branch pushes;
- canonical guidance has been updated to the final ownership model.

## Final integration procedure

This migration intentionally executes as one long-lived branch and one draft PR, per the selected execution strategy:

1. accumulate M0-M7 commits on `docs/web-ui-component-composition-roadmap`;
2. keep PR #91 draft while work changes;
3. once implementation/docs are complete, mark PR #91 ready for review;
4. inspect the hosted Web and Harness gate results and logs;
5. if a material fix is needed, return the PR to draft, commit the fix on the same branch, and request the final gate again;
6. after all applicable final gates pass, squash merge PR #91 into `main`;
7. close #90 and leave this document as migration provenance; durable rules remain in architecture/UI guidance.

No intermediate merge to `main` is part of this roadmap.

## Acceptance criteria

The migration is complete for integration when:

- feature pages primarily own screen/use-case orchestration and composition;
- repeated generic controls/geometry have one design-system implementation owner;
- domain-to-visual mapping is feature-owned;
- repeated feature presentation resides under feature `components/`, not page-local mini-libraries;
- `components/ui/` does not compete with `design-system/components/` and contains only compatibility delegation;
- cross-feature semantic reuse imports from its explicit feature owner;
- technical hooks exist only for demonstrated equivalent reuse;
- no universal prop-driven page/form abstraction was introduced;
- UI ownership boundary checks are part of the Web build;
- final hosted Web/Harness gates pass before squash merge.

## Remaining integration gate

Implementation is complete on the working branch. The only remaining roadmap action before integration is the final `Ready for review` hosted gate, followed by one squash merge if the checks pass.
