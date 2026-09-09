# Active execution

Current: `PLAN-038-i24-local-deployment-hardening.md`

Current task: WP-1 local runtime security baseline verification.

Goal: harden the supported local Docker Compose deployment without introducing enterprise infrastructure or changing product/domain semantics.

## Working set

Read first:
- `docs/plans/active/PLAN-038-i24-local-deployment-hardening.md`
- `compose.yaml`
- `tools/verify_local_postgres_auth.py`
- `.github/workflows/docker.yml`
- `docs/engineering/local-docker-runtime.md`

Expand only as needed into `.env.example`, `Makefile`, `README.md` and canonical current engineering/architecture state.

## Blockers

None for WP-1 verification. A pre-I24 database volume may legitimately fail the new check because PostgreSQL initialization settings persist in the volume; needed data must be backed up before recreation/migration.

## Gate

Fresh local Compose must initialize PostgreSQL with SCRAM host authentication, accept the generated/configured password, reject a deliberately wrong password, preserve local UI login/session behavior and keep public ingress loopback-only.

## Next

Run repository gates for WP1. If green, mark WP1 done and implement WP2 logical PostgreSQL backup/restore tooling and recovery proof.