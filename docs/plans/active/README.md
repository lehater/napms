# Active execution

Current: `PLAN-target-code-structure-migration.md`.
Selected next stage: M1 — Repository backend boundary.

## Working set

- Decision: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.
- Canonical target: `docs/architecture/code-structure.md`.
- Long-range roadmap: `docs/engineering/target-code-structure-migration-roadmap.md`.
- Active plan: `docs/plans/active/PLAN-target-code-structure-migration.md`.
- Current implementation baseline: `docs/architecture/current-architecture.md`.

## Blockers

None.

## Gate

M1 is behavior-preserving repository movement. Required evidence is defined in the active plan: backend/core, harness, knowledge, affected Docker/integration checks and final hosted PR gates.

## Next

Execute M1 exactly as defined in `PLAN-target-code-structure-migration.md`. Do not start M2 semantic-module moves in the same stage.
