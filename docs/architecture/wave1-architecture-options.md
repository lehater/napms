# Wave-1 architecture options and trade-offs — PLAN-027 WP-04

Status: `accepted option analysis; selected strategy ready for ADR`.

Date: 2026-09-08.

## Decision

Select a **modular application architecture with explicit semantic modules and ports/adapters**, deployed initially as the minimum number of operational units justified by integration constraints. Do not assign one service/database per Bounded Context.

The core Wave-1 product should begin as one coherent application/deployment unit unless a concrete external ownership/integration constraint requires a separate adapter/process. Connectivity Decision remains behind an external port. Legacy/enterprise integrations remain adapters. Physical data ownership may use one transactional store initially while preserving module-owned data access and semantic ownership.

## Option A — Modular monolith / coherent application core — selected

Structure:
- one primary Wave-1 application runtime;
- explicit modules for Access Policy, Authority integration, Application Communication Catalogue integration/model, Resource Catalogue integration/model and application use cases;
- module boundaries enforced in code/contracts;
- one authoritative transaction boundary available for Access Policy invariants;
- external/deferred Decision Domain and Legacy/enterprise dependencies behind ports/adapters;
- normalized export as application output boundary.

Strengths:
- simplest credible operational model;
- strongest support for Rule uniqueness/idempotency and coherent orchestration;
- avoids distributed consistency solely because DDD has multiple contexts;
- easiest end-to-end provenance/testing for current slice;
- reversible: modules can later be extracted if evidence establishes deployment independence/scale/security drivers.

Costs/risks:
- semantic module discipline must be enforced or boundaries can erode;
- catalogue ownership may be external in reality, requiring adapters and temporal snapshots/versioned reads rather than pretending local ownership;
- future independent scaling/deployment may require extraction work.

## Option B — Service per participating Bounded Context — rejected for Wave 1

Structure: separate deployable Access Policy, Authority Management, Resource Catalogue, Application Communication Catalogue services plus orchestration/export service.

Potential strengths: explicit runtime isolation, independent deployment/scaling.

Why rejected now:
- no accepted workload/team/security driver requires this distribution;
- turns coherent export into a distributed temporal-consistency problem immediately;
- increases failure modes/operability and provenance propagation complexity;
- risks equating BC with service, explicitly prohibited by project methodology;
- Decision Domain remains unknown, so a distributed topology would freeze assumptions prematurely.

Revisit: measured scale, organizational ownership, security boundary or independent release cadence that materially benefits from extraction.

## Option C — Legacy-centered extension — rejected as target; usable only transitionally

Structure: retain Legacy Excel/SQL/module flows as core and add new Rule/export behavior around them.

Potential strength: short-term compatibility.

Why rejected as target:
- Legacy technical row/request/package semantics conflict with accepted Access Rule identity and fail-closed export semantics;
- preserves implementation mechanisms as domain meaning;
- makes later displacement harder and contaminates target ownership.

Allowed only as Transitional Architecture adapters/bridges with retirement triggers.

## Option D — Event-driven distributed core — rejected for Wave 1

Potential strengths: decoupling/history/scaling.

Why rejected now:
- no evidence requires independent asynchronous evolution;
- authoritative uniqueness and coherent as-of export still need explicit consistency semantics and become harder, not automatically solved;
- introduces operational/event-contract complexity before workload and decision-domain behavior are known.

Event/audit records may still be implementation techniques inside the selected architecture; this rejection concerns making distributed event-driven topology the primary structure.

## Selected structural principles

1. Semantic modules follow ownership; deployment units follow actual architecture drivers.
2. Access Policy is the authoritative consistency boundary for Rule identity/state.
3. Application orchestration composes proposal/export flows without becoming owner of catalogue/policy truth.
4. External facts cross explicit ports with provenance/effective-time semantics.
5. Successful export evaluates against a coherent logical as-of using an architecture mechanism selected during detailed design; physical co-location is not assumed to equal semantic ownership.
6. Connectivity Decision is replaceable behind an exact-subject port.
7. Legacy compatibility exists only in adapters/transition components.
8. Prefer local transactions and simple runtime topology until evidence justifies distribution.

## WP-04 result

A modular coherent application core is the lowest-complexity option that satisfies current P1 drivers and preserves later extraction. Service-per-BC, Legacy-centered target and distributed event-driven core are not justified by current evidence.