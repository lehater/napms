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


## Project-native NOT_APPLICABLE contracts

NAPMS also has a project-native consumer requirement whose requested capability is
not applicable when an accepted architecture capability proves that fact:

`engineering.interface.async-contract`
is marked not applicable by
`engineering.architecture.async-messaging-not-applicable`.

The transient-profile bridge maps that requirement to the evidence capability
instead of inventing a Harness-specific N/A status.

Observed behavior:

- with the evidence capability present, the derived `IMPLEMENTATION-DESIGN`
  profile is `COMPLETE`;
- when only that evidence capability is removed from the projected model,
  `ASYNCHRONOUS-CONTRACT` becomes `CREATE`;
- no special Core state or target-state extension is required.

Conclusion: project-native applicability policy remains in the target consumer
contract. Harness only asks whether the accepted evidence knowledge it relies on
is present and unblocked.


## Whole-vertical profile projection

All 13 current NAPMS consumer/input contracts can be translated into transient
Design Profiles and evaluate `COMPLETE` against the current projected model.

This shows that the bridge is not specific to `IMPLEMENTATION-CONSUMER`; it
also handles the Authority input contracts across domain, architecture,
interface, data, quality, security, operability, implementation and verification.

An in-memory unresolved Question blocking `RESOURCE-DETAIL-UI` produces the
same root blocker in both systems:

- the NAPMS vertical reports the affected consumer requirement as `BLOCKED`;
- external Harness reports `RESOURCE-DETAIL-UI -> WAIT` and leaves downstream
  implementation/verification expectations `PENDING`.

The difference is presentation/actionability, not semantic disagreement.

## Subject-specific knowledge coverage

NAPMS also demonstrates an important Design Profile boundary.

The broad capability `engineering.domain.tactical-model` is intentionally
provided by several artifacts under the same `TACTICAL-DOMAIN-DESIGN`
Authority. Those artifacts cover different Bounded Context subjects.

A Design Profile expectation with:

- subject `BC-RESOURCE-CATALOGUE`;
- broad capability `engineering.domain.tactical-model`;

is insufficient to prove Resource Catalogue coverage. If the RC provider loses
that broad capability, other tactical providers still satisfy capability
resolution and a naive profile remains `COMPLETE`.

The target-owned `docs/engineering-knowledge-completeness.yaml` policy already
solves this at the project level by matching subject + knowledge coverage.

The current-Harness pilot therefore derives ephemeral scoped capabilities from
that accepted coverage metadata, for example:

`napms.coverage.tactical-domain-model.BC-RESOURCE-CATALOGUE`.

With scoped capabilities:

- current accepted coverage evaluates `COMPLETE`;
- removing only the RC scoped capability yields exactly the RC expectation as
  `CREATE`;
- no Subject entity, provider-selector field or other Core extension is needed.

Conclusion: `subject` is expectation scope/reporting, while `CapabilityId`
is the provider-resolution key. Subject-specific completeness requires a
sufficiently scoped capability or a target-owned coverage adapter/check.
