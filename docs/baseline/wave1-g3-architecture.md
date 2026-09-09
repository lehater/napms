# Wave-1 G3 — Target + Transition Architecture

Status: `G3 PASS — historical accepted snapshot`.

Date: 2026-09-08.

## Purpose

Record the G3 architecture decision that allowed implementation inception to begin.

This snapshot is historical provenance. Detailed G3 working architecture packets were absorbed and removed from the living architecture surface. Current target architecture is `docs/architecture/current-architecture.md`; exact historical packets remain in Git history.

## Selected architecture at G3

Wave 1 selected:
- modular application architecture with explicit semantic modules and ports/adapters;
- one primary coherent application/deployment unit until evidence justified distribution;
- Access Policy as authoritative Rule consistency boundary;
- Bounded Contexts as semantic ownership boundaries, not service/database mappings;
- immutable logical Export Snapshot for one `asOf`;
- source identity/version/effective-validity provenance sufficient for coherent export;
- explicit transition adapters so Legacy schemas did not become target ownership.

At G3, Connectivity Decision was deliberately kept behind an external/deferred semantic port. That part of the snapshot is historical: ADR-005 later promoted Connectivity Decision to a first-class Bounded Context.

## Durable current successors

- `docs/architecture/current-architecture.md`;
- `docs/decisions/ADR-001-wave1-modular-application.md`;
- `docs/decisions/ADR-002-wave1-coherent-export-snapshot.md`;
- `docs/decisions/ADR-005-connectivity-decision-bounded-context.md`;
- feature-specific boundaries under `docs/architecture/`;
- current implementation/runtime evidence.

ADR-003 remains only the historical record of the former Decision port deferral.

## G3 challenge result

The accepted architecture closed these material risks:
- no service-per-BC inference;
- authoritative Rule uniqueness/idempotency retained;
- no incoherent successful export under changing catalogue facts;
- normalization keeps end-to-end provenance;
- physical database sharing cannot justify cross-module semantic bypass;
- Legacy source shape cannot redefine target identity;
- topology remains reversible while scale/SLA evidence is unknown.

No open P0/P1 architecture finding blocked inception.

## Decision

`PASS` — implementation inception could begin while preserving the accepted G2/G3 invariants.

For exact historical option/view/threat/transition packet wording, use Git history.
