# ADR-003 — Connectivity Decision as an external semantic port

Status: `accepted`.

Date: 2026-09-08.

## Context

Wave 1 requires `ConnectivityDecision(Allowed|NotAllowed)` for an exact proposed Rule semantic identity, but the internal decision reasons, policies, workflow, actors, exceptions and lifecycle are deliberately deferred and do not justify a current Bounded Context.

## Decision

Represent Connectivity Decision in the target architecture as an external semantic port owned by the application boundary, with the minimum G2 contract only:

`decide/exchange exact proposal subject -> Allowed|NotAllowed + opaque decision/provenance reference where available`.

Access Policy consumes the result but contains no decision-domain policy/workflow. The port may initially be backed by an external system, manual bridge, Legacy adapter or later dedicated capability without changing Access Policy semantics.

## Consequences

- no invented approval/policy engine is embedded in Wave 1;
- adapters translate external representations to the stable semantic contract;
- exact subject correlation is mandatory; mismatches fail closed;
- transport and whether invocation is synchronous/asynchronous remain implementation/transition decisions.

## Revisit trigger

Reopen domain/architecture ownership when research establishes independent decision-domain language/model/lifecycle/authority or when Wave 1 must itself execute/manage that decision process.