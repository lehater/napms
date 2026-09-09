# Deferred research — Connectivity Decision Domain

Status: `superseded by I15 domain closure`.

Date: 2026-09-09.

The Wave-1 deferral served its purpose and is retained only as historical context.

Current accepted Connectivity Decision truth is defined by:
- `docs/domain/connectivity-decision-model.md`;
- `docs/requirements/connectivity-decision-core.md`;
- `docs/requirements/connectivity-decision-acceptance-examples.md`;
- `docs/architecture/connectivity-decision-boundary.md`;
- `docs/decisions/ADR-004-connectivity-decision-bounded-context.md`.

The former external/deferred seam has been promoted to a first-class Connectivity Decision Bounded Context.

Runtime implementation remains I16. Until I16 completes, `local-dev:allowed` is still test/development plumbing only and is not accepted Decision-domain behavior.
