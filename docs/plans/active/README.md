# Active execution

Current: `PLAN-034-i20-realization-reconciliation.md`
Goal: Close I20 desired-vs-configured reconciliation and promote I21 without pulling rendering or device execution into APR.
Current task: WP-4 — final review and hosted repository gates.

Working mode: architecture review / closure; primary Skill `architecture-review`.

## Working set

Read first:
- `docs/plans/active/PLAN-034-i20-realization-reconciliation.md`
- `docs/architecture/access-policy-realization-reconciliation-boundary.md`

Expand only if needed:
- `src/napms/access_policy_realization/`
- `src/napms/composition/access_policy_realization_postgres.py`
- `tests/access_policy_realization/`
- `tests/integration/postgres/test_access_policy_realization_reconciliation.py`
- `docs/domain/access-policy-realization/reconciliation-tactical-model.md`

Recovery facts:
- WP-0..WP-3 are implemented in PR #44.
- I20 remains inside Access Policy Realization; no APR persistence was added.
- Enforcement Target is Logical Firewall + Enforcement Attachment.
- Configured comparison requires explicit EvidenceSet + same-managed-scope effective-Permit completeness contract at exact `asOf`.
- Shared I18 resolution is reused for both desired quality and configured attribution.
- P1 findings found during implementation review were closed fail-closed before WP-4.
- Local checkout/test execution is unavailable in this environment because GitHub DNS resolution fails; hosted Ready-for-review gates are the required executable proof.

## Blockers

Hosted core/knowledge/harness gates have not run yet because PR #44 is still draft.

## Gate

WP-4 passes only when all applicable hosted checks are green, no P0/P1 review finding remains, canonical current state marks I20 complete and I21 next, and the active plan is cleared.

## Next

Mark PR #44 ready, inspect every hosted check, fix failures, then perform canonical absorption and squash merge.
