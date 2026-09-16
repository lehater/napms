# Current design decisions

This directory contains ADRs that are still required to reconstruct or safely evolve the current NAPMS design. It is not a supersession archive.

Two decision roles are retained:

- **as-built decision** — explains a consequential architectural/domain/engineering choice embodied by the current implemented system and needed to reproduce it;
- **target decision** — constrains the current accepted target design.

An ADR does not become historical merely because it was implemented. Remove it only when its decision no longer describes either current as-built or current target design and no reconstruction/evolution task needs it.

## Retained as-built / cross-cutting decisions

- `ADR-001-wave1-modular-application.md` — modular application / ports-and-adapters structural choice.
- `ADR-002-wave1-coherent-export-snapshot.md` — coherent logical-as-of export semantics/architecture.
- `ADR-004-system-name-napms.md` — product/system naming boundary.
- `ADR-006-i27-catalogue-identity-and-lifecycle.md` — implemented catalogue identity/lifecycle choices.
- `ADR-007-i27-resource-lifecycle.md` — implemented Resource lifecycle choices.
- `ADR-008-i27-catalogue-mutation-authority.md` — implemented catalogue mutation authority boundary.
- `ADR-009-i27-dcs-authoring.md` — implemented DCS authoring semantics.
- `ADR-010-i27-command-identity-concurrency.md` — implemented command identity/idempotency/concurrency design.
- `ADR-011-i27-external-correlation-reference-input.md` — external correlation-reference semantics.
- `ADR-012-application-definition-deployment-model.md` — implemented Application Definition / Deployment model; as-built only where target semantics have moved on.
- `ADR-013-i31-application-catalogue-compatibility-and-reference-semantics.md` — implemented compatibility/reference design required to reproduce current behavior.
- `ADR-014-target-code-structure-taxonomy.md` — current structural taxonomy decision.

## Retained current target decisions

- `ADR-018-nep-firewall-current-state-candidate-model.md` — current NEP candidate model used by target/current boundaries.
- `ADR-019-business-connectivity-and-access-governance-boundaries.md` — keeps Business Connectivity separate while unifying formal RuleChange decision/current-policy semantics in Access Policy; customer-specific approval workflow is outside the MVP baseline.
- `ADR-020-required-policy-materialization-is-derived-composition.md` — current materialization ownership/composition decision.
- `ADR-021-provider-policy-interpretation-and-rendering-boundaries.md` — current provider interpretation/rendering boundary decision.

Superseded-only ADRs and intermediate alternatives are kept in Git history rather than this directory.
