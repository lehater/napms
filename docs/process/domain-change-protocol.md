# Domain-change re-entry protocol

Use this protocol when implementation, testing or new requirements reveal a possible semantic change.

## Classify the highest affected layer

```text
implementation detail only
    -> code/tests

accepted behavior or quality expectation changes
    -> requirements
       -> architecture impact
       -> code/tests

aggregate/invariant/semantic identity/lifecycle changes inside one BC
    -> Tactical DDD
       -> requirements/contracts impact
       -> architecture impact if material
       -> code/tests

language, responsibility, authority or lifecycle boundary changes between BCs
    -> Strategic DDD
       -> requirements
       -> architecture/ADRs
       -> Tactical DDD
       -> code/tests
```

Do not let a lower layer silently solve an upstream semantic unknown.

## Strategic DDD re-entry trigger

Revisit Strategic DDD only when evidence materially changes at least one of:
- ubiquitous language boundary;
- responsibility/decision ownership;
- independent lifecycle/invariants;
- authority boundary;
- context relationship.

A new class, table, API, deployment unit or shared library is not by itself a Strategic DDD trigger.
