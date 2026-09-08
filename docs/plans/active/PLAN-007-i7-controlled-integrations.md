# PLAN-007 — I7 first controlled real/transitional integrations

Status: `active`

## Goal

Replace the minimum fake/local boundaries with real, manual or transitional adapters for one explicitly selected controlled environment, proving end-to-end Wave-1 semantics through normalized vendor-neutral export without changing accepted domain/application meaning.

I7 stops before vendor/device rendering, configured-state reconciliation, provider/device execution and broad production rollout.

## Current stage

Greenfield environment/source decision gate before infrastructure implementation.

Legacy is explicitly out of scope for NAPMS implementation. There are no Legacy/MSSQL/transitional source adapters, identity mappings or migration bridges in I7. Historical material may inform problem framing only; it is not an implementation dependency.

The first controlled integration must use the accepted NAPMS modular-monolith/ports-and-adapters architecture and PostgreSQL where relational persistence is required.

## Inputs

Canonical inputs:

- `docs/requirements/wave1-product-requirements.md`;
- `docs/requirements/wave1-semantic-contracts.md`;
- `docs/architecture/wave1-context-definitions.md`;
- `docs/architecture/wave1-data-ownership.md`;
- `docs/architecture/wave1-domain-message-flows.md`;
- `docs/architecture/wave1-threat-model.md`;
- `docs/decisions/ADR-001-modular-monolith-ports-adapters.md`;
- `docs/decisions/ADR-002-wave1-coherent-export-snapshot.md`;
- `docs/engineering/configuration.md`;
- `docs/engineering/dependency-injection.md`;
- current Access Policy + policy_export core and PostgreSQL integration tests.

## Accepted boundaries that adapters must preserve

- semantic owners remain Authority Management, Access Policy, Application Communication Catalogue, Resource Catalogue and Connectivity Decision Domain;
- each module owns its data and exposes semantic ports/contracts rather than cross-module table access;
- PostgreSQL is the relational persistence technology for admitted greenfield infrastructure;
- one PostgreSQL deployment may physically host multiple module-owned schemas, but schema ownership and dependency direction remain explicit;
- unknown/missing/stale authority/catalogue/decision facts fail closed;
- exact RuleSemanticIdentity and ResourceReference correlation is mandatory;
- coherent Export Snapshot requires one logical `asOf` plus source identity/version/effective-validity evidence;
- ComponentDeployment -> Resource-reference binding is ACC-owned;
- Resource/Endpoint realization is RC-owned;
- DCS payload decoding must yield accepted `DcsTrafficAlternative` semantics without vendor-specific leakage;
- normalized rows perform no live post-snapshot owner lookup;
- provenance must remain attributable through normalized output;
- direct cross-module database reads are prohibited;
- HTTP/CLI/serialization are adapter/interface choices, not domain semantics.

## Decision gates before implementation

### D1 — First controlled environment

Select the first greenfield runtime target:
- local/dev integration environment;
- shared test/staging;
- or bounded pilot.

Do not infer production topology from CI.

### D2 — Greenfield module implementation boundary

For each Wave-1 semantic owner required by the end-to-end path, decide whether I7 implements it now as a real NAPMS module or keeps it behind a deterministic test/manual port:

- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- Connectivity Decision Domain.

Any implemented module must own its PostgreSQL schema/repository and expose semantic application ports; no module may read another module's tables directly.

### D3 — Initial greenfield data contracts

For implemented modules, define only the minimum Wave-1 durable model required by accepted contracts:

- Authority Management: actor/action/scope/effective validity/provenance;
- ACC: ComponentDeployment identity, immutable DCS revision, Deployment -> Resource-reference binding, DCS projection semantics/provenance;
- RC: Resource identity, Resource Endpoint/address realization, effective validity/provenance;
- Connectivity Decision: exact RuleSemanticIdentity subject, Allowed|NotAllowed, decision reference/provenance.

Do not broaden these into generic IAM, CMDB, application portfolio or workflow systems.

### D4 — Temporal snapshot mechanism

For ACC/RC PostgreSQL facts, select the greenfield mechanism that proves logical-as-of coherence.

Recommended baseline:
- append-only/versioned fact rows with explicit `valid_from` / `valid_to` half-open validity;
- stable source/fact revision identity;
- queries resolve the fact valid at requested `asOf`;
- no hidden wall-clock fallback.

If a simpler mechanism is selected, it must still satisfy ADR-002 and fail closed outside proven validity.

### D5 — Invocation and output handoff

Select only what the first controlled proof needs:
- direct application composition/integration test;
- CLI;
- HTTP;
- serializer/handoff format.

Do not add interfaces without a concrete consumer.

## Recommended greenfield baseline

Unless owner decisions say otherwise:

1. **Environment:** local/dev controlled integration environment.
2. **Database:** PostgreSQL only.
3. **Physical topology:** one PostgreSQL instance is acceptable initially, with separate module-owned schemas/migrations and no cross-schema reads from application code.
4. **Temporal model:** explicit version/effective-validity rows for ACC/RC facts.
5. **Trigger:** direct application/integration composition first; no HTTP/CLI requirement yet.
6. **Serialization:** defer until a concrete consumer exists.
7. **Legacy:** no implementation dependency whatsoever.

## Work packages

1. Resolve D1-D5 and record the selected greenfield module/source map.
2. Add PostgreSQL schemas/migrations only for modules admitted by D2/D3.
3. Implement one module adapter/repository at a time behind accepted ports.
4. Add configuration/DI only for admitted modules and fail startup on required missing/invalid config.
5. Implement concrete DCS projection encoding/decoder only after ACC durable representation is selected.
6. Prove end-to-end happy path plus denied/unknown/missing/stale/correlation-mismatch failure paths.
7. Verify no cross-module SQL access or source-specific semantics leak into Domain/Application.
8. Record I7 PASS only for the explicitly selected controlled environment/scope.

## Exit criteria

- controlled greenfield environment is named and bounded;
- every implemented Wave-1 semantic owner has explicit data ownership and PostgreSQL schema/repository boundaries;
- no Legacy/MSSQL/transitional dependency exists;
- temporal/as-of evidence mechanism is credible for ACC/RC facts;
- required configuration is explicit and fail closed;
- module contract/integration tests cover success and material degraded cases;
- concrete DCS representation preserves accepted I6 traffic semantics;
- end-to-end proof produces a complete normalized export without live post-snapshot owner lookup;
- no direct cross-module database reads;
- no P0/P1 authority, correlation, temporal, provenance, security or architecture finding remains;
- I7 result clearly states its environment/scope and does not overclaim broader production readiness.

## Blockers

D1-D5 require owner decisions before real module infrastructure is implemented.

## Validation

- core regression: `make test`;
- existing PostgreSQL proof: `make postgres-test` when relevant changes touch Access Policy persistence;
- harness/process changes: `make harness-check`;
- source adapter integration tests: exact commands/gates must be defined with each selected adapter;
- final candidate: `make check` plus every admitted adapter integration gate.

## Next

I8 — controlled coexistence/cutover proof for the selected I7 environment, including observable success/failure and rollback routing, still without vendor/device mutation.
