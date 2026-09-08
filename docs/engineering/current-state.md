# Current implementation state

Status: `I6 PASS — I7 controlled integration selection may begin under the active plan`.

Date: 2026-09-08.

Current execution is owned by `docs/plans/active/README.md`; do not mirror its work-package status here.

## Completed through I6

- I1 authoritative Access Rule materialization core;
- I2 PostgreSQL uniqueness/concurrency/rollback proof;
- I3 authorized Active/Inactive mutation with durable business audit;
- I4 EffectiveWindow mutation/evaluation and authorized effective desired-policy selection;
- I5 coherent immutable Export Snapshot with source-neutral ACC/RC projection ports;
- accepted Wave-1 normalized traffic selector `DcsTrafficAlternative`;
- explicit source and destination port constraints with distinct `NotApplicable | Any | canonical PortRange set` semantics;
- inclusive `PortRange(0..65535)` validation and canonical sorted/non-overlapping/non-adjacent range sets;
- optional ACC-owned service reference preserved separately from explicit traffic selector semantics;
- protocol represented as a non-empty canonical source-neutral token without inventing a Wave-1 protocol registry/vendor mapping;
- pure/local `DcsProjectionDecoder` boundary for immutable I5 DCS payload bytes; no live owner lookup during normalization;
- deterministic per-Rule expansion: source endpoint realization × destination endpoint realization × DCS traffic alternative;
- one normalized row retains Rule ID, semantic identity, decision reference, RuleGovernanceScope, effective state/window context, snapshot as-of/read-authority provenance, ACC provenance and both RC provenance chains;
- port ranges remain ranges and are never expanded into per-port rows;
- independently authoritative Rules remain independent even when normalized technical effects are identical;
- malformed snapshot correlation, non-effective/scope-drift Rule, invalid decoder output or decode failure cannot produce a successful normalized export;
- successful normalized export and rows are immutable application results;
- no live catalogue/authority lookup, database, HTTP, vendor rendering or source-specific serializer is used by the I6 transform;
- final I6 semantic/provenance/architecture review has no open P0/P1 finding;
- hosted core gate passed on the I6 implementation candidate.

## I6 result

`PASS`.

Wave-1 vendor-neutral normalization semantics are executable as a pure transformation over a successful immutable Export Snapshot.

Concrete DCS payload encoding/codec and output serialization remain intentionally deferred until a real controlled source/environment and handoff format are selected.

## Current infrastructure boundary

Access Policy PostgreSQL behavior remains proven through I4. I5/I6 add application-composition semantics only.

Real Authority, Application Communication Catalogue, Resource Catalogue and Connectivity Decision adapters are still not selected. I7 owns the first controlled integration choice and must preserve all accepted anti-corruption, temporal and provenance boundaries.
