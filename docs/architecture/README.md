# Architecture map

This directory contains current target architecture only.

Start with the smallest relevant artifact:

- `current-architecture.md` — cross-cutting target structure, dependency/ownership rules, runtime boundary and architecture drivers.
- `application-catalogue-target-boundary.md` — I31 target ACC compatibility projection, cross-context dependency ports and external-correlation boundary.
- `connectivity-requirements-boundary.md` — Connectivity Requirements boundary.
- `requirement-policy-alignment.md` — Requirement-to-Policy Alignment composition.
- `connectivity-decision-boundary.md` — Connectivity Decision boundary.
- `scoped-connectivity-inventory.md` — Scoped Connectivity Inventory composition.
- `technical-access-evidence-boundary.md` — Technical Access Evidence boundary.
- `access-policy-realization-resolution-boundary.md` — I18 Technical-to-Domain Access Resolution boundary.
- `network-enforcement-placement-boundary.md` — I19 Network Enforcement Placement boundary.
- `access-policy-realization-reconciliation-boundary.md` — I20 desired enforcement derivation/reconciliation boundary.
- `enterprise-identity-authoritative-sources-boundary.md` — I23 local-first runtime with dormant external identity/source extension seams.

Consequential choices are recorded in `docs/decisions/`. Product behavior belongs in `docs/requirements/`; architecture should reference those contracts rather than restate them.

Historical Wave-1 G3 design packets are not current architecture. Their accepted decisions were absorbed into `current-architecture.md`, ADRs and feature boundaries; provenance remains in `docs/baseline/` and Git history.
