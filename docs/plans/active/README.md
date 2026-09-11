# Active execution

Current: `PLAN-I33-code-structure-locality-cleanup.md`
Goal: I33 Code Structure Locality Cleanup removes proven residual compatibility/locality debt after completed I32 without changing product, domain, API or persistence semantics.
Current task: S5 completed — legacy HTTP monolith replaced by process-only runtime.

Working branch: `refactor/code-structure-locality`.

## Working set

Read first:
- `docs/plans/active/PLAN-I33-code-structure-locality-cleanup.md`
- `src/napms/runtime/http_api.py`

Expand only:
S5 is closed. Do not expand scope while awaiting coordinator review.

## Blockers

None known.

## Gate

The process runtime is assembled directly without a legacy base app; only process routes are implemented there, feature errors and routes are owner-local, architecture guards protect the boundary, and `make check` passes.

## Next

Coordinator review; select the next evidence-backed slice before further implementation.
