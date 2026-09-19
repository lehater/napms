# Current Harness pilot findings — NAPMS

Status: non-canonical pilot evidence.

## Projection compatibility

The current external Harness adapter can consume the existing NAPMS
`docs/harness-core.yaml` directly as a `harness-canonical-graph-projection`.

NAPMS continues to own:

- canonical artifact routing in `docs/canonical-graph.yaml`;
- engineering Authority/capability/consumer contracts in `docs/harness-core.yaml`;
- all product/domain/architecture/interface semantics in their existing canonical paths.

No persistent second Harness Core graph is required.

## Implementation consumer target state

The pilot derives a transient Design Profile from the existing
`IMPLEMENTATION-CONSUMER` contract.

With the current accepted repository state the external Harness evaluates that
profile as `COMPLETE`.

When only `engineering.interface.resource-detail-ui` is removed from the
projected model, Harness exposes:

- `RESOURCE-DETAIL-UI -> CREATE`;
- downstream implementation/verification expectations -> `PENDING`;
- no unrelated `WAIT` or new semantic Question.

This confirms that existing NAPMS consumer contracts can drive the current
Harness target-state mechanism without duplicating expectation policy.

## Resource-detail implementation feedback

Canonical NAPMS knowledge already decides the target behavior:

- `docs/contracts/http/napms.openapi.yaml` defines
  `GET /api/resources/{resourceId}` returning one `ResourceDetail` with
  separate `current` and `history`;
- `docs/contracts/ui/resource-detail.yaml` consumes that same contract;
- `docs/plans/first-mvp-test-intent.yaml` requires scenario `MVP-RC-014`
  to prove ended/replaced Resource facts remain inspectable through the
  supported browser workflow.

Current product implementation still uses separate legacy reads:

- `/api/v1/catalogues/resources/{resourceReference}`;
- `/api/v1/catalogues/resource-history/{resourceReference}`.

Current executable evidence includes backend history-query coverage and a visual
E2E check that the History tab exists, but does not prove the full
`MVP-RC-014` replace/end -> browser-history scenario.

Classification: **implementation / verification evidence gap**, not a missing
engineering decision.

Therefore the correct current-Harness behavior is to remain `COMPLETE`.
No Core Question, new Design Profile expectation, schema or artifact skill is
justified. Product/test changes remain subject to the repository's separate
implementation-authorization rule.
