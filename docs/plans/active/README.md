# Active execution

Current: `PLAN-I28-user-journey-validation-pilot.md`
Goal: Prove a minimal Harness-supported user-journey validation loop on J01 Application Catalogue authoring, close its P0/P1 gaps, then retain only demonstrated reusable support.
Current task: WP-4 — execute the deterministic J01 browser regression on the full local stack and inspect hosted evidence.
Working mode: `execute-work-package` with `user-journey-validation`; automation proves deterministic behavior, not subjective usability quality.

## Working set

Read first:
- `e2e/test_j01_application_authoring.py`
- `.github/workflows/journey-e2e.yml`

Expand only if needed:
- `web/AGENTS.md`
- `web/src/features/catalogues/ApplicationDetailsPage.tsx`
- `web/src/features/catalogues/DcsAuthoringPanel.tsx`
- `web/src/features/catalogues/catalogueApi.ts`
- `compose.yaml`
- `tools/local_start.py`
- `docs/requirements/web-ui-requirements.md`

## Recovery facts

- WP-1 closed: Harness/CI discoverability gate passed in hosted run `34500542639`.
- WP-2 verdict was `FAIL` with J01-P1-01 lifecycle maintenance inaccessible from HTTP/Web and J01-P1-02 persisted DCS traffic semantics absent after reopen.
- WP-3 closed both P1s: Application/Component/Deployment rename+retire are exposed through a dedicated Application workspace adapter/Web UI, and saved DCS revisions expose readable decoded traffic semantics while raw payload remains internal.
- Full WP-3 affected-scope CI is green on head `3e88443df91c5968df02a32666cf9fd6726e74ff`: core `34502524497`, postgres `34502524459`, web `34502524770`, harness `34502524593`, knowledge `34502524561`, docker local runtime `34502524670` all succeeded.
- J01 deterministic fixture remains `Order Management` with `Web UI`, `Orders API`, `Database` production deployments plus tcp/443 and tcp/5432 directed communications.
- WP-4 now has a real Playwright regression in `e2e/test_j01_application_authoring.py`, invoked by `make journey-e2e` and hosted by `J01 browser journey gate`.
- The browser test creates all J01 business objects through visible UI controls, performs Application rename, dismisses a Component retirement confirmation, navigates away/reopens, and verifies readable persisted traffic semantics.
- Browser automation is regression evidence only; subjective usability findings remain owned by journey validation.

## Blockers

None. GitHub Actions is the executable browser surface because this chat connector cannot render the product UI directly.

## Gate

WP-4 closes when `J01 browser journey gate` passes against the composed local product and the run/log confirms the browser executed `make journey-e2e` successfully. Affected Harness/core/Web/runtime gates must also remain green.

## Next

Inspect the current J01 browser run. Fix only reproducible test/product failures, regate, then advance to WP-5 pilot review and absorption.
