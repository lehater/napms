# Active execution

Current: `PLAN-I28-user-journey-validation-pilot.md`
Goal: Prove a minimal Harness-supported user-journey validation loop on J01 Application Catalogue authoring, close its P0/P1 gaps, then retain only demonstrated reusable support.
Current task: WP-4 — regate the deterministic J01 browser regression after closing the PostgreSQL Applications-list blocker.
Working mode: `execute-work-package` with `user-journey-validation`; automation proves deterministic behavior, not subjective usability quality.

## Working set

Read first:
- `e2e/test_j01_application_authoring.py`
- `.github/workflows/journey-e2e.yml`

Expand only if needed:
- `src/napms/application_catalogue/adapters/postgres/curation_repository.py`
- `tests/integration/postgres/test_application_catalogue_listing_i28.py`
- `web/src/features/catalogues/ApplicationDetailsPage.tsx`
- `web/src/features/catalogues/catalogueApi.ts`
- `compose.yaml`
- `tools/local_start.py`

## Recovery facts

- WP-1 closed: Harness/CI discoverability gate passed in hosted run `34500542639`.
- WP-2 verdict was `FAIL` with J01-P1-01 lifecycle maintenance inaccessible from HTTP/Web and J01-P1-02 persisted DCS traffic semantics absent after reopen.
- WP-3 closed both P1s: Application/Component/Deployment rename+retire are exposed through a dedicated Application workspace adapter/Web UI, and saved DCS revisions expose readable decoded traffic semantics while raw payload remains internal.
- Full WP-3 affected-scope CI is green on head `3e88443df91c5968df02a32666cf9fd6726e74ff`: core `34502524497`, postgres `34502524459`, web `34502524770`, harness `34502524593`, knowledge `34502524561`, docker local runtime `34502524670` all succeeded.
- J01 deterministic fixture remains `Order Management` with `Web UI`, `Orders API`, `Database` production deployments plus tcp/443 and tcp/5432 directed communications.
- WP-4 has a real Playwright regression in `e2e/test_j01_application_authoring.py`, invoked by `make journey-e2e` and hosted by `J01 browser journey gate`.
- Diagnostic browser run `34504491558` proved login, Application/Component/Deployment creation, both DCS mutations, Application rename, retirement confirmation and navigation through the real UI before failing on reopen search.
- That run exposed J01-P1-03: PostgreSQL Application list/search returned 503 because the nullable search predicate used an untyped `%s IS NULL` parameter. The repository predicate now casts that parameter to `text`, with a real PostgreSQL list/search regression in `test_application_catalogue_listing_i28.py`.
- Browser automation is regression evidence only; subjective usability findings remain owned by journey validation.

## Blockers

None known. J01-P1-03 is fixed pending hosted regate.

## Gate

WP-4 closes when `J01 browser journey gate` passes against the composed local product and the run/log confirms `make journey-e2e` succeeded. Harness/core/PostgreSQL/Web/runtime gates on the same head must also remain green.

## Next

Run the Ready-for-review gates on the current head. Fix only reproducible failures; once green, advance to WP-5 pilot review and absorption.
