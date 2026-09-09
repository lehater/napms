# Active execution

Current: `PLAN-038-i24-local-deployment-hardening.md`

Current task: local runtime security baseline verification.

Goal: harden the supported local Docker Compose deployment without introducing enterprise infrastructure or changing product/domain semantics.

## Working set

Read first:
- `docs/plans/active/PLAN-038-i24-local-deployment-hardening.md`
- `compose.yaml`
- `tools/prepare_local_postgres.py`
- `tools/verify_local_postgres_auth.py`
- `.github/workflows/docker.yml`

Expand only as needed into `docs/engineering/local-docker-runtime.md`, `.env.example`, `Makefile`, `README.md` and canonical current engineering/architecture state.

## Blockers

None for WP1 verification. A pre-I24 database volume may legitimately fail the new wrong-password check because PostgreSQL host-authentication rules persist in the volume; needed data must be backed up before recreation/migration.

## Gate

Fresh local Compose must initialize PostgreSQL with SCRAM host authentication. A second startup on the same preserved volume must rotate to a new generated database credential. Both runs must accept the configured password, reject a deliberately wrong password, preserve local UI login/session behavior and keep public ingress loopback-only.

## Next

Run repository gates on the credential-rotation head. If green, mark WP1 done and implement WP2 logical PostgreSQL backup/restore tooling and recovery proof.