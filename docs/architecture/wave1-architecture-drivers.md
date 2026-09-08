# Wave-1 architecture drivers — PLAN-027 WP-03

Status: `accepted architecture-driver synthesis`.

Date: 2026-09-08.

## Ranked drivers

### D1 — Authoritative semantic correctness and idempotency — P1
Access Policy must guarantee one authoritative Rule per immutable semantic identity under retries/concurrency. First Allowed materialization is Active; NotAllowed never materializes a Rule.

### D2 — Temporal coherence and fail-closed export — P1
A successful export must represent one logical as-of and be complete for every selected effective Rule. Missing/stale/unknown required facts make the result non-successful, not best-effort success.

### D3 — End-to-end provenance/explainability — P1
Every successful normalized row must remain traceable through Rule, decision, operational state/properties, proposal/authority provenance, DCS facts, technical realization and export as-of.

### D4 — Separation of immutable semantic identity from mutable realization — P1
Source/Destination Deployment + immutable DCS define Rule identity. Address/endpoint/provider realization may change without mutating Rule identity/decision.

### D5 — Preserve semantic ownership without BC=service coupling — P1
Access Policy, Authority Management, Application Communication Catalogue and Resource Catalogue have distinct semantic ownership. Architecture may colocate them physically but must not blur authoritative ownership or derive deployment units mechanically from BCs.

### D6 — Deferred Connectivity Decision seam — P1
Wave 1 depends only on exact-subject `Allowed|NotAllowed` plus opaque provenance/reference. Architecture must allow that dependency to remain external/manual/adapted initially and later evolve without putting invented decision-domain logic into Access Policy.

### D7 — Authority and audit correctness — P2
Proposal, Rule mutation and export are permitted for action/scope/effective time; historical provenance is retained. Operational state transitions are attributable.

### D8 — Vendor-neutral semantics-preserving handoff — P2
Normalized export is a stable semantic boundary before future rendering/execution. Normalization may expand but must not lose independent Rule meaning/provenance or introduce vendor/device semantics.

### D9 — Legacy coexistence without Legacy-shaped target domain — P2
Transition may temporarily adapt Legacy data/interfaces, but Excel/SQL/module/device structure must not become target domain architecture by inertia. Target and Transitional Architecture remain distinct.

### D10 — Evolvability/reversibility under unknown scale and future waves — P2
Current evidence has no numeric SLA/workload envelope. Avoid irreversible distribution/topology choices justified by imagined scale. Keep seams suitable for later rendering, reconciliation, Connectivity Requirements and Decision Domain participation.

## Constraints / non-drivers

- No numeric latency/throughput/availability target is accepted yet.
- Network device execution reliability is outside Wave 1.
- Vendor configuration rendering is outside Wave 1.
- Bounded Context count is not a service-count requirement.
- Existing Legacy schemas/modules are transition evidence, not target topology constraints.

## Architecture consequences

Candidate structures must demonstrate:
1. a strong consistency mechanism for Access Policy Rule uniqueness/materialization;
2. a credible coherent-read/as-of strategy across semantic owners for export;
3. provenance propagation across all participating boundaries;
4. explicit authority integration without hard-coded static-role semantics;
5. replaceable external seam for Connectivity Decision;
6. low operational complexity unless distribution is justified by evidence;
7. clean isolation of temporary Legacy adapters from target domain ownership.

## WP-03 result

Architecture option selection is driven primarily by semantic consistency/coherence/provenance and reversibility, not by service decomposition or unsupported scale assumptions.