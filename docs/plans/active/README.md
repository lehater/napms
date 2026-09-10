# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: complete I31 by proving the accepted Application Catalogue target through unchanged downstream semantics and absorbing the resulting current-state documentation.

Current task: WP-5 compatibility acceptance, deterministic screenshot evidence and final absorption.

## Working set

Read first:
- `docs/plans/active/PLAN-I31-application-catalogue-target-migration.md`
- `docs/engineering/application-catalogue-target-migration-roadmap.md`
- `docs/ui/application-catalogue-wireframes.md`
- `e2e/test_j01_application_authoring.py`
- `e2e/test_j03_connectivity_request_decision.py`

Expand only when required into downstream Connectivity / Decision / Access Policy Web flows, browser-gate infrastructure and current-state/canonical documentation touched by I31.

## Blockers

None known. M0-M4 are squash-merged. M4 is integrated as `64bd709b5f29db7bd59b09cc4447aa9141e9556f` after all six applicable hosted gates passed.

## Gate

WP-5 exits when target-authored Application data is proven through existing downstream Connectivity / final Decision / Access Policy semantics, representative accepted Application Catalogue layouts have deterministic screenshot regression evidence, and current-state/canonical documentation is absorbed with the active I31 plan removed.

## Next

Extend J01 from target authoring into downstream semantics without duplicating J03, add the smallest deterministic screenshot regression set for representative accepted layouts, run Docker/hosted gates, then absorb documentation and close I31.
