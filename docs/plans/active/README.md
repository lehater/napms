# Active execution

Current: `PLAN-039-i25-product-completion-acceptance.md`

Current task: WP3 cross-chain explainability navigation.

Goal: complete the bounded operator journey by making existing authoritative provenance references navigable, without adding new semantic data or authority.

## Working set

Read first:
- `docs/plans/active/PLAN-039-i25-product-completion-acceptance.md`
- `web/src/features/rules/AccessRuleDetailsPage.tsx`
- `web/src/features/decisions/ConnectivityDecisionDetailsPage.tsx`

Expand only as needed into App callback wiring and existing Requirement detail routing.

## Current result

WP2B is done and the first WP3 `Realization` workspace is also gate-proven: core, PostgreSQL, Web, harness, knowledge and Docker local-runtime gates all passed on head `e63450cb81ca7dab900e03969e01d29464836a61`. Realization preserves backend `Available | NotAvailable | Unknown` and links contributing Rules to authoritative Rule detail.

Audit found one remaining P1 explainability gap: Rule detail exposes its Decision reference only as text, and Decision detail exposes `ConnectivityRequirement` evidence only as text. The underlying authoritative IDs already exist; only navigation is missing.

## Blockers

No external blocker. Runtime still has no selected configured-evidence/managed-scope-contract source and no durable HTTP-wired NEO history, so those stages remain unavailable until actual owning inputs/results exist.

## Gate

Add navigation only. Do not copy Decision/Requirement state into another view, infer semantics, broaden authority, or add mutation controls.

## Next

Add the two owner-preserving links `Rule -> Decision` and `Decision evidence -> Connectivity Requirement`, wire them through App routing, then rerun the Web/runtime gates.