# Active execution

Current: `PLAN-130-revalidate-policy-lifecycle.md`

Goal: realize the G1/G2-accepted concrete Component Deployment, unified Policy Rule lifecycle and vendor-neutral export through an owner-preserving target architecture compatible with the current runtime.

Current task: define the selected first-MVP S3 architecture for AP lifecycle, AD ownership, policy export and as-built compatibility.

Lifecycle stage: `S3`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs/domain/mvp-ddd-convergence-checkpoint.md` records G2 PASS on 2026-09-16 for the revalidated target baseline.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Working set

Read first:
- `docs/plans/active/PLAN-130-revalidate-policy-lifecycle.md`
- `docs/architecture/README.md`
- `docs/architecture/code-structure.md`
- `docs/architecture/current-architecture.md`
- `docs/domain/mvp-ddd-convergence-checkpoint.md`

## Blockers

None currently. S3 must make compatibility explicit because the implemented ACC compatibility `ComponentDeployment` has different ownership/identity semantics from target AD `ComponentDeployment`.

## Gate

G3 — feasible owner-preserving architecture with explicit ports, persistence ownership, consistency/failure semantics, compatibility/changeover path and no P0/P1 architecture contradiction.

## Next

Accept the target first-MVP architecture, challenge it with the architecture-review lenses, then enter S4 only after G3 PASS. Production-code implementation remains forbidden.
