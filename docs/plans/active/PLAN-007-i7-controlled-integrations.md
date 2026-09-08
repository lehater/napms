# PLAN-007 — I7 first controlled real/transitional integrations

Status: `active`

## Goal

Replace the minimum fake/local boundaries with real, manual or transitional adapters for one explicitly selected controlled environment, proving end-to-end Wave-1 semantics through normalized vendor-neutral export without changing accepted domain/application meaning.

I7 stops before vendor/device rendering, configured-state reconciliation, provider/device execution and broad production rollout.

## Current stage

Owner decision packet prepared from target transition architecture plus concrete `lehater/sssr_xlam` implementation evidence.

The legacy repository contains a reproducible SQL Server 2022 Developer container, schema initialization for `SSSR`, `pobeda` and `ProductTest`, a pyodbc adapter, and legacy tables relating applications/roles/protocol-port semantics/resources/IP ranges. It does not provide a trustworthy direct target ComponentDeployment UUID mapping or the target action/scope Authority model. The recommended first controlled proof therefore combines real transitional MSSQL catalogue/resource reads with explicit manual bridges where semantic equivalence cannot be proven.

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

- semantic owners remain Authority Management, Access Policy, Application Communication Catalogue, Resource Catalogue and deferred Connectivity Decision Domain;
- adapters translate source-specific identities/data into accepted port contracts; source schemas do not become domain meaning;
- unknown/missing/stale authority/catalogue/decision facts fail closed;
- exact RuleSemanticIdentity and ResourceReference correlation is mandatory;
- coherent Export Snapshot requires one logical `asOf` plus source identity/version/effective-validity evidence or an equivalent adapter-owned capture mechanism;
- ComponentDeployment -> Resource-reference binding is ACC-owned;
- Resource/Endpoint realization is RC-owned;
- DCS payload decoding must yield accepted `DcsTrafficAlternative` semantics without vendor-specific leakage;
- normalized rows perform no live post-snapshot owner lookup;
- source provenance must remain attributable through normalized output;
- direct cross-module/source database shortcuts are prohibited;
- HTTP/CLI/serialization are adapters/interface choices, not domain semantics.

## Decision gates before implementation

### D1 — First controlled environment

Record:
- deployment/runtime boundary;
- intended users/operators;
- controlled data scope;
- whether the environment is local/dev, test/staging, pilot or another explicitly bounded target;
- acceptable manual/transitional steps.

Do not infer production topology from the current PostgreSQL CI proof.

### D2 — Source/adapter mapping

For the selected environment, identify the concrete source or accepted manual bridge for each boundary actually required by the end-to-end slice:

- AuthorityPort;
- proposal CommunicationCataloguePort;
- ConnectivityDecisionPort;
- ApplicationCommunicationProjectionPort;
- ResourceCatalogueProjectionPort;
- DcsProjectionDecoder.

For each source record:
- authority/ownership basis;
- identity correlation;
- temporal/version evidence available;
- unavailable/unknown behavior;
- source provenance reference;
- credentials/configuration needs;
- whether adapter is permanent, transitional or manual.

A boundary may remain fake only if the selected controlled proof explicitly excludes that part; such exclusion must be stated rather than hidden.

### D3 — End-to-end trigger and handoff

Select only what the controlled proof needs:
- invocation surface: direct application composition, CLI, HTTP or another explicit adapter;
- normalized export serialization/handoff format if an artifact is required;
- controlled storage/delivery location if applicable.

Do not add an HTTP service or CSV/XLSX/JSON serializer merely because it is conventional.

### D4 — Temporal snapshot feasibility

For ACC/RC sources used by the controlled proof, establish one credible mechanism for logical-as-of coherence:
- source-native temporal/version query;
- immutable source version token;
- adapter-owned capture/version;
- or another explicit equivalent.

If no credible mechanism exists, reopen ADR-002 implementation mechanism rather than weakening snapshot semantics.

## Work packages

1. Resolve D1-D4 and record the selected controlled environment/source map.
2. Add configuration/DI only for admitted adapters; fail startup on required missing/invalid config.
3. Implement the minimum anti-corruption adapters one boundary at a time with contract/integration tests.
4. Add the concrete DCS payload codec only for the selected ACC representation.
5. Add invocation/serialization adapters only if selected by D3.
6. Prove end-to-end happy path plus denied/unknown/missing/stale/correlation-mismatch failure paths for the controlled scope.
7. Verify no source-specific semantics leak into Domain/Application and no cross-owner persistence shortcuts appear.
8. Record I7 PASS only for the explicitly selected controlled scope/environment.

## Exit criteria

- controlled environment/scope is named and bounded;
- every admitted external/manual source is mapped to an accepted port with ownership/provenance documented;
- temporal/as-of evidence mechanism is credible for all facts used in successful snapshot/export;
- required configuration and credentials are explicit and fail closed;
- adapter contract/integration tests cover success and material degraded cases;
- concrete DCS payload codec preserves accepted I6 traffic semantics;
- end-to-end controlled proof produces a complete normalized export without live post-snapshot lookups;
- no P0/P1 authority, correlation, temporal, provenance, security or architecture finding remains;
- transition/manual adapters carry retirement/revisit criteria;
- I7 result clearly states its environment/scope and does not overclaim broader production readiness.

## Candidate evidence

Transition evidence from `lehater/sssr_xlam`:

- `docs/target/wave1-transition-architecture.md` explicitly allows Legacy SQL catalogue/resource facts behind anti-corruption adapters and a manual/external exact-subject Connectivity Decision bridge;
- `infra/db/docker-compose.yml` provides SQL Server 2022 Developer;
- `infra/db/devops/db/init-db.sh` initializes `sssr.sql`, `pobeda.sql` and `ProductTest.sql`;
- `apps/api/src/db_mssql.py` proves a working pyodbc/DSN integration style;
- `artifacts/sql/sssr.sql` contains legacy application-role relations, protocol/port rows, resources and resource-IP-range relations.

Important non-equivalences:
- legacy AppRole/AppRoleRelation identity is not automatically target ComponentDeployment/DCS revision identity;
- legacy approver/resource data is not automatically target Authority Management action/scope/effective-time truth;
- legacy current tables do not establish general historical temporal queries for arbitrary target `asOf`.

## Recommended controlled I7 decision packet

### R1 / D1 — local transitional integration lab

Select a **local/dev controlled integration lab**, not staging/pilot/production.

Runtime:
- NAPMS PostgreSQL as already proven;
- SQL Server 2022 Developer initialized from the legacy repository's `SSSR/pobeda/ProductTest` scripts;
- pytest/application composition as the operator surface.

Scope:
- one deliberately small seeded catalogue slice;
- one target source ComponentDeployment + one target destination ComponentDeployment + one immutable target DCS revision;
- one-or-more mapped source/destination Resources/IP realizations sufficient to exercise expansion;
- no live enterprise credentials;
- no device/rendering/execution path.

The proof claims only semantic/adaptor compatibility with the seeded transitional schema.

### R2 / D2 — source/adapter mapping

| Target boundary | Controlled source | Treatment |
|---|---|---|
| `AuthorityPort` | explicit manual lab authority manifest | manual adapter; exact actor/action/RuleGovernanceScope/effective validity + provenance; do **not** infer from legacy approvers |
| proposal `CommunicationCataloguePort` | manual target-to-legacy mapping manifest + seeded legacy MSSQL catalogue facts | transitional ACC adapter; mapping explicitly binds target ComponentDeployment/DCS UUIDs to selected legacy role/relation keys; mismatch/absence = Unknown/Invalid |
| `ConnectivityDecisionPort` | explicit manual exact-subject decision manifest | manual bridge emitting Allowed/NotAllowed + stable lab reference; no invented decision internals |
| `ApplicationCommunicationProjectionPort` | same mapping manifest + seeded legacy MSSQL app-role/protocol-port/resource relations | transitional ACC projection adapter; returns target ResourceReferences + captured DCS payload/provenance |
| `ResourceCatalogueProjectionPort` | seeded legacy MSSQL `resources/resourcesipranges/ipranges` facts | transitional RC adapter; target ResourceReference is mapped explicitly, legacy IDs do not escape as target identity |
| `DcsProjectionDecoder` | versioned transitional payload emitted by the ACC adapter | local codec translating protocol/SPS/SPE/DPS/DPE into accepted I6 alternatives |

The mapping manifests are controlled transition evidence, not new target semantic owners. Every mapping entry carries an explicit stable lab reference and legacy source key.

### R3 / D3 — direct application trigger, no serializer yet

Use direct application composition from the integration test/harness.

The proof result is the in-memory `SuccessfulNormalizedPolicyExport`.

Do not add HTTP/CLI/CSV/XLSX/JSON export delivery in this increment. A public handoff format remains a separate decision when a consumer exists.

The internal ACC-to-decoder payload may use a small versioned deterministic codec solely between the two transitional adapters; that encoding is not the Normalized Policy Export serialization contract.

### R4 / D4 — immutable seeded-run capture

For the first lab proof, do not claim historical MSSQL temporal capability.

Instead:
- initialize a deterministic seeded legacy dataset before each integration run;
- prohibit mutations to the seeded source dataset during one proof attempt;
- assign the dataset/capture a stable run provenance reference;
- choose the logical export `asOf` inside the known validity of that immutable seeded dataset;
- ACC and RC adapters return the same capture/version reference for facts used in that run;
- any requested `asOf` outside the seeded fixture's declared validity fails closed.

This is an adapter-owned capture/version mechanism acceptable under ADR-002 **only for the controlled lab**. It makes no claim that live Legacy MSSQL supports arbitrary historical as-of queries.

## Retirement/revisit rules for recommended manual/transitional pieces

- manual Authority manifest retires when a durable Authority Management provider/process is selected;
- manual Connectivity Decision manifest retires when a durable Decision provider/process exists;
- target-to-legacy identity mapping retires when authoritative target/enterprise catalogue identities are available;
- legacy MSSQL ACC/RC adapters retire when authoritative enterprise/target catalogue sources satisfy the same contracts;
- seeded-run temporal mechanism must be replaced/revalidated before any live mutable-source pilot.

## Blockers

Owner acceptance of R1-R4 is required before I7 adapter implementation.

Do not implement real/transitional adapters until this controlled scope/source map is accepted.

## Validation

- core regression: `make test`;
- existing PostgreSQL proof: `make postgres-test` when relevant changes touch Access Policy persistence;
- harness/process changes: `make harness-check`;
- source adapter integration tests: exact commands/gates must be defined with each selected adapter;
- final candidate: `make check` plus every admitted adapter integration gate.

## Next

I8 — controlled coexistence/cutover proof for the selected I7 environment, including observable success/failure and rollback routing, still without vendor/device mutation.
