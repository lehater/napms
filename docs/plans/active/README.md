# Active execution

Current: `PLAN-038-i24-local-deployment-hardening.md`

Current task: WP6 final verification and absorption.

Goal: verify the complete I24 hardening branch, absorb durable operational outcomes into canonical repository truth, then retire PLAN-038 and promote I25.

## Working set

Read first:
- `docs/plans/active/PLAN-038-i24-local-deployment-hardening.md`
- `.github/workflows/docker.yml`
- `docs/engineering/local-docker-runtime.md`
- `docs/engineering/local-upgrade-procedure.md`
- `docs/engineering/current-state.md`
- `docs/engineering/post-wave1-product-completion-roadmap.md`

Expand only as needed into `docs/architecture/current-architecture.md`, `README.md`, `compose.yaml` and operator tooling touched by I24.

## Blockers

No product/domain blocker remains. Closure depends only on complete-branch verification and canonical absorption. Enterprise TLS, external secret stores, HA, corporate identity and multi-node topology remain outside the selected local deployment target.

## Gate

Core, PostgreSQL persistence, harness, knowledge and Docker local-runtime gates must all pass on the complete I24 head. Docker proof must cover SCRAM/password enforcement, preserved-volume restart with credential rotation, logical backup/clean restore, migration replay no-op and local diagnostic checks.

## Next

Run final gates. If green, perform PR diff review, update canonical current-state/architecture/roadmap with accepted I24 outcomes, retire PLAN-038 and promote I25.