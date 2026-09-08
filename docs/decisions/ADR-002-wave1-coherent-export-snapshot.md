# ADR-002 — Coherent logical-as-of export snapshot

Status: `accepted architecture contract; implementation mechanism deferred to inception`.

Date: 2026-09-08.

## Context

A successful Normalized Policy Export must be complete and explainable for one logical `as-of` while Access Policy and catalogue facts may change concurrently. Semantic owners may be physically colocated or external; a distributed transaction across enterprise sources is neither required nor assumed.

## Decision

Treat export input as an explicit immutable **logical export snapshot** assembled for one `asOf` before normalization succeeds.

The snapshot contains/correlates:
- selected effective Access Rules and decision/state/property provenance;
- source/destination technical realizations proven valid for `asOf`;
- referenced DCS projection semantics and validity/provenance;
- authority/provenance required for the export action.

Each contributing external fact must carry a stable identity/version/effective-validity reference sufficient to demonstrate it was valid for the snapshot `asOf`. If the architecture cannot establish that for every selected effective Rule, snapshot assembly fails and no successful export artifact is produced.

The snapshot is a semantic consistency boundary, not necessarily a persisted aggregate or database snapshot. PLAN-028 may choose transaction snapshots, version tokens, temporal queries, immutable read models or equivalent mechanisms per source.

## Alternatives

- read each source opportunistically during row rendering — rejected: cannot prove coherent as-of under concurrent change;
- require one shared database/global transaction for all semantic owners — rejected: confuses physical storage with ownership and overconstrains external catalogues;
- best-effort rows with warnings but success status — rejected by G2 fail-closed semantics.

## Consequences

- normalization operates on stable captured inputs rather than live mutable lookups;
- provenance/version/effective-time references are architecture-significant data;
- external integrations must support temporal/version evidence or an adapter-owned capture mechanism;
- snapshot assembly has an explicit failure/degraded result distinct from successful export.

## Revisit trigger

Revisit mechanism, not semantics, when concrete source capabilities and workload are known. The one-as-of complete-success invariant remains unless product requirements change.