# NAPMS

**Network Access Policy Management System**

This is the authoritative greenfield product repository for NAPMS.

## Repository boundary

This repository contains current product requirements, living DDD models, architecture decisions, engineering policies, production-target code and tests.

It intentionally does **not** contain Legacy implementation, reverse-engineering evidence, old prototypes or reconstruction workflow artifacts. Those remain in `lehater/sssr_xlam`.

## Current implementation state

Wave 1 is implementation-ready. I1 Access Policy materialization core, I2 PostgreSQL persistence proof and I3 authorized Active/Inactive mutation have passed their gates. The active plan owns the next inside-out behavior increment.

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

PostgreSQL integration proof uses the optional `postgres` extra and `make postgres-test`.

See `AGENTS.md` and `docs/README.md` before changing domain or architecture semantics.
