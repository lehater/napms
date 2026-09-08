# Wave-1 G2 — Greenfield Product Baseline

Status: `G2 PASS`.

Date: 2026-09-08.

## Outcome

Wave 1 is sufficiently specified for architecture work without using Legacy implementation as domain meaning.

Selected end-to-end outcome:

```text
compose/request valid application-backed Access Rule Proposal(s)
    -> consume ConnectivityDecision(Allowed | NotAllowed)
    -> materialize/resolve one authoritative Active Rule per Allowed semantic identity
    -> maintain Active <-> Inactive + supported declarative operational properties
    -> select authorized effective desired-policy subset
    -> resolve coherent current technical realization for one export as-of
    -> produce complete explainable vendor-neutral Normalized Policy Export
    -> STOP
```

## Canonical G2 inputs

- functional requirements: `docs/target/wave1-product-requirements.md`;
- behavior trace: `docs/target/wave1-story-use-case-trace.md`;
- normalized export trace: `docs/target/wave1-normalized-export-trace.md`;
- acceptance examples: `docs/target/wave1-acceptance-examples.md`;
- quality scenarios / ASRs: `docs/target/wave1-quality-scenarios.md`;
- semantic contracts: `docs/target/wave1-semantic-contracts.md`;
- deferred behavior: `docs/target/wave1-deferrals.md`;
- accepted D1 decisions/provenance: `docs/requirements-audit/wave1-d1-decision-packets.md`;
- deferred Connectivity Decision research: `docs/requirements-audit/connectivity-decision-domain-deferred.md`;
- Strategic DDD authority: `docs/ddd/readiness.md` (`DDD-BDM-010`).

## G2 challenge

| Criterion | Result | Evidence |
|---|---|---|
| every Wave-1 behavior through normalized export accepted/testable | PASS | requirements + traces |
| material rules have examples/counterexamples/degraded cases | PASS | acceptance examples E1-E14 |
| identity/decision/state semantics explicit | PASS | D1 decisions + requirements |
| structural proposal validity explicit | PASS | DCS-described interaction; no invented blanket same-Application invariant |
| missing/stale data behavior explicit | PASS | fail-closed successful export semantics |
| provenance/effective-time semantics explicit | PASS | D1 decisions + QS-03/QS-05 + contracts |
| ASRs concrete enough to compare architecture options | PASS | P1/P2 quality scenarios; unsupported numeric SLA deliberately not invented |
| participating contexts elaborated only as needed | PASS | semantic contracts; no BC=service inference |
| deferred domains have safe seams/revisit triggers | PASS | deferral register + Decision Domain artifact |
| Strategic DDD contradiction discovered | NONE | accepted behavior remains within DDD-BDM-010 ownership seams |
| architecture decision used to fill product gap | NONE | topology/API/storage/technology remain unchosen |
| Legacy mechanisms copied as product truth | NONE | Word/Excel/XUIT/firewall split/render/execution explicitly dispositioned/deferred |

## Architecture-significant drivers handed to G3

Priority order:

1. authoritative semantic correctness and idempotent Rule materialization;
2. coherent temporal export and fail-closed completeness;
3. end-to-end provenance/explainability;
4. action-scoped authority and auditability;
5. semantics-preserving vendor-neutral normalization/interoperability.

Numeric scale/performance/availability targets are not established by current evidence and are not invented at G2. PLAN-027 may revisit them if architecture feasibility or transition workload requires a concrete envelope.

## Boundaries that architecture must preserve

```text
Bounded Context != service != database != deployment unit
```

Architecture must not:
- invent Connectivity Decision internals;
- collapse immutable Rule semantic identity with mutable technical realization;
- make best-effort incomplete output look successful;
- lose Rule/decision provenance through normalization;
- infer permanent target topology from Legacy modules/tables/apps;
- promote deferred rendering/execution semantics into Wave 1.

## G2 decision

`PASS` — PLAN-027 Target and Transition Architecture may start.
