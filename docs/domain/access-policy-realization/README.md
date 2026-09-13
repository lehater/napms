# Access Policy Realization — Problem Statement and Design Directions

Status: `active design / requirements framing`.

Date: 2026-09-13.

This file is the single current source for the Access Policy Realization (APR) problem statement while its target Tactical DDD is being designed.

APR is treated as a separate bounded context. Its final Tactical DDD, ERD, persistence model, computation engine contract and migration plan are not yet locked.

## Problem statement

APR owns the following problem:

> For a given technical policy target, determine how completely and exactly the currently configured effective access policy realizes the required technical access policy, identify the semantic difference, design the policy change needed to remove that difference, and verify that the proposed change preserves the required access semantics before rendering or execution.

The unit of comparison is **effective access semantics**, not textual firewall configuration, provider-native rule identity, ACL line identity or rule count.

APR therefore reasons about:

```text
required effective access
        versus
configured effective access
```

and must be able to answer:

- what required access is already realized;
- what required access is missing;
- what configured access is excessive relative to the required policy;
- what semantic difference exists between the two policies;
- what policy change should remove that difference;
- whether the proposed resulting policy would exactly realize the required policy;
- how the verified change or target policy can be rendered for a concrete target without changing its semantics.

## Context boundary

### Upstream target selection is not APR responsibility

APR receives a technical policy target through an upstream contract. It does not interpret or reevaluate why that target was selected.

In particular APR does not own:

- candidate relevance;
- forwarding-path or routing analysis;
- route existence;
- path confidence;
- target-selection ambiguity;
- selection of another device or policy attachment instead of the received target.

Those questions belong upstream. For APR, the received target is an input to policy-realization work.

Conceptually:

```text
upstream placement/composition
        |
        | target + required policy
        v
Access Policy Realization
```

### Authorization and catalogue truth remain upstream

APR does not own authoritative Access Rule identity/state, application/component communication contracts, Resource identity/realization, network placement truth or collected technical evidence.

It consumes published contracts/projections needed to construct the required and configured sides of one comparable target policy.

### Execution remains downstream

APR may produce a verified and rendered policy change, but it does not own:

- target connection/session lifecycle;
- device mutation execution;
- retries/backoff;
- operational concurrency control;
- rollback mechanics;
- post-apply transport/device operation lifecycle.

## Conceptual inputs

Final contracts are still to be designed. The current required shape is conceptual.

### Target Required Policy

A target-specific required policy associates one opaque technical target reference with the effective access semantics expected to exist on that target.

```text
TargetRequiredPolicy
    targetRef
    requiredPolicyRef / required effective access
    scope or snapshot identity
    logical/effective time where required
    provenance
```

`targetRef` is opaque to APR core semantics. APR does not need placement/topology meaning in order to compare policy behavior.

### Configured Policy Snapshot

APR also consumes the configured policy state for the same target and comparable scope.

```text
ConfiguredPolicySnapshot
    targetRef
    configuredPolicyRef
    configured effective access
    snapshot/evidence identity
    completeness contract
    provenance
```

The configured side must represent **effective policy semantics** for the comparison scope.

Raw ordered ACL entries, vendor objects, implicit defaults, rule-order behavior, NAT-dependent behavior or other source-specific constructs must not be compared as though textual rule equality were equivalent to effective access equality.

The exact ownership and contract for normalization from provider-specific policy to source-neutral effective access is still to be designed.

## Conceptual outputs

APR results are derived from the selected input policies and target. Current output directions are:

```text
RealizationAssessment
SemanticDelta
PolicyChangeDesign
VerificationResult
RenderedConfiguration
```

Final names, identities and persistence/lifecycle decisions remain open until Tactical DDD is locked.

## Effective technical access space

The core semantic abstraction is an **effective technical access space**.

For the current network-policy problem, one technical region is conceptually defined across dimensions such as:

```text
source address space
x destination address space
x protocol
x source port space
x destination port space
```

A target policy denotes the effective set/union of such regions for the relevant comparison scope.

APR reconciliation semantics require exact operations equivalent to:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

These equations define domain meaning independently from storage representation or computation algorithm.

Two policies are semantically equivalent when they describe the same effective access space, even if their rule decomposition differs. One rule covering a `/24`, for example, may be semantically equivalent to two rules covering its two `/25` halves when all other dimensions and effective behavior are equal.

Raw rule identity, textual equality, object decomposition and rule count are therefore not policy-semantic equality.

## Current requirements direction

### APR-DIR-001 — Treat target selection as upstream truth

APR shall consume target-specific required-policy input without reevaluating candidate, routing, path or placement semantics.

No APR result shall reinterpret target relevance.

### APR-DIR-002 — Compare effective behavior, not configuration text

APR reconciliation shall compare effective access semantics.

Semantically equivalent policies shall compare as equivalent even when represented by different rule counts, address decompositions, policy objects or provider-native identities.

### APR-DIR-003 — Preserve exact policy-space algebra

For complete comparable inputs, APR shall compute exact `common`, `missing` and `excess` policy space without semantic widening or narrowing.

Every computation strategy must preserve the same observable algebra.

### APR-DIR-004 — Separate assessment from semantic delta

APR shall distinguish:

- classification of realization state; and
- the exact semantic difference that explains the state.

A realization status is a summary. The semantic delta remains the authoritative explanation of the difference.

### APR-DIR-005 — Separate semantic delta from policy change design

`missing` and `excess` describe **what semantics differ**. They do not by themselves prescribe the best edit to the existing rulebase.

Policy Change Design is a separate concern and may over time choose strategies such as:

- reuse an existing rule;
- modify an existing rule;
- reuse or modify an existing policy object/group;
- create a new rule/object;
- narrow or remove obsolete policy material.

The first implementation may use a simpler change representation, but the domain model must not collapse semantic difference and concrete policy editing into one concept.

### APR-DIR-006 — Verify proposed changes before execution

APR shall support evaluating the effective semantics of a proposed resulting policy and comparing them with the required policy.

Conceptually:

```text
effective(configured + proposedChange)
        versus
required effective policy
```

Verification must expose remaining missing access and introduced or remaining excess access.

Operational mutation remains outside APR.

### APR-DIR-007 — Keep rendering downstream of semantic design and verification

Provider/vendor rendering shall remain downstream from semantic reconciliation and change design.

Rendering must not broaden, narrow or reinterpret the verified semantic intent.

The target design still must determine whether rendering primarily consumes a verified change design, a full target policy, or both as explicit modes.

### APR-DIR-008 — Keep technical-to-domain attribution as supporting explanation

APR needs an explanation/attribution capability for answering which domain interaction or business meaning corresponds to a technical access region.

This is a supporting concern distinct from pure technical policy equivalence. The target design must not make technical reconciliation depend on attribution unless a concrete invariant requires that dependency.

### APR-DIR-009 — Do not require materialization of massive policy sets in application memory

APR must be designed for very large policy datasets.

The target architecture shall not require complete required/configured policy sets to be hydrated into Python/domain-object collections merely to compute intersection and difference.

Large-set operations should execute **data-locally**, close to the persisted or indexed policy representation, and return compact assessment metadata plus paged/streamed delta details when required.

### APR-DIR-010 — Hide computation strategy behind APR semantics

The implementation technology is not the domain definition.

The application/domain boundary should express policy assessment, comparison, simulation and delta access in APR language through a semantic computation boundary such as a `PolicySemanticEngine`-style port.

A PostgreSQL-backed implementation is a valid first candidate. If later semantics or scale require a symbolic representation such as BDD/FDD/atomic predicates, the domain contract should remain stable.

### APR-DIR-011 — Preserve bounded-context ownership during data-local processing

Performance requirements do not justify unrestricted SQL navigation through another bounded context's private persistence schema.

Data-local integration shall use explicit published projections/contracts or another stable owner-provided integration boundary.

Physical co-location in one PostgreSQL instance does not create a shared domain model.

### APR-DIR-012 — Require trustworthy comparison scope and completeness

A complete realization conclusion is valid only when required and configured sides represent the same target/comparison scope and the configured side is complete for that contract.

Completeness must be explicit. Empty evidence alone does not prove an empty effective policy.

### APR-DIR-013 — Preserve provenance and explainability

Derived APR results shall preserve references sufficient to explain:

- which required-policy input/snapshot was used;
- which target was compared;
- which configured-policy snapshot/evidence was used;
- which logical/evidence time was used where relevant;
- how semantic delta results trace back to contributing inputs.

External references remain external; APR does not turn them into authoritative peer-context identities.

### APR-DIR-014 — Derived computation may be materialized without becoming authoritative truth

APR results are derived by default.

For scale, pagination, rendering, repeatability or reuse, implementations may materialize reconciliation runs, policy-space indexes or delta worksets.

Such state remains derived/computational unless a future product requirement introduces an independent APR lifecycle, for example an editable/approvable change plan.

## Use-case directions

### Assess Policy Realization

Answer:

> How completely and exactly is the required effective policy realized on this target?

A likely result vocabulary includes exact, under-realized, over-realized, diverged and unknown states, but final names are not yet locked.

### Reconcile Policy

Compute the exact semantic relationship:

```text
common
missing
excess
```

For large results, return a compact result/reference and expose delta regions through paged/streamed or data-local consumption rather than constructing one giant in-memory object graph.

### Design Policy Change

Translate semantic difference into a vendor-neutral change design for the existing rulebase.

This is deliberately separate from reconciliation.

### Verify Proposed Change

Evaluate the effective semantics of the proposed resulting policy before execution and prove whether it matches the required policy.

This is semantic pre-change verification, not operational post-deployment verification.

### Render Policy Change / Target Policy

Convert verified vendor-neutral intent into a target/provider-specific representation while preserving semantic equivalence.

### Explain / Attribute Technical Access

Support business/domain attribution of a technical access region for explanation and diagnostics without redefining technical policy equality.

### Future: Policy Optimization

Redundant, shadowed, overly broad and unused policy material is a natural future capability, but it is outside the current core until its own use cases and invariants are accepted.

## Scale and data-local computation

The expected data volume is an architectural driver.

Preferred shape:

```text
APR application use case
        |
        v
APR semantic computation boundary
        |
        v
PostgreSQL-backed or other data-local engine
        |
        +-- required effective-policy projection
        +-- configured effective-policy projection
        +-- exact comparison/index/workset
        |
        v
compact assessment result / delta reference
```

The application process should normally receive references, status/summary metadata, counts/measures where useful and requested pages/fragments. It should not need the complete policy on every call.

PostgreSQL is a reasonable first implementation candidate when both policy sides are already represented as canonical effective technical regions supporting exact relational/range operations.

If ordered ACL semantics, deny/default behavior, nested objects, NAT-dependent semantics or other constructs make relational representation unsafe or inefficient, a specialized symbolic engine may be required. Semantic correctness and measured scale determine that choice.

## Cross-context data boundary

APR needs fast access to upstream facts without coupling to peer persistence internals.

The target design should evaluate explicit APR-facing contracts for:

```text
required effective-policy projection
configured effective-policy projection
target-to-policy correlation
```

Rules:

1. the owning bounded context defines the meaning of each published projection;
2. APR consumes the published contract, not private persistence structure;
3. projections may be physically co-located for performance;
4. derived/indexed copies carry snapshot/freshness/provenance semantics;
5. cross-context database foreign keys must not create a hidden shared aggregate.

## Explicit non-goals of the current framing

This document does not yet define:

- final APR aggregate roots;
- final canonical ERD;
- final physical table/view/materialized-view layout;
- final semantic-engine interface;
- PostgreSQL range/index strategy;
- adoption of BDD/FDD/atomic-predicate techniques;
- exact ownership of provider-specific normalization to effective policy;
- final policy-change operation vocabulary;
- approval/edit lifecycle for change plans;
- final renderer input contract;
- migration patches to current runtime code;
- public API/UI design.

## Next design work

Continue in this order:

1. lock exact APR input/output and cross-context contracts;
2. lock effective-access-space semantics, comparison scope and completeness rules;
3. design the semantic computation/data-local boundary;
4. design policy change semantics;
5. design proposed-change verification;
6. lock rendering boundary;
7. define the canonical Tactical DDD/ERD and persistence decisions;
8. only then create the runtime migration plan.
