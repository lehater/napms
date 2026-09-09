# Active execution

Current: `PLAN-038-i24-local-deployment-hardening.md`

Current task: local upgrade and migration procedure.

Goal: harden the supported local Docker Compose deployment without introducing enterprise infrastructure or changing product/domain semantics.

## Working set

Read first:
- `docs/plans/active/PLAN-038-i24-local-deployment-hardening.md`
- `docs/engineering/local-upgrade-procedure.md`
- `src/napms/composition/postgres_migrations.py`
- `tools/local_postgres_backup.py`
- `.github/workflows/docker.yml`

Expand only as needed into `compose.yaml`, `docs/engineering/local-docker-runtime.md`, Makefile and current engineering state.

## Blockers

None. Downgrade is intentionally not claimed; recovery from a failed forward upgrade uses the pre-upgrade logical backup rather than attempting arbitrary reverse migrations.

## Gate

On a current restored database, replaying `napms-migrate` must succeed without changing the migration-journal count or durable application state. A migration checksum mismatch remains a hard failure.

## Next

Document the local pre-upgrade/forward-migration/recovery sequence and extend the Docker gate with an explicit migration replay no-op proof.