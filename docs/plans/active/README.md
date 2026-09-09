# Active execution

Current: `PLAN-034-i20-realization-reconciliation.md`
Goal: Complete I20 desired-vs-configured reconciliation and enforcement-policy derivation without pulling I21 rendering or I22 execution forward.
Current task: WP-1 — implement the framework-free APR desired-enforcement/reconciliation core.

Working mode: implementation slice; primary Skill `implement-slice`.

## Working set

Read first:
- `docs/domain/access-policy-realization/reconciliation-tactical-model.md`
- `docs/architecture/access-policy-realization-reconciliation-boundary.md`

Expand only if needed:
- `docs/requirements/access-policy-realization-reconciliation.md`
- `docs/requirements/access-policy-realization-reconciliation-acceptance-examples.md`
- `src/napms/access_policy_realization/domain/`
- `src/napms/access_policy_realization/application/`
- `tests/access_policy_realization/`

Recovery facts:
- WP-0 is accepted; I20 stays inside Access Policy Realization.
- Complete configured comparison requires one explicit same-governance-scope + Logical Firewall + Enforcement Attachment managed-scope/source contract.
- First complete configured slice requires an explicitly selected TAE Configured set with `EvidenceTime.Instant == asOf` and exact effective-Permit semantics/completeness.
- TAE itself does not gain global current/complete state; raw Block/order/default/vendor evaluation remains source-adapter work and fails closed when unsupported.
- Shared I18 domain resolution must be reused for desired quality/configured attribution.
- Exact `common | missing | extra` drives `No-op | Add | Remove | Replace`; Replace is not a device command.

## Blockers

None for WP-1 under the accepted first-slice contracts.

## Gate

WP-1 passes when framework-free APR Domain/Application implement exact desired/configured policy semantics with deterministic Unknown/Ambiguous precedence, no peer/infrastructure imports and unchanged I18 behavior.

## Next

Implement I20 core + architecture tests, then advance to WP-2 owner-preserving adapters only after the core gate is coherent.
