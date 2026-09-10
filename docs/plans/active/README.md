# Active execution

Current: `PLAN-I28-user-journey-validation-pilot.md`
Goal: Prove a minimal Harness-supported user-journey validation loop on J01 Application Catalogue authoring, close its P0/P1 gaps, then retain only demonstrated reusable support.
Current task: WP-2 — establish the J01 Application Catalogue baseline and classify journey gaps before implementing fixes.
Working mode: `execute-work-package` with `user-journey-validation`; route discovered semantic or implementation gaps only after baseline classification.

## Working set

Read first:
- `docs/requirements/catalogue-curation-acceptance-examples.md`
- `docs/requirements/web-ui-requirements.md`
- `web/AGENTS.md`

Expand only if needed:
- `docs/requirements/catalogue-curation.md`
- `docs/ui/screens.md`
- `docs/ui/interaction-rules.md`
- `web/src/features/catalogues/ApplicationsPage.tsx`
- `web/src/features/catalogues/ApplicationDetailsPage.tsx`
- `web/src/features/catalogues/DcsAuthoringPanel.tsx`
- `web/src/features/catalogues/catalogueApi.ts`
- `src/napms/runtime/catalogue_curation_http.py`

## Recovery facts

- WP-1 is closed: hosted Harness run `34500542639` executed `make harness-check` successfully after CI exposed and corrections closed two active-plan validation defects.
- `user-journey-validation` is the selected workflow for WP-2; J01-specific truth remains in accepted requirements and the active plan.
- J01 fixture is `Order Management` with `Web UI`, `Orders API`, `Database` production deployments and tcp/443 plus tcp/5432 directed communications.
- Journey evidence must come from supported UI behavior. Code/API inspection may identify candidate gaps or diagnose failures but must not be presented as an executed UI PASS.
- Repository CI is an available deterministic execution surface; current connector can inspect runs/jobs/logs but cannot create `workflow_dispatch` runs.

## Blockers

No running browser/UI execution surface is currently connected to this chat. WP-2 may use code inspection to identify reproducible candidate gaps, but J01 cannot be declared PASS without executable UI evidence. If the baseline shows a blocking implementation gap directly from accepted requirements/code, classify it rather than inventing browser evidence.

## Gate

WP-2 closes when J01 has an explicit PASS/FAIL verdict with reproducible P0-P3 findings and every P0/P1 finding has an owning next workflow plus concrete expected accepted result.

## Next

Compare accepted Catalogue Curation/Web UI behavior with the current Applications UI and backend boundary, establish the smallest reproducible J01 baseline findings, and identify the least-complex executable UI evidence path needed before implementation begins.
