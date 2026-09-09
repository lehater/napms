# ADR-004 — Connectivity Decision as a first-class bounded context

Status: `accepted`.

Date: 2026-09-09.

## Context

ADR-003 deliberately kept Connectivity Decision as an external/deferred semantic port during Wave 1 because decision identity, reasons, authority, validity and lifecycle were unknown.

I13/I14 established durable Connectivity Requirements and explicit Requirement-to-Policy Alignment. The post-Wave-1 roadmap now requires NAPMS to explain/manage why an exact proposal becomes Allowed or NotAllowed and to replace the local deterministic allow adapter.

The revisit trigger from ADR-003 is therefore met.

## Decision

Promote **Connectivity Decision** to a first-class Bounded Context.

The context owns immutable final Decision records with:
- stable DecisionId;
- exact RuleSemanticIdentity subject;
- Decision Governance Scope equal to the accepted proposal authority scope in the first model;
- outcome `Allowed | NotAllowed`;
- explicit validity;
- mandatory reason/provenance;
- optional evidence references;
- immutable supersession history.

Authority Management independently admits `DecideConnectivity` and `ReadConnectivityDecision`.

A deciding principal may be human or automated. No pending approval lifecycle, quorum or SoD is introduced without a concrete accepted requirement.

Access Policy consumes only one effective final Decision for exact subject/scope/logical time and continues to own Access Rule state/lifecycle.

## Consequences

- I16 can implement a durable local Decision provider without inventing domain semantics in adapters;
- `local-dev:allowed` is no longer a valid normal-product decision mechanism;
- Connectivity Requirements can be referenced as evidence without becoming authorization;
- decision history is explainable and immutable;
- proposal authority and decision authority remain independent;
- later Decision expiry/supersession does not silently mutate existing Access Rules;
- richer approval/case/revocation semantics remain explicit future changes, not hidden assumptions.

## Supersedes

This ADR supersedes ADR-003 for current target architecture.

ADR-003 remains historical evidence of the Wave-1 deferral.
