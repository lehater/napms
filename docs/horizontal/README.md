# Full-width documentation reconstruction — S0 through strategic S2

Status: COMPLETE / REVIEWED / non-canonical / documentation-only.

## Scope

This horizontal pass reconstructs the entire product/problem space represented by accepted current documentation under `docs/**`, from problem framing through requirements and strategic DDD.

It is intentionally wider than the selected implementation MVP. It includes:

- current target behavior;
- current as-built behavior that remains required to reconstruct the designed system;
- accepted future/deferred problem areas and extensions described in current `docs/**`;
- non-peer compositions and integration/application capabilities where they are part of the documented problem/capability landscape.

It does not promote every capability to a Bounded Context and does not treat implementation as a design source.

## Source authority

Only accepted current documentation under `docs/**` is product/project design truth for this pass. Product code and tests are stale and excluded from design reconstruction.

Where documents disagree:

1. explicit current target/revalidated statements override as-built/legacy compatibility statements for target design;
2. earlier-stage semantic truth constrains later-stage artifacts;
3. an explicit superseding statement overrides the superseded statement;
4. unresolved material contradictions require a product/domain decision rather than implementation inspection.

No unresolved material contradiction remains in the reviewed horizontal candidate.

## Stage boundary

This pass stops after strategic S2:

- S0 — problem, actors/outcomes, evidence and externally imposed/non-negotiable constraints;
- S1 — solution-agnostic functional/quality requirements and acceptance intent across the whole documented problem space;
- S2 strategic — capabilities, Bounded Context boundaries, semantic ownership, context relationships and ubiquitous strategic language.

Tactical domain models, S3 architecture/contracts and S4 implementation planning are downstream and are not reconstructed by this horizontal pass.

## Candidate artifact set

```text
docs-v2/horizontal/
  README.md
  source-ledger.md
  traceability.yaml
  validation-review.md
  s0/
    problem-landscape.md
    user-journeys.md
  s1/
    capability-requirements.md
    quality-requirements.md
    acceptance.md
    glossary.md
  s2/
    strategic-model.md
    context-map.puml
```

The source ledger accounts for accepted `docs/**` source families and their routing/supersession. Traceability connects problem areas to functional/quality/acceptance evidence and strategic ownership/disposition. The validation review records documentation-level V0-V2 results and V3 readiness without declaring canonical gates passed.

## Current strategic baseline

The accepted target baseline identifies ten peer Bounded Contexts:

1. Business Connectivity
2. Access Policy
3. Authority Management
4. Resource Catalogue
5. Application Communication Catalogue
6. Application Deployment
7. Network Enforcement Placement
8. Technical Access Evidence
9. Access Policy Realization
10. Network Environment Operations

Non-peer owner-preserving compositions include Vendor-Neutral Policy Export, Required Policy Materialization, Evidence Access Recognition, Scoped Connectivity Inventory, Checker / Traffic Analysis and Connectivity Impact Analysis. Provider Policy Interpreter, Provider Policy Renderer, technical-evidence acquisition and enterprise-source integration remain integration/application capabilities.

Two distinct policy projections are preserved:

```text
Vendor-Neutral Policy Export = AP + ACC + AD + RC
Required Policy Materialization = AP + ACC + AD + RC + NEP
```

The first is a complete vendor-neutral effective-policy projection and has no NEP dependency. The second is enforcement/realization materialization producing target-required policy for reconciliation.

## Revalidated semantic baseline

- ACC Interaction endpoints are Components; immutable Interaction Contract Revisions carry traffic semantics.
- AD owns concrete ComponentDeployment identity as ComponentRef -> ResourceRef.
- AP PolicyRule governs one directed concrete ComponentDeployment pair using an exact ACC revision and validates endpoint compatibility.
- RC current target has at most one effective AddressSpace at a logical time, exactly HostAddress or Prefix when present.
- Evidence, recognition, business need, policy proposal/acceptance, materialization, realization, execution and verification remain distinct kinds of truth.
- Execution success is not convergence verification.
- No Shared Kernel is accepted among peer Bounded Contexts.

## Reconstruction rule

All documented problem areas were inventoried, but stage/type is determined by semantic content rather than legacy file location. Future/deferred material is retained with an explicit maturity/disposition marker rather than silently discarded or promoted to MVP behavior.

## Completion and lifecycle state

The requested horizontal reconstruction is complete as a **non-canonical docs-v2 candidate**. Documentation-level review is recorded in `validation-review.md`.

This status does not mean canonical G0/G1/G2 gates have been accepted, does not authorize canonical `docs/**` cutover, and does not authorize tactical S2, S3, S4 or implementation work. Those are separate lifecycle actions.
