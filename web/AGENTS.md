# Web source scope

Apply root `AGENTS.md` first.

## Responsibility

`web/` is the React outer adapter for accepted NAPMS application use cases. It presents backend-owned business truth; it does not create alternate domain, authority or lifecycle semantics.

## Working set

For one Web task:
1. recover the active plan and selected Skill;
2. read only the relevant accepted requirement plus the matching `docs/ui/` guidance;
3. inspect the feature-local page/components and only the API boundary used by that feature;
4. avoid repo-wide UI/API scans unless the task is explicitly cross-cutting.

## Structure

- group code by feature/use case;
- keep reusable visual primitives under `src/components/ui/`;
- keep transport DTO/request mapping at the frontend API boundary;
- extract shared components/helpers after demonstrated reuse;
- backend Authority Management remains authoritative for visibility/action admission;
- never invent placeholder business state to complete a screen.

## Validation

Run `npm run build` (or `make web-check` from the repository root) for Web changes.
