# Access Policy Realization Revalidation — Problem Statement and Design Directions

Status: `active design / requirements framing`.

Date: 2026-09-13.

## Purpose

Capture the current problem statement, responsibility boundary, requirements direction and design questions for the **Access Policy Realization (APR)** bounded context before changing its Tactical DDD, persistence model or runtime implementation.

This document is intentionally a working design brief. It records what has already been established and the directions that must guide the next design pass. It does **not** yet lock the final APR Tactical DDD, ERD, persistence schema, SQL representation, application ports or migration plan.

The review assumes that **Access Policy Realization remains a separate bounded context**. Whether APR should exist as a bounded context is not an open question in this pass.

Existing accepted I18/I20/I21 documents and current code remain evidence of prior implementation choices. Where they conflict with this brief, they are candidates for later supersession or migration; this brief does not silently rewrite them.

## Problem statement

APR owns the problem:

> For a given technical policy target, determine how completely and exactly the currently configured effective access policy realizes the required technical access policy, identify the semantic difference, design the policy change needed to remove that difference, and verify that the proposed change preserves the required access semantics before rendering or execution.

The important unit of comparison is **effective access semantics**, not textual firewall configuration, provider-native rule identity or raw ACL line equality.

APR therefore works with two conceptual sides:

```text
required / desired effective access
            versus
observed / configured effective access
```

and must be able to answer at least:

- what required access is already realized;
- what required access is missing;
- what configured access is excessive relative to the required policy;
- what semantic policy change is required;
- how that semantic change should be represented as a concrete policy change;
- whether the proposed change would produce the required effective policy without introducing unintended access.

## Boundary with Network Enforcement Placement

Network Enforcement Placement (NEP) is upstream of APR.

APR must **not** interpret or reevaluate how NEP selected a Firewall, policy locator, attachment or other technical target. Candidate relevance, forwarding-path confidence, routing ambiguity and other placement semantics belong to NEP.

For APR, a target received through the upstream contract is simply an input to policy-realization work.

Conceptually:

```text
upstream composition / NEP
        |
        | target -> required policy
        v
Access Policy Realization
```

APR does not ask:

- why the target was selected;
- whether the target is a candidate or a proven path element;
- whether another target would be more relevant;
- whether a route exists;
- whether NEP knowledge was ambiguous.

Those questions must be resolved by the owner of the upstream contract before APR is invoked, or represented as the absence of an actionable APR input.

This direction supersedes the idea that APR itself should own `PlacementStatus`, `NoForwardingPath`, placement ambiguity or placement winner selection.

## Conceptual inputs

The final contracts are still to be designed, but APR conceptually requires the following inputs.

### Target required policy

A target-specific required policy associates one technical target with the access semantics that are expected to exist there.

Conceptually:

```text
TargetRequiredPolicy
    targetRef
    requiredAccess
    logical/effective time or snapshot reference
    provenance
```

The target reference is opaque from the APR core point of view. APR does not need topology semantics in order to compare policies.

The required policy may be produced from Access Policy plus the accepted RC/ACC/NEP composition, but APR should not require the full upstream object graphs to be materialized inside its application process merely to perform reconciliation.

### Configured policy snapshot

APR also requires the configured policy state for the same target and comparable scope.

Conceptually:

```text
ConfiguredPolicySnapshot
    targetRef
    configuredPolicyRef
    effective access semantics
    evidence time / snapshot identity
    completeness contract
    provenance
```

The configured side must represent **effective policy semantics** for the comparison scope. Raw ordered ACL entries, vendor objects, implicit defaults, rule-order behavior, NAT-dependent semantics or other provider-specific constructs must not be compared as though their text were the effective access set.

The exact ownership of normalization from provider-specific configuration to source-neutral effective access remains part of the next design pass.

## Conceptual outputs

APR must expose derived results, not copies of upstream authoritative facts.

The target direction includes:

```text
RealizationAssessment
SemanticDelta
PolicyChangeDesign
VerificationResult
RenderedConfiguration
```

The final names and persistence/lifecycle rules remain open until the target Tactical DDD is locked.

## Core semantic model direction

The central mathematical abstraction is an **effective technical access space**.

For the currently supported network-policy subset, a technical region is conceptually defined by dimensions such as:

```text
source address space
x destination address space
x protocol
x source port space
x destination port space
```

A policy is the effective set/union of such regions for a target and managed scope.

The domain semantics must support exact operations equivalent to:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

These operations define the meaning of reconciliation independent of storage or algorithm.

Two policies may therefore be semantically equivalent even when their rule decomposition is different. For example, one rule covering a `/24` may be equivalent to two rules covering its two `/25` halves if every other policy dimension and effective behavior are identical.

Raw rule identity, textual equality, rule count or vendor object decomposition are not policy-semantic equality.

## Working requirements

The following requirements are a **draft target baseline** for the revalidation work. They are not yet a replacement for the accepted numbered I18/I20/I21 requirements.

### APR-DIR-001 — Treat target selection as upstream truth

APR shall consume target-specific required policy input without reevaluating NEP candidate, path, routing or placement semantics.

No APR domain result shall reinterpret target relevance.

### APR-DIR-002 — Compare effective behavior, not configuration text

APR reconciliation shall compare effective access semantics.

Semantically equivalent policies shall compare as equivalent even when represented by different rule counts, address decompositions, objects or provider-native rule identities.

### APR-DIR-003 — Preserve exact policy-space algebra

For comparable complete inputs, APR shall compute exact `common`, `missing` and `excess` policy space without semantic widening or narrowing.

Any implementation technique must preserve the same observable algebra.

### APR-DIR-004 — Separate assessment from semantic delta

APR shall distinguish:

- the classification of realization state; and
- the exact semantic difference that explains that state.

A status such as exact/under-realized/over-realized/diverged is a summary. The semantic delta remains the authoritative explanation.

### APR-DIR-005 — Separate semantic delta from policy change design

`missing` and `excess` describe **what semantics differ**. They do not by themselves prescribe the best edit to the existing rulebase.

APR design shall preserve a separate step for **Policy Change Design**, capable over time of choosing among strategies such as:

- reuse an existing rule;
- modify an existing rule;
- reuse or modify an existing policy object/group;
- create a new rule/object;
- narrow or remove obsolete policy material.

The MVP may begin with a simpler change representation, but the domain boundary must not collapse semantic difference and concrete policy editing into one concept.

### APR-DIR-006 — Verify proposed changes semantically before execution

APR shall have a use case for evaluating the policy semantics that would result from a proposed change and comparing that result with the required policy.

Conceptually:

```text
effective(configured + proposedChange)
        versus
required effective policy
```

The verification result must be able to expose remaining missing access and newly introduced or remaining excess access.

Operational apply/retry/rollback remains outside APR.

### APR-DIR-007 — Keep rendering downstream of semantic design

Provider/vendor rendering shall remain downstream from semantic reconciliation and change design.

Rendering must not broaden, narrow or reinterpret the verified semantic intent.

The next design pass must decide whether the primary renderer input is a full target policy, a policy change design, or whether both modes are required.

### APR-DIR-008 — Keep Technical-to-Domain Resolution as a supporting capability

The existing Technical-to-Domain Access Resolution capability remains useful for attribution, explanation and diagnostics.

It answers a different question from pure technical reconciliation: which domain interaction(s) correspond to a technical access region.

The next design pass must decide whether successful technical reconciliation should require complete I18 attribution, or whether attribution is an independent explanation concern. Current evidence suggests these concerns should not be unnecessarily coupled.

### APR-DIR-009 — Do not materialize massive policy sets in the application process by default

APR must be designed for very large policy datasets.

The target architecture shall not require loading complete required and configured policy sets into Python/domain-object collections merely to compute intersection and difference.

Large-set operations should execute **data-locally**, close to the persisted or indexed policy representation, and return compact assessment metadata plus paged/streamed delta details when required.

### APR-DIR-010 — Hide the computation strategy behind an APR semantic boundary

The fact that the first implementation may use PostgreSQL is an infrastructure decision, not the definition of APR semantics.

The application/domain boundary should express operations such as assessment, comparison, simulation and delta access in APR language, for example through a `PolicySemanticEngine`-style port.

A PostgreSQL-backed implementation may execute exact set algebra in the database. If future policy semantics require a symbolic representation such as BDD/FDD/atomic-predicate techniques, the domain contract should remain stable.

### APR-DIR-011 — Preserve bounded-context ownership in data-local processing

Performance requirements do not justify unrestricted SQL joins against another bounded context's private persistence schema.

Data-local integration shall use explicit published integration/read projections or another stable owner-provided contract.

Physical co-location in one PostgreSQL instance does not create a shared domain model.

### APR-DIR-012 — Require trustworthy comparison scope and completeness

APR may classify a policy as fully realized, under-realized, over-realized or otherwise completely reconciled only when the required and configured sides represent the same target/scope and the configured side is complete for that comparison contract.

Completeness must be explicit. Empty evidence alone is not proof of an empty effective policy.

### APR-DIR-013 — Preserve provenance and explainability

Derived APR results shall preserve references sufficient to explain:

- which required-policy snapshot/input was used;
- which target was compared;
- which configured-policy snapshot/evidence was used;
- which logical/evidence time was used where applicable;
- how missing/excess results can be traced back to their contributing inputs.

APR must not convert external references into new authoritative peer-context identities.

### APR-DIR-014 — Derived computation may be materialized without becoming authoritative truth

APR results are derived by default.

For performance, pagination, rendering or repeatability, implementations may materialize reconciliation runs, canonical policy-space indexes or delta worksets.

Such storage is computational/derived state unless a later product requirement establishes an independent APR lifecycle such as editable/approvable change plans.

## Identified capability/use-case directions

The following use cases are the current target directions for further design.

### 1. Assess Policy Realization

Question:

> How completely and exactly is the required policy already realized on this target?

Expected result direction:

```text
Exact
UnderRealized
OverRealized
Diverged
Unknown
```

with exact semantic delta available separately.

The final vocabulary is still subject to Tactical DDD review.

### 2. Reconcile Policy

Compute the exact semantic relationship between required and configured effective policy:

```text
common
missing
excess
```

For very large results, APR should return a compact result/reference and expose delta regions through paged/streamed or data-local consumers rather than constructing one giant in-memory result graph.

### 3. Design Policy Change

Translate semantic difference into a vendor-neutral change design for the existing rulebase.

This use case is intentionally distinct from reconciliation.

A later optimization level may choose between reusing/modifying existing rules or objects versus creating/removing policy material.

### 4. Verify Proposed Change

Evaluate the effective semantics of the proposed resulting policy before execution and prove whether the result matches the required policy.

This is semantic verification, not operational post-deployment verification.

### 5. Render Policy Change / Target Policy

Convert verified vendor-neutral intent into a provider-specific representation while preserving semantic equivalence.

The exact renderer input contract remains open.

### Supporting: Resolve Technical Access

Retain Technical-to-Domain Access Resolution as an APR supporting capability for business attribution/explanation of technical access regions.

### Future direction: Policy Optimization

Industry practice shows a natural future capability around redundant, shadowed, overly broad and unused policy material.

This is not required to lock the first APR target model and should not be mixed into core reconciliation until its own invariants and product use cases are accepted.

## Data-local computation direction

The expected scale changes the implementation assumptions.

A target design should prefer a shape similar to:

```text
APR application use case
        |
        v
APR semantic computation port
        |
        v
PostgreSQL-backed / other data-local engine
        |
        +-- required effective-policy projection
        +-- configured effective-policy projection
        +-- exact comparison/index/workset
        |
        v
small assessment result / delta reference
```

The application process should normally receive:

- target/snapshot references;
- realization status;
- counts/measures where useful;
- delta/workset reference;
- requested pages/fragments for UI, explanation or rendering.

It should not need the complete policy on every call.

### PostgreSQL as the first implementation candidate

PostgreSQL is a reasonable first implementation candidate when both policy sides are already represented as canonical effective technical regions that support exact relational/range operations.

The design must remain open to another engine if ordered ACL semantics, deny/default behavior, nested policy objects, NAT-dependent semantics or other constructs make a specialized symbolic representation materially safer or more efficient.

The decision gate is semantic correctness and scale, not preference for SQL or in-memory objects.

## Cross-context data boundary direction

APR needs fast access to upstream facts without coupling itself to peer persistence internals.

The next design pass should evaluate explicit APR-facing projections/contracts such as conceptual:

```text
required effective-policy projection
configured effective-policy projection
target-to-policy correlation projection
```

Names and physical schemas are intentionally not fixed here.

Rules for the design:

1. the owner bounded context defines the meaning of the published projection;
2. APR consumes only the published contract;
3. direct peer private-table navigation is not the integration model;
4. projections may be physically co-located for performance;
5. derived/indexed copies must carry freshness/snapshot/provenance semantics;
6. no cross-context database foreign key may imply a hidden shared aggregate.

## Current repository implications to review later

The following are known target-vs-current tensions. They are recorded here so the next design work does not accidentally preserve them as requirements.

### I20 placement semantics are too deep inside APR

Current I20 derives desired enforcement intent by consuming and classifying NEP placement outcomes. The target direction instead treats target selection as upstream responsibility and gives APR target-specific policy input.

Later work must review and likely supersede:

- `PlacementStatus` in APR;
- `EnforcementPlacementPort` / equivalent APR placement selection ports;
- `NoEnforcement` / `NoForwardingPath` handling inside APR desired-policy derivation;
- APR-side placement ambiguity semantics.

### Current reconciliation object graphs assume application-side materialization

Current ports and use cases load desired/configured projections into the application process and then reconcile domain objects.

The target direction requires a data-local semantic engine for large sets. The final migration plan must distinguish small-value domain types from large policy-space representations that should stay in an indexed/data-local form.

### Current `Add | Remove | Replace | No-op` is not a complete change-design model

The current enum remains useful as a compact classification of semantic delta, but it must not be mistaken for a concrete policy edit plan.

### Current renderer consumes desired policy rather than an explicit change design

The target design must revisit whether rendering should consume:

- full desired target policy;
- verified policy change design;
- or both as explicit modes.

### I18 should be preserved but its coupling to reconciliation must be reviewed

The exact technical-region algebra and Technical-to-Domain Resolution remain valuable.

The next design pass must decide which parts form the shared APR mathematical kernel and whether complete domain attribution is a prerequisite for purely technical policy equivalence.

## Explicit non-goals of this framing pass

This document does not yet define:

- final APR aggregate roots;
- final canonical ERD;
- final table/view/materialized-view layout;
- final `PolicySemanticEngine` interface;
- PostgreSQL range/index strategy;
- BDD/FDD/atomic-predicate adoption;
- exact ownership of provider-to-effective-policy normalization;
- final change-operation vocabulary;
- approval/edit lifecycle for change plans;
- final renderer input contract;
- migration patches to current APR code;
- public API/UI design.

Those items belong to the next design additions on this branch.

## Next design work

Continue on this branch by resolving, in order:

1. exact APR boundary and cross-context contracts;
2. target-specific required-policy input contract;
3. configured effective-policy/completeness contract;
4. canonical policy-space domain abstraction and supported first algebra;
5. `Assess -> Reconcile -> Design -> Verify -> Render` use-case contracts;
6. data-local semantic-engine boundary and first PostgreSQL representation;
7. derived-workset/persistence policy;
8. final Tactical DDD and PlantUML ERD;
9. target-vs-current gap report;
10. ADR(s) superseding old I20/I21 decisions where necessary;
11. implementation migration roadmap only after the target model is accepted.

## Completion gate for this branch phase

The requirements-framing phase is complete when the repository clearly states that:

```text
APR owns effective-policy realization/reconciliation/change semantics
!= NEP target-selection semantics
!= raw vendor policy representation
!= NEO execution mechanics
```

and the next design work can proceed without treating the current I20 application structure as the target architecture.
