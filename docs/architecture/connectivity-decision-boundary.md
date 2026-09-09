# Connectivity Decision Boundary

Status: `accepted and implemented through I16B`.

Date: 2026-09-09.

## Purpose

Define the current durable Connectivity Decision boundary while preserving Clean Architecture and bounded-context ownership.

## Ownership

**Connectivity Decision** is a first-class semantic owner.

It owns:
- DecisionId;
- exact RuleSemanticIdentity subject;
- Decision Governance Scope;
- final Allowed/NotAllowed outcome;
- validity;
- reason/evidence references;
- deciding provenance;
- supersession history.

It does not own:
- proposal authority;
- Connectivity Requirement identity/lifecycle;
- ACC/RC facts;
- Access Rule identity/state/properties;
- authentication/IAM;
- UI workflow.

## Context relationships

```text
Connectivity Requirements --evidence reference--> Connectivity Decision
Application composition --proposal subject/scope--> Connectivity Decision
Authority Management --decision/read authority--> Connectivity Decision
Connectivity Decision --effective final decision--> Access Policy
Connectivity Decision --coarse final summary--> Scoped Connectivity Inventory
```

All relationships use semantic contracts/ports. No consumer reads Decision persistence directly.

## Application boundary

The Decision-domain application layer exposes use cases equivalent to:

```text
RecordConnectivityDecision
GetConnectivityDecision
ListConnectivityDecisions
DiscoverDecisionScopes / DiscoverDecisionInteractions
SelectEffectiveConnectivityDecision
```

Exact HTTP routes/DTOs are not domain meaning.

### Record input

Trusted application input:
- authenticated actor/principal;
- proposal exact subject;
- governance scope;
- business action time;
- outcome;
- validity;
- reason code/text;
- evidence references;
- optional supersedes DecisionId.

The runtime must not accept caller-supplied authority provenance as truth.

### Selection input

Consumer input:
- exact RuleSemanticIdentity;
- exact governance scope;
- logical asOf.

Consumer output:
- one effective Allowed/NotAllowed Decision with DecisionId/provenance;
- no decision;
- explicit unknown/ambiguous failure.

## Authority boundary

Connectivity Decision owns consumer-specific Authority ports.

The runtime checks `DecideConnectivity` before recording/superseding and `ReadConnectivityDecision` before exposing protected Decision data.

Authority Management remains owner of assignment/effectiveness semantics.

## Persistence boundary

I16 may introduce Decision-owned persistence.

Required invariants at the persistence boundary:
- unique DecisionId;
- immutable historical records;
- version/concurrency-safe supersession;
- no trusted success after unknown commit acknowledgement;
- prevention/detection of multiple current effective Decisions for one subject/scope/asOf.

Exact schema/locking strategy is I16 implementation detail.

## Access Policy consumer port

Access Policy consumes only the minimal semantic projection required for proposal materialization:

```text
EffectiveConnectivityDecision
    decisionId
    subject
    governanceScope
    outcome = Allowed | NotAllowed
    validFrom
    validUntil?
```

Access Policy does not consume Decision workflow internals, reason policy algebra or persistence model.

The current Access Policy consumer port selects by exact subject, proposal governance scope and logical `asOf`, and receives only the minimal effective Decision projection above.

## Runtime transition

The normal product journey uses the durable Connectivity Decision runtime.

The historical deterministic `local-dev:allowed` adapter is not selected by normal local composition and has been removed from the runtime path. Focused tests may still supply explicit consumer-port fakes without redefining Decision-domain truth.

## Workflow disposition

I15 does not accept a pending approval queue.

If I16 needs human decision entry, the UI is a direct authorized final-decision workspace over unresolved proposal subjects. A richer case lifecycle/work queue is introduced only if concrete behavior cannot be represented without it.

## Security/failure rules

- proposal authority never authorizes decision mutation;
- request payload cannot establish deciding actor, action time or authority provenance;
- Decision subject/scope mismatch fails closed;
- missing/expired/ambiguous Decision never becomes Allowed;
- read permission does not imply decision permission;
- external evidence references do not grant authority;
- unexpected infrastructure failures return generic public errors while retaining safe correlation internally.

## Dependency direction

```text
Connectivity Decision Domain
        ^
        |
Connectivity Decision Application / Ports
        ^
        |
Adapters / PostgreSQL / HTTP / Composition
```

Access Policy depends on a consumer-owned semantic port, not on Decision infrastructure classes.
