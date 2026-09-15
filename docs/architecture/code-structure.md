# Code structure

Status: `current structural guardrails`.

## Backend taxonomy

Target semantic modules live under `backend/src/napms/contexts/<context>/` and follow inward dependency direction:

```text
domain <- application/ports <- adapters/presentation/composition
```

Cross-context workflows live under `backend/src/napms/workflows/` only when orchestration is genuinely cross-context. Platform/runtime wiring lives under `backend/src/napms/platform/`.

A workflow may consume public application ports/contracts of semantic owners. It must not import peer private domain models, query peer-owned tables directly or acquire independent ownership of orchestrated facts.

## Web taxonomy

The Web application keeps shell/routing under `web/src/app`, feature-local behavior under `web/src/features`, reusable composition under `web/src/components`, reusable visual primitives/tokens under `web/src/design-system`, and technical helpers under `web/src/lib`.

Feature code may depend on the design system and generic components. The design system must not depend on product features.

## Selected MVP

Physical placement for the Required Access Matrix workflow, its API contract, consistency mechanism and UI/export adapter is not accepted yet. S3 Architecture must choose those details without widening the product scope beyond ACC + AD + RC -> Required Access Matrix -> table/export.

## Structural invariants

- Domain code has no framework, database, transport or DI-container dependency.
- Consuming application modules own the ports they require.
- Cross-context references are semantic identifiers, not database foreign keys into peer-owned storage.
- No workflow or adapter reads peer-private persistence directly.
- Provider-specific code stays outside source-neutral domain models.
- Rebuildable projections may improve locality but do not become semantic owners.
- Mechanical dependency rules should be executable in architecture tests/CI where practical.
