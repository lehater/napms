# Walking Skeleton engineering readiness — PLAN-028 WP-05

Status: `accepted G4 engineering baseline with prototype replacement guardrail`.

Date: 2026-09-08.

## Repository/module path

Use `apps/api` as reusable Python/FastAPI engineering scaffolding only. Existing `AccessRequestService` code/models/database semantics are prototype evidence and must not be incrementally treated as target domain. Replace/restructure target source around the accepted modular architecture.

Recommended target package shape inside the API application:

```text
src/napm/
  access_policy/        # domain + application-owned policy semantics
  application/          # use cases/orchestration
  ports/                # authority/catalogue/decision/persistence abstractions
  adapters/http/        # FastAPI
  adapters/persistence/ # relational repository/UoW
  adapters/integration/ # fake/manual/enterprise/Legacy adapters
```

Dependency rule: domain -> no framework/adapters; application -> domain + ports; adapters -> application/ports/domain as required.

## Build/package/local workflow

Retain Python >=3.10 + setuptools/pytest/FastAPI toolchain initially because it already provides a runnable/testable repository path and no accepted architecture driver requires a language/framework change. Rename package/product semantics away from historical AccessRequestService during implementation.

Required local path:
- install editable dev dependencies;
- run unit/component tests without external MSSQL;
- run persistence integration tests against the selected relational test engine/container;
- run FastAPI locally with fake/manual dependency adapters by configuration.

## Persistence

First skeleton requires relational transactional uniqueness. Do not adopt existing MSSQL schema/procedures as target model. PLAN implementation may choose a lightweight local relational engine for fast tests plus a deployment relational engine, provided concurrency semantics are validated against the real deployment engine before production readiness.

## Test gates

Minimum pre-merge implementation gates:
- domain/application unit/component tests;
- persistence integration test including duplicate/concurrent materialization;
- HTTP acceptance tests from `walking-skeleton-acceptance-pack.md`;
- module dependency/import rule;
- formatting/lint/type/security checks selected when implementation dependencies are finalized.

Existing `make api-test` can be evolved rather than preserving historical test semantics.

## CI

CI must install the target API package and execute the above deterministic checks. Harness `make agent-check` remains scoped to Harness/process/DDD-gate changes and is not a substitute for product-code tests.

## Configuration/secrets

- dependency adapter selection and connection strings through environment/configuration;
- no secrets committed;
- fake/manual adapters available for local/acceptance runs;
- production credentials supplied by deployment environment/secret facility; concrete platform is not yet a domain/architecture requirement.

## Deploy/run

First production-shaped unit is one NAPM API application plus its authoritative relational persistence and configured external adapters. Container/process technology may follow existing repository infrastructure where suitable; no additional service topology is required for the skeleton.

## Observability

At minimum log/measure with correlation identifiers:
- proposal command/request ID;
- canonical semantic identity correlation (avoid leaking unnecessary sensitive detail);
- authority/catalogue/decision dependency outcome category;
- materialization created/resolved/NotAllowed/failure outcome;
- RuleId on successful authoritative resolution;
- latency/error counters by use case/dependency.

Never log secrets; address/topology details should be minimized according to operational need.

## Bootstrap

Skeleton test/demo requires only:
- fake authority assignment allowing/denying a known actor/scope;
- fake catalogue containing one valid Source/Destination/DCS interaction plus invalid case;
- fake/manual decision adapter returning exact Allowed/NotAllowed/mismatch/unknown cases;
- empty target Access Policy store.

No Legacy data migration is required to prove the first skeleton.

## Readiness result

The repository has sufficient Python/API/test scaffolding to begin the target implementation without a platform-first project. Existing prototype domain/database code must be replaced or isolated rather than treated as accepted target semantics.