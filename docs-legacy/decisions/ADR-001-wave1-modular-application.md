# ADR-001 — Wave-1 modular application architecture

Status: `accepted`.

Date: 2026-09-08.

## Context

Wave 1 requires authoritative Rule uniqueness/idempotency, coherent logical-as-of export, end-to-end provenance and explicit semantic ownership. No accepted workload, organizational or security evidence requires independently deployable services. Strategic Bounded Contexts are explicitly not deployment units.

## Decision

Implement the Wave-1 target as a modular application architecture with explicit semantic modules and ports/adapters. Start with one primary coherent application/deployment unit unless a concrete external integration constraint requires a separate adapter/process.

Access Policy owns the authoritative Rule consistency boundary. Other semantic owners remain distinct in model/contracts even if initially colocated physically. Connectivity Decision and enterprise/Legacy dependencies are accessed through replaceable ports/adapters. A shared physical transactional store is permitted initially, but modules must not bypass semantic ownership through arbitrary cross-module persistence access.

## Alternatives

- service per participating Bounded Context — rejected: unsupported distribution and immediate consistency/operability cost;
- Legacy-centered extension — rejected as target: conflicts with accepted greenfield semantics; allowed only transitionally;
- distributed event-driven core — rejected: no current driver justifies topology/contract complexity.

## Consequences

Positive:
- simple operations and testing;
- strong local consistency for Rule invariants;
- lower complexity for coherent export/provenance;
- preserves semantic modularity and later extraction.

Negative/risks:
- requires enforceable module boundaries despite one runtime/store;
- future independent deployment may require extraction/migration;
- external catalogue coherence still needs explicit temporal/version semantics and cannot be assumed from local transactions.

## Reversibility / revisit triggers

Revisit deployment decomposition when accepted evidence establishes material independent scaling, release cadence, organizational ownership, security/trust isolation, availability or workload requirements that outweigh distribution cost.

Do not revisit merely because Strategic DDD has multiple Bounded Contexts.