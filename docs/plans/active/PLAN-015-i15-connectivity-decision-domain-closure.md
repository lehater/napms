# PLAN-015 — I15 Connectivity Decision Domain Closure

Status: `active`.

Date: 2026-09-09.

## Goal

Close the deferred Connectivity Decision domain so I16 can implement a durable non-local decision provider without inventing business semantics in runtime code.

## Current stage

WP1-WP4 semantic work is accepted on the branch. WP5 closure is active: consistency validation, canonical current-state/roadmap absorption and final PR gate.

## Inputs

- `docs/domain/deferred-connectivity-decision.md`;
- `docs/decisions/ADR-003-connectivity-decision-port.md`;
- current Connectivity Requirements and Access Policy canonical truth;
- I15 roadmap questions in `docs/engineering/post-wave1-product-completion-roadmap.md`.

## Scope

In scope:
- Strategic DDD disposition and semantic ownership;
- Tactical DDD for decision identity, subject, outcome, validity, reason/provenance and supersession;
- relationship to Access Rule Proposal, Connectivity Requirement, Authority Management and Access Policy;
- authority actions and fail-closed semantics;
- requirements and acceptance examples;
- architecture/ADR contract for the future I16 runtime.

Out of scope:
- PostgreSQL/runtime/Web implementation;
- approval queue UI;
- quorum/SoD unless domain evidence requires it;
- enterprise IdP/source integration;
- automatic Access Rule revocation/change management.

## Work packages

### WP1 — Semantic closure — done
Connectivity Decision is a first-class Bounded Context with distinct DecisionId, exact RuleSemanticIdentity subject, proposal-derived governance scope, binary final outcome and independent decision/read authority.

### WP2 — Tactical model — done
Immutable Decision validity, mandatory reason/provenance, evidence references, supersession and fail-closed selection semantics are accepted.

### WP3 — Product requirements — done
Core requirements and acceptance examples cover authority separation, Allowed/NotAllowed, missing/ambiguous decisions, Requirement evidence and immutable reconsideration.

### WP4 — Architecture contract — done
ADR-004 and the durable boundary define the I16-compatible context relationship while keeping Access Policy independent of Decision internals.

### WP5 — Closure — active
- consistency review across domain/requirements/architecture;
- update roadmap/current-state;
- repository harness/knowledge validation;
- remove absorbed active-plan artifacts;
- final PR gate.

## Exit criteria

I15 is complete when:
1. Connectivity Decision ownership is explicit in Strategic DDD;
2. Tactical semantics answer every I15 roadmap question;
3. requirements/acceptance examples are testable;
4. ADR/architecture define the I16-compatible boundary;
5. no I15 runtime behavior is invented in Access Policy;
6. repository gates pass;
7. I16 is promoted as next roadmap increment.

## Blockers

None known. Local network access is unavailable in the execution sandbox, so repository-local checks are verified against validator rules and the hosted PR CI is the authoritative final gate.

## Next

Absorb I15 into roadmap/current-state, remove active-plan artifacts, mark PR ready and require final CI before squash merge.
