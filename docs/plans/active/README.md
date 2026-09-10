# Active execution

Current: `PLAN-I27-catalogue-curation.md`

Goal: finish I27 Catalogue Curation as the supported local self-service path for Resource Catalogue and Application Communication Catalogue data consumed by Connectivity and related workflows.

Current task: fix the remaining hosted harness-plan validation failure, rerun the final gate, then absorb I27 if all gates are green.

## Working set

Read first:
- `docs/requirements/catalogue-curation.md`

## Blockers

No known product/domain blocker remains.

First hosted gate diagnostics were fixed on the branch:
- core: one architecture check false-positive from an absolute `application_catalogue` domain import; changed to a relative domain import;
- PostgreSQL: stale parent-table cleanup in two dependent suites and nullable `scope/pattern` SQL inference in the Resource workspace projection; both fixed;
- harness: previous capsule was oversized and malformed; this file now follows `tools/validate_plans.py` grammar and budget.

## Gate

PR #51 is draft while fixes are applied.

Second gate results before this harness-only fix:
- core: green;
- PostgreSQL persistence: green;
- web: green;
- knowledge: green;
- docker local runtime: pending/completing at the time of this capsule update;
- harness: failed only active-plan index validation.

The final retry must run from a new `ready_for_review` transition after this capsule commit. If any material fix is required, return the PR to draft before editing and gate again.

## Next

1. Mark PR #51 ready for review and inspect every hosted workflow on the new head SHA.
2. If all gates are green, absorb durable I27 outcomes into current-state/architecture/UI/roadmap owners and retire this active plan/capsule.
3. Gate any material absorption changes required by repository policy.
4. Squash-merge PR #51 only after final green validation and absorption.
