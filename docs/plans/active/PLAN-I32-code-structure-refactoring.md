# I32 Code Structure Refactoring

Status: `active`

Date: 2026-09-11.

## Goal

Align physical code ownership with the accepted context-first Clean/Hexagonal architecture so humans and agents can locate changes from their semantic owner, without changing product/domain semantics.

## Inputs

Canonical architecture and execution inputs:
- `docs/architecture/current-architecture.md`;
- `docs/architecture/code-structure.md`;
- `docs/engineering/current-state.md`;
- `docs/engineering/code-structure-refactoring-roadmap.md`;
- `AGENTS.md`, `src/AGENTS.md`, `web/AGENTS.md`;
- `docs/process/working-loop.md`.

## WP-0 — structure contract

Outcome: completed and integrated through PR #64. The repository has a canonical context-first / layers-second code-structure contract and ordered I32 roadmap.

## WP-1 — backend structural migration

Outcome: completed and squash-integrated through PR #65 (`a90b866`). M1-M4 moved feature HTTP beside semantic owners, reduced active runtime HTTP to process assembly, and established `napms.bootstrap` as the executable composition root. Final Core, Harness, PostgreSQL, Docker runtime and browser journey gates were green.

## WP-2 — demonstrated backend granularity

Responsibility: execute M5 only where post-WP-1 evidence shows unrelated use cases still share an editing/search context.

Outcome: completed in PR #66 as one evidence-driven pilot.
- `structure_curation.py` mixed Application mutation/lifecycle use cases with Component mutation/lifecycle use cases.
- implementation is now split into `application_structure_curation.py` and `component_structure_curation.py`;
- genuinely shared outcome/authority/fingerprint plumbing lives in `curation_mutation.py`;
- `structure_curation.py` is a small compatibility-export facade so unrelated callers do not need churn in the same increment;
- an architecture test prevents use-case implementation from returning to the shared facade;
- Core, PostgreSQL, Harness and browser journey gates were green on the implementation head.

M5 stop condition was evaluated against the other prominent ACC candidates. `deployment_curation.py` is cohesive around Component Deployment lifecycle; `binding_curation.py` is cohesive around Deployment↔Resource binding lifecycle. File size alone is not evidence for another split, so no second backend hotspot is selected.

M6 Web locality remains separate.

## Exit criteria

WP-2 exits when the selected split reduces mixed-responsibility editing/search context, preserves domain/API/persistence/authority/concurrency/idempotency behavior, has executable locality protection, and applicable Core/PostgreSQL/Harness/browser gates pass. These criteria are satisfied by PR #66.

I32 remains open only for a separately selected M6 Web-locality increment if current Web evidence shows a similarly useful locality improvement.

## Blockers

None known.

## Next

Finalize and squash-integrate PR #66. After integration, evaluate M6 against current Web structure; select a Web pilot only when a concrete feature change still requires crossing root/shared files because of misplaced responsibility rather than file size alone.
