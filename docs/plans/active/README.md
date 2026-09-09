# Active execution — resume capsule

Current: `PLAN-029-i16a-scoped-connectivity-workspace.md`

Roadmap: `docs/engineering/post-wave1-product-completion-roadmap.md`

Goal: finish I16A as the resource-centric Connectivity workspace and close it only after repository gates and P0/P1 review pass.

Current task: WP-08 — I16A acceptance, validation and reconciliation.

Working mode: implementation validation / architecture review.

Primary workflow: `.agents/skills/execute-work-package/SKILL.md`.

## Working set

Read first:
- `docs/requirements/scoped-connectivity-inventory.md` — accepted inventory and contextual Request access semantics.

Expand only if the current gate requires it:
- `web/AGENTS.md`
- `docs/plans/active/PLAN-029-i16a-scoped-connectivity-workspace.md`
- `docs/engineering/http-api-contract.md`
- `docs/architecture/scoped-connectivity-inventory.md`
- `.github/workflows/ci.yml`
- `.github/workflows/postgres.yml`
- `.github/workflows/web.yml`
- `.github/workflows/knowledge.yml`
- `.github/workflows/harness.yml`

Do not reopen accepted Resource Scope Affiliation / ReadScopedConnectivity semantics unless validation exposes contradictory canonical evidence.

## Recovery facts — non-authoritative

These are compact recovery summaries; canonical owners win if they conflict.

- Resource Catalogue owns time-qualified Resource Scope Affiliation; Authority Management independently owns `ReadScopedConnectivity` admission.
- Scoped Connectivity Inventory is a non-peer read composition and persists no composite business truth.
- Need / Decision / Policy remain independent dimensions; Connectivity Decision has only final `Allowed | NotAllowed`.
- I16A runtime keeps Decision summary safely `Unknown` until I16B supplies the durable Decision provider.
- First executable Request access reuses an existing exact ACC interaction; zero-interaction authoring remains gated by an accepted ACC capability.

## Blockers

No open semantic P0 blocker is accepted at this point.

Validation is still pending for:
- Python/core gate;
- PostgreSQL persistence gate;
- Web build gate;
- knowledge/harness gates;
- final P0/P1 architecture/security/domain review.

## Gate

Do not close PLAN-029, mark I16A PASS, or merge PR #31 until all applicable repository gates pass on the branch synchronized with current `main` and no P0/P1 finding remains open.

## Next

Synchronize the feature branch with current `main`, run the repository gates, fix failures, then perform the final P0/P1 review and update the plan/PR state from evidence.
