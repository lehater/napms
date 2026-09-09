# ADR-003 — Connectivity Decision as an external semantic port

Status: `superseded by ADR-004`.

Date: 2026-09-08.

## Historical context

Wave 1 required `ConnectivityDecision(Allowed|NotAllowed)` for an exact proposed Rule semantic identity while internal decision reasons, policies, workflow, actors, exceptions and lifecycle were deliberately unknown.

## Historical decision

Wave 1 represented Connectivity Decision as an external semantic port with the minimum contract:

`exact proposal subject -> Allowed|NotAllowed + opaque reference`.

Access Policy consumed the result and did not own decision reasons/process.

## Supersession

The ADR revisit trigger was met by I15.

ADR-004 promotes Connectivity Decision to a first-class Bounded Context with accepted decision identity, governance scope, validity, reason/provenance, Authority actions and supersession semantics.

This ADR remains historical evidence of the deliberate Wave-1 deferral.
