# Active execution

Current: `PLAN-039-i25-product-completion-acceptance.md`

Current task: WP2A full-chain acceptance proof.

Goal: close the P0 product-completion evidence gap with one real Requirement -> Decision -> Rule -> realization -> rendering -> controlled execution -> Verified PostgreSQL integration scenario before adding downstream UI.

## Working set

Read first:
- `docs/plans/active/PLAN-039-i25-product-completion-acceptance.md`
- `docs/engineering/product-completion-gap-matrix.md`
- `tests/integration/postgres/test_network_environment_operations_stub_flow.py`

Expand only as needed into real Connectivity Requirement/Decision integration tests, greenfield composition, APR reconciliation fixtures and owning application APIs.

## Blockers

None. The deterministic NEO target stub is accepted for controlled-execution semantics; real Cisco/device access and enterprise integrations are not required.

## Gate

The acceptance proof must use real Connectivity Requirement and Connectivity Decision persistence at the upstream handoff, not the historical `AllowedDecision` stub. It may reuse deterministic catalogue/resource/topology/evidence fixture preparation, but lifecycle facts with existing owning APIs must be created through those APIs.

## Next

Inspect the existing PostgreSQL-backed Requirement/Decision composition and build the smallest owner-preserving full-chain acceptance test through APR reconciliation/rendering and NEO `Verified`.