# Lifecycle specification

Status: SKELETON — M1 owns completion.

## Purpose

Define routing, stage responsibilities, gate semantics, reopen/dirty propagation and implementation authorization without embedding stage-specific working instructions.

## Skeleton

```text
S0 Problem / Evidence          -> G0
S1 Requirements                -> G1
S2 Domain Design               -> G2
S3 Architecture                -> G3
S4 Implementation Readiness    -> G4
IMPLEMENTATION -> VALIDATION
```

## Core boundary

A stage creates or updates canonical knowledge artifacts. A gate validates whether the artifacts required by the next stage are sufficient. A gate is not itself a product artifact.

Enter at the earliest stage whose accepted truth may change; revalidate only affected downstream truth.

## M1 must define

- inputs, responsibilities and exit guarantees for S0-S4;
- G0-G4 evidence rules;
- stage/gate states and transitions;
- reopen and dirty propagation;
- exact implementation authorization semantics;
- interaction with artifact requirements;
- minimal routing data required by an agent.

Do not define detailed artifact schemas here; those belong to the artifact catalog.