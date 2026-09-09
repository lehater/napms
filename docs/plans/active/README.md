# Active execution

Current: `PLAN-038-i24-local-deployment-hardening.md`

Current task: local PostgreSQL backup and recovery contract.

Goal: harden the supported local Docker Compose deployment without introducing enterprise infrastructure or changing product/domain semantics.

## Working set

Read first:
- `docs/plans/active/PLAN-038-i24-local-deployment-hardening.md`
- `tools/local_postgres_backup.py`
- `tools/local_start.py`
- `compose.yaml`
- `.github/workflows/docker.yml`

Expand only as needed into `docs/engineering/local-docker-runtime.md`, `Makefile`, `.gitignore`, README and canonical engineering state.

## Blockers

None. Restore is intentionally destructive and must require explicit confirmation plus backup validation before replacing the local PostgreSQL volume.

## Gate

A logical backup must restore into a clean local PostgreSQL volume, preserve known durable application state created by the fresh journey, and allow restart-safe authenticated reads afterward. Backup does not claim to capture in-memory sessions, in-memory NEO operations, external device/provider state or local secret values.

## Next

Implement custom-format `pg_dump` backup, validated explicit clean-volume restore and a Docker backup -> replace volume -> restore -> authenticated read round-trip proof.