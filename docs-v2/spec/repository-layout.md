# Repository layout specification

Status: SKELETON — M3 owns completion.

## Purpose

Define where canonical artifacts live, naming conventions, locality/ownership rules and generated-output policy.

## Target shape to evaluate

```text
docs/
  problem/
  requirements/
    functional/
    quality/
  domain/
  architecture/
  contracts/
  decisions/
  plans/
  process/
```

This is a design hypothesis, not yet an approved layout.

## Invariants

- storage follows knowledge ownership, not lifecycle gate numbers;
- requirements do not require bounded contexts to exist;
- bounded-context-specific domain artifacts live with their context;
- generated renderings do not replace source artifacts;
- empty optional directory trees are not pre-created;
- one canonical owner exists for current truth; indexes/projections may reference it but not duplicate it.

## M3 must define

Path patterns, naming, artifact locality, cross-cutting artifacts, contract placement, ADR placement, generated outputs, traceability/index placement and cutover target tree.