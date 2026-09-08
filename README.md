# NAPMS

**Network Access Policy Management System**

This is the authoritative greenfield product repository for NAPMS.

## Repository boundary

This repository contains current product requirements, living DDD models, architecture decisions, engineering policies, production-target code and tests.

It intentionally does **not** contain Legacy implementation, reverse-engineering evidence, old prototypes or reconstruction workflow artifacts. Historical material may inform problem framing only; it is not an implementation dependency of NAPMS.

## Current implementation state

Wave 1 is implementation-ready through I7: Access Policy semantics, PostgreSQL persistence, Authority Management, Application Communication Catalogue, Resource Catalogue, coherent Export Snapshot, vendor-neutral normalization and a local-dev greenfield PostgreSQL end-to-end proof have passed their gates.

The active plan owns selection of the first concrete consumer/runtime boundary. HTTP/CLI/public serialization are not assumed before that consumer is selected.

## Layout

```text
src/napms/                 product code
tests/                     executable specifications and architecture tests
docs/domain/               living DDD model
docs/requirements/         accepted product requirements
docs/architecture/         target architecture
docs/decisions/            ADRs
docs/engineering/          implementation and engineering policies
docs/baseline/             accepted readiness/provenance snapshots
```

## Development

```bash
python -m pip install -e ".[dev]"
make test
```

PostgreSQL integration tests use the optional `postgres` extra and `make postgres-test`.

See `AGENTS.md` and `docs/README.md` before changing domain or architecture semantics.
