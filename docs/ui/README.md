# NAPMS Web UI guidance

This directory contains reusable current presentation/interaction guidance for the Web outer adapter.

Current reusable guidance:
- `design-tokens.md` — visual tokens and density;
- `layout.md` — shell/workspace layout;
- `components.md` — reusable component responsibilities;
- `component-composition.md` — composition boundaries;
- `design-system.md` — reusable visual system;
- `interaction-rules.md` — generic form/loading/error/navigation mechanics.

Product behavior is owned by `docs/requirements/`. The selected MVP requires a practical tabular Required Access Matrix and downloadable export; screen structure is an S3/UI design decision and is not pre-specified here.

UI guidance must not introduce domain lifecycle, authority or identity semantics that are absent from the owning requirement/domain contracts.
