# Active execution

Current: `PLAN-130-revalidate-policy-lifecycle.md`

Goal: realize the concrete Component Deployment, unified Policy Rule lifecycle and vendor-neutral export without embedding customer-specific approval workflow into the MVP domain.

Current task: complete G3 review of the simplified target architecture for AP formal decisions, AD/BC ownership, policy export and as-built compatibility.

Lifecycle stage: `S3`
Stage state: `IN_PROGRESS`
Lifecycle basis: G1 and G2 were revalidated on 2026-09-16 after simplifying RuleChange governance to one formal `Pending -> Accepted | Rejected` decision; `docs/domain/mvp-ddd-convergence-checkpoint.md` records G2 PASS for that baseline.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Working set

Read first:
- `docs/architecture/first-mvp-policy-lifecycle-export.md`

Expand only when a concrete review lens requires it, starting with the active plan, accepted G2 checkpoint, target policy boundary or code-structure reference relevant to that question.

## Blockers

None currently. S3 must preserve the simplified decision boundary: no source/destination approval model, no ApprovalBasis persistence, and no mandatory RC Responsibility Scope dependency for baseline `DecideRuleChange`.

## Gate

G3 — feasible owner-preserving architecture with explicit ports/persistence/concurrency/failure/compatibility semantics and no P0/P1 contradiction, while keeping customer-specific approval procedures outside the first-MVP core.

## Next

Run the architecture-review lenses against the simplified S3 candidate and synchronize remaining architecture/as-built target references before evaluating G3. Production-code implementation remains forbidden.
