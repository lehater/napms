# Architecture map

This directory contains current target architecture only.

Start with the smallest relevant artifact:

- `current-architecture.md` — cross-cutting target structure, dependency/ownership rules, runtime boundary and architecture drivers.
- `connectivity-requirements-boundary.md` — Connectivity Requirements boundary.
- `requirement-policy-alignment.md` — Requirement-to-Policy Alignment composition.
- `connectivity-decision-boundary.md` — Connectivity Decision boundary.
- `scoped-connectivity-inventory.md` — Scoped Connectivity Inventory composition.

Consequential choices are recorded in `docs/decisions/`. Product behavior belongs in `docs/requirements/`; architecture should reference those contracts rather than restate them.

Historical Wave-1 G3 design packets are not current architecture. Their accepted decisions were absorbed into `current-architecture.md`, ADRs and feature boundaries; provenance remains in `docs/baseline/` and Git history.
