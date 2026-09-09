# Wave-1 G2 — Greenfield Product Baseline

Status: `G2 PASS — historical accepted snapshot`.

Date: 2026-09-08.

## Purpose

Record the G2 product-readiness decision that allowed architecture work to begin.

This is historical provenance, not current product truth. Detailed Wave-1 working requirement/trace/example packets were later absorbed and removed from the living requirements surface. Git history preserves their exact content.

## Accepted outcome at G2

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

## Durable current successors

Current accepted behavior is now owned by:
- `docs/requirements/access-policy-core.md`;
- `docs/requirements/policy-export-core.md`;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/requirements/connectivity-decision-core.md`;
- current feature-specific requirements;
- executable implementation/evidence under `src/` and `tests/`.

Connectivity Decision was intentionally deferred at G2; ADR-005 and current Decision requirements supersede that historical deferral.

## G2 challenge result

G2 established that:
- proposal/Rule semantic identity and Allowed/NotAllowed materialization behavior were testable;
- retries/concurrency must not create duplicate authoritative Rules;
- technical realization must not redefine Rule identity;
- successful export must be coherent for one logical time and fail closed on incomplete required facts;
- provenance must survive normalization;
- action authority and business audit are explicit;
- Bounded Context does not imply service/database/deployment unit;
- unsupported numeric SLA/workload values must not be invented;
- rendering, provider execution and configured-state reconciliation were outside the selected slice.

No Legacy mechanism was accepted as target domain truth.

## Decision

`PASS` — the product baseline was sufficiently specified to enter target-architecture work.

For exact historical G2 packet wording, use Git history rather than current requirements.
