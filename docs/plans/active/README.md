# Active execution

Current: `PLAN-I29-resource-authoring-journey.md`
Goal: Validate J02 Resource Catalogue authoring end to end, close only demonstrated P0/P1 gaps, then verify whether the I28 journey pattern genuinely reuses.
Current task: WP-2 — validate closure of J02-P1-01 Resource lifecycle maintenance through HTTP/Web, then complete the durable reopen/retirement path.
Working mode: `execute-work-package` with `user-journey-validation`.

## Working set

Read first:
- `e2e/test_j02_resource_authoring.py`
- `web/src/features/catalogues/ResourceDetailsPage.tsx`
- `src/napms/runtime/catalogue_resource_workspace_http.py`
- `tests/runtime/test_catalogue_resource_workspace_http.py`

Expand only if needed:
- `.agents/skills/user-journey-validation/SKILL.md`
- `docs/requirements/catalogue-curation.md`
- `docs/decisions/ADR-007-i27-resource-lifecycle.md`
- `web/src/features/catalogues/resourceWorkspaceApi.ts`
- `src/napms/resource_catalogue/application/curation.py`

## Recovery facts

- I28/J01 is merged and provides the reusable `user-journey-validation` Skill plus a real full-stack Playwright acceptance pattern.
- J02 fixture: `Orders Database`; address `10.20.30.40` replaced by `10.20.30.41`; scope `orders-prod`; Technical owner Team `Orders Platform`, ref `team:orders-platform`, contact `orders@example.test`.
- WP-1 baseline run `34506272832`: J01 passed; J02 successfully created the Resource, realization, scope affiliation and responsibility and replaced the realization, then failed because no `Rename` action existed.
- J02-P1-01: accepted Resource rename/retire lifecycle maintenance was inaccessible through HTTP/Web although core/composition already owned `RenameResource` and `RetireResource`. Owner is outer-adapter implementation; no new domain decision is required.
- WP-2 implementation now exposes Resource rename/retire through the Resource workspace HTTP router and Web detail page with optimistic versioning, confirmation and explicit retirement-blocked feedback.
- Accepted retirement remains non-destructive and blocked while current scope affiliations or responsibilities exist; the user must end those relations explicitly before retrying retirement.
- J02-P2-01 candidate: Resource detail currently presents only effective temporal facts, so a replaced realization becomes invisible even though the UI states that a historical version is created. This does not block the current-authoring journey and is not part of WP-2 unless executable evidence elevates it.
- Shared browser execution is now justified by two real journeys: `make journey-e2e` runs all `e2e/` tests and the workflow covers both Application and Resource Catalogue surfaces.

## Blockers

None. Browser execution uses hosted GitHub Actions because this connector does not render the local product UI.

## Gate

WP-2 closes when J02 can rename, navigate away/reopen by the new name, receive an understandable retirement-blocked result, explicitly end current scope/responsibility relations, and retire successfully through the supported UI. J01 must remain green.

## Next

Run the complete J01+J02 browser regression and applicable core/Web/runtime checks. Fix only reproducible failures, then advance to WP-3/WP-4 absorption and final integration.
