# Active execution

Current: `PLAN-I28-user-journey-validation-pilot.md`
Goal: Prove a minimal Harness-supported user-journey validation loop on J01 Application Catalogue authoring, close its P0/P1 gaps, then retain only demonstrated reusable support.
Current task: WP-4 — add deterministic browser regression for the stabilized J01 path and obtain executable UI evidence on the full local stack.
Working mode: `execute-work-package` with `user-journey-validation`; automation proves deterministic behavior, not subjective usability quality.

## Working set

Read first:
- `web/AGENTS.md`
- `web/src/features/catalogues/ApplicationDetailsPage.tsx`

Expand only if needed:
- `web/src/features/auth/LoginPage.tsx`
- `web/src/App.tsx`
- `compose.yaml`
- `tools/dev_compose.py`
- `.github/workflows/docker.yml`
- `docs/requirements/web-ui-requirements.md`

## Recovery facts

- WP-1 closed: Harness/CI discoverability gate passed in hosted run `34500542639`.
- WP-2 verdict was `FAIL` with J01-P1-01 lifecycle maintenance inaccessible from HTTP/Web and J01-P1-02 persisted DCS traffic semantics absent after reopen.
- WP-3 closed both P1s: Application/Component/Deployment rename+retire are exposed through a dedicated Application workspace adapter/Web UI, and saved DCS revisions expose readable decoded traffic semantics while raw payload remains internal.
- Full WP-3 affected-scope CI is green on head `3e88443df91c5968df02a32666cf9fd6726e74ff`: core `34502524497`, postgres `34502524459`, web `34502524770`, harness `34502524593`, knowledge `34502524561`, docker local runtime `34502524670` all succeeded.
- J01 deterministic fixture remains `Order Management` with `Web UI`, `Orders API`, `Database` production deployments plus tcp/443 and tcp/5432 directed communications.
- No browser surface is connected directly to this chat, so WP-4 should use hosted CI to run an actual browser against the composed local product rather than infer UI execution from source/build tests.
- Browser automation must create the J01 business objects through the UI; direct API/database mutation is not valid journey evidence.

## Blockers

None. GitHub Actions can provide the required browser execution surface even though this connector cannot itself open the rendered UI.

## Gate

WP-4 closes when an actual browser executes the deterministic J01 happy path plus one high-value correction/reopen check against the full local stack, the test passes in hosted CI, and the automation does not claim to measure subjective usability.

## Next

Add the smallest Playwright-based J01 browser test and hosted workflow, start the compose stack with ephemeral known test credentials, execute the journey through visible UI controls, then inspect the run/log before advancing to pilot review.
