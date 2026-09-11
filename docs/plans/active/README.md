# Active execution

Current: `PLAN-I33-code-structure-locality-cleanup.md`
Goal: I33 Code Structure Locality Cleanup removes proven residual compatibility/locality debt after completed I32 without changing product, domain, API or persistence semantics.
Current task: S6 completed — Catalogue-specific HTTP support is owner-local.

Working branch: `refactor/code-structure-locality`.

## Working set

Read first:
- `docs/plans/active/PLAN-I33-code-structure-locality-cleanup.md`
- `src/napms/runtime/http_support.py`

Expand only:
S6 is closed. Do not expand scope while awaiting coordinator review.

## Blockers

None known.

## Gate

Runtime HTTP support contains only genuinely shared process/transport helpers; Catalogue-specific validation and mutation mapping are owner-local, the architecture guard protects the boundary, targeted tests pass, and `make check` passes.

## Next

Coordinator review; select the next evidence-backed slice before further implementation.
