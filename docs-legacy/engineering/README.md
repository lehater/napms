# Engineering contracts

This directory contains current engineering contracts required to reproduce and operate the designed system. Implemented contracts remain here while they define current behavior; they are not execution history.

## As-built reconstruction contracts

- `current-state.md` — implemented capability/runtime inventory and compatibility boundaries.
- `http-api-contract.md` — implemented HTTP/session/error/query/mutation contract for the product surface.
- `application-catalogue-target-http-contract.md` — implemented Application Catalogue HTTP contract.
- `catalogue-curation-http-api-contract.md` — implemented catalogue curation transport contract.
- `catalogue-curation-command-contract.md` — implemented mutation/idempotency/concurrency contract.
- `i2-persistence-engine-decision.md` — PostgreSQL persistence/concurrency decision required by the current design.
- `local-product-operator-runbook.md` — supported local product/operator path.

## Current cross-cutting runtime contracts

- `configuration.md` — configuration/secrets/runtime input contract.
- `dependency-injection.md` — composition and dependency wiring rules.
- `error-model.md` — application/adapter/public error semantics.
- `local-docker-runtime.md` — supported local deployment topology.
- `local-backup-recovery.md` — backup/recovery contract.
- `local-upgrade-procedure.md` — upgrade/migration execution contract.
- `observability.md` — logging/diagnostic/health contract.

Completed migration/refactoring roadmaps, hardening review snapshots and problem-history registries are not current engineering contracts and belong in Git history.

When an as-built contract differs from current target domain/architecture, preserve both and label the difference; do not erase the implemented contract or let it override target semantics.
