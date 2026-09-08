# Wave-1 threat model — PLAN-027 WP-08

Status: `accepted G3 threat baseline`.

Date: 2026-09-08.

## Assets

- authoritative Access Rules and operational state;
- authority assignments/effective permission evidence;
- application/resource catalogue identities and technical realization;
- Connectivity Decision correlations;
- normalized export and provenance chain;
- audit history.

## Trust boundaries

- actor/client -> NAPM application;
- NAPM -> Authority source;
- NAPM -> Application Communication Catalogue source;
- NAPM -> Resource Catalogue source;
- NAPM -> Connectivity Decision provider/manual bridge;
- NAPM -> Legacy transition adapters;
- NAPM -> export consumer/storage.

## Material threats and required architecture treatment

### T1 — Unauthorized proposal/state mutation/export — P1
Mitigation: action/scope/effective-time authority check at application use-case boundary; domain mutation also enforces invariants independent of UI visibility; attributable audit for accepted mutations.

### T2 — Decision-subject substitution/replay — P1
Mitigation: immutable exact semantic identity correlation between proposal, decision and materialization; reject mismatch; retain decision reference/provenance; idempotent materialization prevents duplicate authority objects.

### T3 — Catalogue identity/realization tampering or stale substitution — P1
Mitigation: trusted-source adapters, stable source identity/version/effective-validity evidence, logical export snapshot, fail closed when validity cannot be established.

### T4 — Export semantic broadening/narrowing or provenance loss — P1
Mitigation: normalize only immutable snapshot inputs; semantics-preserving transformation tests; retain Rule/decision/source correlation per row; independent Rules not merged when meaning/provenance would be lost.

### T5 — Direct persistence bypass of semantic owner — P1
Mitigation: module-owned persistence access; no cross-module table mutation/read shortcut replacing contracts; Access Policy is sole authoritative Rule mutation boundary.

### T6 — Legacy adapter contaminates target authority — P2
Mitigation: explicit anti-corruption/translation adapters; source provenance; Legacy facts never silently promoted to target ownership; transition components carry retirement triggers.

### T7 — Audit/provenance tampering — P2
Mitigation: append/immutable-enough audit semantics for accepted Rule transitions/material actions; restrict mutation; correlate records with actor/time/source identities. Exact tamper-evidence technology is PLAN-028 detail.

### T8 — Sensitive topology/address leakage through export — P2
Mitigation: export requires scoped authority; output includes only selected policy scope; transport/storage protection and retention become implementation controls. No evidence currently requires a separate security deployment boundary.

### T9 — Dependency outage/unknown response converted to permission/success — P1
Mitigation: fail closed for unknown authority, structural validity, decision subject/result, or required export facts. Availability degradation is explicit; it never becomes implicit Allowed or successful incomplete export.

## Residual / deferred

- concrete authentication protocol/identity provider;
- cryptographic/secret-management implementation;
- retention periods/data classification;
- rate limits/DoS envelope;
- device execution credentials/threats (outside Wave 1).

These are PLAN-028 or later unless evidence makes them architecture-changing.

## Architecture feedback

Threat analysis reinforces the selected modular architecture: strong application/domain boundaries, explicit external ports, trusted adapters, provenance/version evidence and fail-closed behavior are required. No current threat justifies service-per-BC distribution or a separate security deployment boundary.