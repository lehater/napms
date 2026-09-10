# Active execution

Current: `PLAN-I31-application-catalogue-target-migration.md`

Goal: migrate the PR #57 Application Catalogue target end to end without rewriting existing downstream semantic identities or historical policy truth.

Current task: WP-0 close the target/migration contract before implementation.

## Working set

Read first:
- `docs/decisions/ADR-012-application-definition-deployment-model.md`
- `docs/engineering/application-catalogue-target-migration-roadmap.md`
- `docs/domain/application-communication-catalogue/README.md`

Expand only when required into the current ACC Tactical DDD, ADR-011, downstream `DirectedInteractionIdentity` consumers, API/Web code named by the plan, and `docs/process/decision-protocol.md`.

## Blockers

- P0 semantic choices remain open: downstream compatibility projection; Interaction Definition edit/snapshot semantics; ownership/value semantics for Definition/Component metadata and Deployment Company/Environment/Scope context; active-reference retirement dependencies.

## Gate

Implementation gate is closed. WP-0 exits only when the blocking choices are canonicalized in their owning domain/requirements/architecture/ADR/API artifacts and the resulting migration design preserves existing downstream identity/history. Run the applicable knowledge and harness checks before integrating the stage.

## Next

Resolve the compatibility projection first, then the missing target metadata/context semantics and interaction edit/retirement rules. Do not begin persistence/API/Web implementation until WP-0 closes.
