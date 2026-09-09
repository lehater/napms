# Active execution

Current: `PLAN-038-i24-local-deployment-hardening.md`

Current task: WP-1 local runtime security baseline.

Goal: harden the supported local Docker Compose deployment without introducing enterprise infrastructure or changing product/domain semantics.

## Working set

Read first:
- `docs/plans/active/PLAN-038-i24-local-deployment-hardening.md`
- `compose.yaml`
- `.env.example`
- `tools/dev_compose.py`
- `docs/engineering/post-wave1-product-completion-roadmap.md`

Expand only as needed into `README.md`, Dockerfiles, workflow smoke gates and current engineering/architecture state.

## Blockers

None for WP-1. External secret stores, enterprise TLS/HA and corporate identity remain explicitly out of scope.

## Gate

Preserve the current local login/session behavior and loopback-only public ingress. Replace only the avoidable PostgreSQL trust boundary, with deterministic Docker smoke evidence before moving to backup/restore.

## Next

Change Compose/database credential handling so `make dev-up` injects an ephemeral PostgreSQL password and raw Compose requires an explicit non-committed override; update operator documentation and tests/gates accordingly.