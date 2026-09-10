# Active execution

Current: `PLAN-I29-resource-authoring-journey.md`
Goal: Validate J02 Resource Catalogue authoring end to end, close only demonstrated P0/P1 gaps, then verify whether the I28 journey pattern genuinely reuses.
Current task: WP-1 — baseline J02 against accepted Resource curation semantics and current supported HTTP/Web surface.
Working mode: `execute-work-package` with `user-journey-validation`.

## Working set

Read first:
- `.agents/skills/user-journey-validation/SKILL.md`
- `docs/requirements/web-ui-requirements.md`
- `web/src/features/catalogues/ResourceDetailsPage.tsx`
- `web/src/features/catalogues/ResourcesPage.tsx`

Expand only if needed:
- `docs/requirements/catalogue-curation.md`
- `docs/decisions/ADR-007-i27-resource-lifecycle.md`
- `src/napms/runtime/catalogue_curation_http.py`
- `src/napms/resource_catalogue/application/curation_read.py`
- `web/src/features/catalogues/catalogueApi.ts`
- `e2e/test_j01_application_authoring.py`

## Recovery facts

- I28/J01 is merged and provides the reusable `user-journey-validation` Skill plus a real full-stack Playwright acceptance pattern.
- J02 fixture: `Orders Database`; address `10.20.30.40` replaced by `10.20.30.41`; scope `orders-prod`; Technical owner Team `Orders Platform`, ref `team:orders-platform`, contact `orders@example.test`.
- Accepted Resource behavior includes create, rename/retire, realization version replacement, scope affiliation create/end and responsibility/contact create/end.
- Static baseline candidate: current Resource Web detail exposes realization/scope/responsibility mutation but does not expose Resource rename/retire.
- Static baseline candidate: current Resource detail read model exposes only effective temporal facts, while accepted UI guidance requires history/current distinction.

## Blockers

None. Browser execution will use hosted GitHub Actions because this connector does not render the local product UI.

## Gate

WP-1 closes with explicit J02 PASS/FAIL based on executable evidence and reproducible P0-P3 findings. Static inspection alone is insufficient.

## Next

Build the smallest J02 browser baseline on the existing full local stack. Use it to prove actual blockers before changing product behavior.
