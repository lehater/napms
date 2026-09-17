# NAPMS full-width quality requirements

Status: CANDIDATE / non-canonical / S1 reconstruction from accepted `docs/**`.

These requirements describe externally relevant or system-wide qualities. S3/S4 implementation mechanisms are not made canonical here merely because current engineering documents realize them in a particular way.

## Semantic safety

- **QREQ-SAFE-001 CURRENT** — missing, ambiguous, unavailable or subject-mismatched authority/identity/semantic dependency knowledge must not be converted into permission, valid access truth or successful materialization.
- **QREQ-SAFE-002 CURRENT** — expected denied/not-allowed outcomes remain distinguishable from Unknown/Unavailable and from technical failure.
- **QREQ-SAFE-003 CURRENT** — dependency subject mismatch is rejected rather than silently repaired, substituted or correlated to a different subject.
- **QREQ-SAFE-004 CURRENT** — authoritative state is not reported changed when persistence/mutation outcome cannot be established.

## Consistency and retry safety

- **QREQ-CONS-001 CURRENT** — semantic retries must not manufacture duplicate business attempts or duplicate authoritative identities.
- **QREQ-CONS-002 CURRENT** — stale concurrent decisions/mutations must not overwrite a newer authoritative state.
- **QREQ-CONS-003 CURRENT** — a successful full-policy/export result is coherent across all owner inputs used to construct it; inconsistent-current reads are not silently published as one current truth.
- **QREQ-CONS-004 CURRENT** — a complete-policy materialization/export is complete-or-unresolved; unresolved selected policy does not become partial success.
- **QREQ-CONS-005 CURRENT** — alternate representations of one published export, including table/JSON and CSV, represent the same immutable materialized result rather than independently re-reading live truth.

## Provenance and explainability

- **QREQ-PROV-001 CURRENT** — business-significant authoritative state preserves actor/time/source/provenance needed to explain current and historical truth.
- **QREQ-PROV-002 CURRENT** — operational correlation identity does not replace domain identity or authoritative business provenance.
- **QREQ-PROV-003 CURRENT** — observed, recognized, needed, proposed, accepted, materialized, realized, executed and verified facts remain distinguishable in explanation and audit.

## Security and information disclosure

- **QREQ-SEC-001 CURRENT** — trusted actor identity, authority evidence and command/current time used for protected decisions are server/integration-owned trusted inputs, not caller-asserted truth.
- **QREQ-SEC-002 CURRENT** — user-facing failures do not expose secrets, credentials, internal stack traces, raw vendor/database exceptions or unrelated authority/catalogue/decision data.
- **QREQ-SEC-003 CURRENT** — full-policy reads and other protected operations fail closed on Denied or Unknown authority and disclose no protected policy data on failed admission.
- **QREQ-SEC-004 CURRENT** — provider-specific and infrastructure-specific exception/details do not redefine core domain/application semantics.

## Operability and recovery

- **QREQ-OPS-001 CURRENT** — supported operation exposes enough safe diagnostic context to distinguish successful, denied/invalid, degraded/unknown and unexpected-failure outcomes and correlate a request/command across boundaries.
- **QREQ-OPS-002 CURRENT** — operational logs/telemetry are diagnostic evidence, not authoritative substitutes for domain audit/provenance.
- **QREQ-OPS-003 CURRENT** — supported durable product state has an explicit backup/recovery path with verification that restored authoritative state is usable; recovery claims distinguish durable NAPMS truth from ephemeral runtime and external-system state.
- **QREQ-OPS-101 EXTENSION** — stronger recovery objectives, point-in-time recovery, replication, enterprise retention and richer telemetry remain evidence-driven extensions unless separately accepted.

## Reconstruction and ownership

- **QREQ-DOC-001 CURRENT** — current as-built and target design remain reconstructible from accepted documentation without consulting implementation as design authority.
- **QREQ-OWN-001 CURRENT** — compositions, views, workflows, transports and adapters preserve semantic ownership and do not acquire authoritative truth merely by storing, projecting or transporting it.
