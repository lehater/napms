# Active execution

Current: `PLAN-I33-code-structure-locality-cleanup.md`
Goal: I33 Code Structure Locality Cleanup removes proven residual compatibility/locality debt after completed I32 without changing product, domain, API or persistence semantics.
Current task: S1 — removal of obsolete runtime bootstrap facades.

Working branch: `refactor/code-structure-locality`.

## Working set

Read first:
- `docs/plans/active/PLAN-I33-code-structure-locality-cleanup.md`
- `src/napms/bootstrap/local_seed.py`
- `tests/architecture/test_bootstrap_structure.py`

Expand only to the three owner-local bootstrap tests and failures directly caused by S1. Do not touch other `runtime` HTTP/auth/support files, `composition/`, domain/application behavior or other structural cleanup.

## Blockers

None known.

## Gate

The five obsolete facade files must be absent, remaining consumers must use `napms.bootstrap`, owner-local tests must live under `tests/bootstrap/`, the architecture guard must prevent facade return, and `make check` must pass.

## Next

Execute S1, validate, push, then coordinator review.
