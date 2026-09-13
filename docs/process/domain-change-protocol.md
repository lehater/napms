# Domain-change re-entry protocol

Use this focused protocol when implementation, testing or new requirements reveal a possible semantic change.

The top-level progression/gate semantics live in `docs/process/change-lifecycle.md`. This file does not define a parallel lifecycle; it helps determine which domain layer must be reopened.

## Classify the highest affected layer

```text
implementation detail only
    -> Implementation Readiness / code-tests impact

accepted behavior or quality expectation changes
    -> Requirements
       -> revalidate dependent Domain/Architecture/Implementation stages

aggregate/invariant/semantic identity/lifecycle changes inside one BC
    -> Tactical Domain Design
       -> revalidate requirements/contracts impact where applicable
       -> revalidate Architecture/Implementation stages

language, responsibility, authority or lifecycle boundary changes between BCs
    -> Strategic Domain Design
       -> revalidate affected requirements/contracts
       -> revalidate Architecture/Tactical Domain/Implementation stages
```

Do not let a lower layer silently solve an upstream semantic unknown. Record the problem and return `REOPEN(stage)` through the change lifecycle when an earlier stage owns the missing truth.

## Strategic DDD re-entry trigger

Revisit Strategic DDD only when evidence materially changes at least one of:
- ubiquitous language boundary;
- responsibility/decision ownership;
- independent lifecycle/invariants;
- authority boundary;
- context relationship.

A new class, table, API, deployment unit or shared library is not by itself a Strategic DDD trigger.
