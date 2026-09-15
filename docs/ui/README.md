# NAPMS Web UI specification

This directory contains both reconstructable product UI specifications and reusable presentation/interaction guidance for the Web outer adapter.

## Current as-built UI specifications

- `screens.md` — implemented product screen/navigation map and workspace responsibilities.
- `application-catalogue-target.md` — implemented Applications catalogue interaction model.
- `application-catalogue-wireframes.md` — implemented Application Catalogue screen structure.
- `resource-catalogue-wireframes.md` — implemented Resource Catalogue screen structure.
- `checker.md` — implemented Checker UI contract.
- `references/` — visual references used by current UI specifications.

These documents remain project documentation after implementation because they are required to reproduce the current designed UI. Where they describe compatibility vocabulary that differs from newer target domain semantics, they are as-built reconstruction contracts only.

## Reusable current guidance

- `design-tokens.md` — visual tokens and density;
- `layout.md` — shell/workspace layout;
- `components.md` — reusable component responsibilities;
- `component-composition.md` — composition boundaries;
- `design-system.md` — reusable visual system;
- `interaction-rules.md` — generic form/loading/error/navigation mechanics.

Product behavior is owned by `docs/requirements/`; semantic identity/lifecycle/authority is owned by `docs/domain/`. UI specifications must not invent those semantics.

The selected Required Access Matrix MVP requires a practical table and downloadable export; its specific screen structure remains an S3/UI design decision and is not yet specified here.
