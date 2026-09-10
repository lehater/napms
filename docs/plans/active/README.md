# Active execution

Current: `PLAN-I28-user-journey-validation-pilot.md`
Goal: Prove a minimal Harness-supported user-journey validation loop on J01 Application Catalogue authoring, close its P0/P1 gaps, then retain only demonstrated reusable support.
Current task: WP-3 — close the two J01 P1 gaps proven by the baseline: lifecycle maintenance and durable DCS semantics inspection.
Working mode: `execute-work-package`; implement accepted behavior through the scoped runtime/Web adapters and keep domain identity/lifecycle unchanged.

## Working set

Read first:
- `web/AGENTS.md`
- `web/src/features/catalogues/catalogueApi.ts`

Expand only if needed:
- `docs/requirements/web-ui-requirements.md`
- `src/napms/application_catalogue/application/curation_detail.py`
- `src/napms/runtime/catalogue_curation_http.py`
- `src/napms/runtime/composition.py`
- `web/src/features/catalogues/ApplicationDetailsPage.tsx`
- `tests/runtime/test_catalogue_curation_http.py`

## Recovery facts

- WP-1 is closed: hosted Harness run `34500542639` executed `make harness-check` successfully.
- WP-2 verdict: `FAIL` with two P1 findings proven from accepted contracts plus implementation inspection; no subjective browser PASS is claimed.
- J01-P1-01: Application/Component/Deployment rename+retire are accepted and already implemented/wired in the application layer, but are not exposed by the current HTTP/Web Applications workspace. Expected result: stable-identity rename, optimistic concurrency, leaf-to-parent retirement, confirmation and explicit conflict/block feedback.
- J01-P1-02: Applications detail drops persisted DCS traffic semantics and after reload shows only revision label/direction. Expected result: readable source/destination plus protocol/ports/service alternatives after reopen; correction remains creation of another immutable DCS revision.
- `docs/requirements/web-ui-requirements.md` has been synchronized with the already accepted ACC lifecycle/DCS semantics before implementation.
- Prefer a small Application-workspace HTTP adapter parallel to the existing Resource-workspace adapter rather than expanding generic curation transport responsibilities.
- No running browser/UI execution surface is connected to this chat; deterministic tests/builds can prove implementation behavior but final judgement-based journey closure still requires executable UI evidence.

## Blockers

None for implementing the two proven P1 gaps.

## Gate

WP-3 closes when both J01 P1 findings are implemented through supported HTTP/Web paths, relevant core/runtime and Web checks pass, and no new P0/P1 is introduced by the changes. J01 remains pending final executable UI evidence before overall pilot closure.

## Next

Add the Application workspace runtime adapter for lifecycle mutations and DCS traffic presentation, wire it in composition, update the Applications Web client/detail UI, add focused deterministic tests, then run the affected hosted gates.
