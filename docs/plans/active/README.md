# Active execution

Current: `PLAN-I33-code-structure-locality-cleanup.md`
Goal: I33 Code Structure Locality Cleanup removes proven residual compatibility/locality debt after completed I32 without changing product, domain, API or persistence semantics.
Current task: S3 — localization of Policy Export JSON serialization.

Working branch: `refactor/code-structure-locality`.

## Working set

Read first:
- `docs/plans/active/PLAN-I33-code-structure-locality-cleanup.md`
- `src/napms/policy_export/adapters/http_json.py`
- `tests/policy_export/test_http_json.py`
- `tests/architecture/test_dependency_rules.py`

Expand only to the named production consumers and failures directly caused by S3. Replace import paths only: do not change the JSON contract, application/domain types or consuming adapter behavior, and do not create shared infrastructure.

## Blockers

None known.

## Gate

The serializer and its test must be owner-local, all consumers must use `napms.policy_export.adapters.http_json`, the runtime source and old references must be absent, the architecture guard must protect this state, and `make check` must pass.

## Next

Execute S3, validate, push, then coordinator review.
