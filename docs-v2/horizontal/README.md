# Full-width documentation reconstruction — S0 through strategic S2

Status: IN PROGRESS / non-canonical / documentation-only.

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

## Stage boundary

This pass stops after strategic S2:

- S0 — problem, actors/outcomes, evidence and externally imposed/non-negotiable constraints;
- S1 — solution-agnostic functional/quality requirements and acceptance intent across the whole documented problem space;
- S2 strategic — capabilities, Bounded Context boundaries, semantic ownership, context relationships and ubiquitous strategic language.

Tactical domain models, S3 architecture/contracts and S4 implementation planning are downstream and are not reconstructed by this horizontal pass unless needed only as source evidence for routing upstream truth.

## Current strategic baseline

The accepted target baseline currently identifies ten peer Bounded Contexts:

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

Required Policy Materialization and Evidence Access Recognition remain non-peer compositions. Provider Policy Interpreter, Provider Policy Renderer and technical-evidence acquisition remain integration/application capabilities. Scoped Connectivity Inventory and Connectivity Impact Analysis remain compositions/analysis capabilities unless the documentation provides a later explicit ownership decision.

## Reconstruction rule

All documented problem areas are inventoried, but stage/type is determined by semantic content rather than by the legacy file location. Future/deferred material is retained with an explicit maturity/disposition marker rather than silently discarded or promoted to MVP behavior.
