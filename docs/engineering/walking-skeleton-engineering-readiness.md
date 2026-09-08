# Walking Skeleton engineering readiness

Status: `accepted pre-infrastructure engineering baseline`.

Date: 2026-09-08.

## Repository/module path

The product package is:

```text
src/napms/
  access_policy/
    domain/
    application/
```

I1 contains Domain + Application + consuming ports only. Infrastructure/adapters are intentionally absent until the I1 core gate passes.

Dependency rule: Domain has no outward dependencies; Application depends on Domain + owned port abstractions; future adapters depend inward.

## Build/package/local workflow

Current minimum:
- Python >=3.10;
- setuptools;
- pytest;
- editable local install;
- deterministic core/architecture tests without external services.

No FastAPI, ORM, SQL driver or external SDK is required by I1.

## I1 test gate

Before infrastructure:
- complete Access Policy core behavior matrix;
- architecture/import rules;
- error/message model accepted;
- observability policy accepted;
- configuration model accepted;
- dependency-injection/composition model accepted;
- no open P0/P1 semantic or structural issue;
- successful full test execution.

In-memory repository tests prove semantic idempotency only. Production concurrency/transaction semantics are not claimed until I2.

## Post-I1 infrastructure proof

Only after I1 PASS may I2 add:
- relational repository/UoW;
- schema/migrations and authoritative unique constraint;
- real concurrency/rollback tests;
- an HTTP adapter if still selected;
- external Authority/Catalogue/Decision adapters in later increments.

Infrastructure must adapt to the accepted ports/core semantics.

## Configuration/secrets

The central typed configuration model is defined in `configuration.md`. Domain/Application never read environment variables, files or secrets directly.

## DI/composition

Constructor injection is the core rule. A production composition root is introduced when concrete runtime adapters exist. No container/service locator may leak into Domain/Application.

## Observability

The logging/observability contract is defined in `observability.md`. Business audit/provenance remains domain truth and is not replaced by operational logs.

## Bootstrap data

I1 tests use only explicit fakes/in-memory implementations:
- permitted/denied/unknown authority;
- valid/invalid/unknown directed interaction;
- exact Allowed/NotAllowed/Unknown/mismatch decision;
- empty/in-memory Access Rule repository.

No Legacy migration or infrastructure is required to prove I1.

## Readiness result

The clean NAPMS repository is sufficient for domain/application-first implementation. Infrastructure remains intentionally gated behind successful I1 proof.
