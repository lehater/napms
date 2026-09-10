# Active execution

Current: `PLAN-039-i25-product-completion-acceptance.md`

Current task: WP3 explainability and network-operator Web journey.

Goal: expose the proven owner-preserving realization projection through one bounded Web workspace without inventing configured or executed state.

## Working set

Read first:
- `docs/plans/active/PLAN-039-i25-product-completion-acceptance.md`
- `web/src/features/realization/NetworkOperatorRealizationPage.tsx`
- `src/napms/runtime/network_operator_view_http.py`

Expand only as needed into App routing/navigation, existing Rule detail navigation and Web/runtime gate diagnostics.

## Current result

WP2B is done: framework-free operator view, dedicated Authority action, PostgreSQL composition and authenticated HTTP surface passed core, PostgreSQL, harness, knowledge and Docker gates. WP3 now adds one read-only `Realization` workspace that renders backend availability unchanged and links contributing Rule references back to authoritative Rule detail.

## Blockers

No external blocker. Runtime still has no selected configured-evidence/managed-scope-contract source and no durable HTTP-wired NEO history, so the Web must show those stages as unavailable until actual inputs/results exist.

## Gate

Web is presentation only: no reconciliation calculation, execution inference, generic IAM roles or mutation controls. Preserve `Available | NotAvailable | Unknown` exactly from HTTP.

## Next

Run the repository gates on the Web-wired head. If green, inspect the remaining Requirement -> Decision -> Rule explainability links and add only the smallest missing navigation.