# PLAN-007 — I7 first controlled real/transitional integrations

Status: `active`

## Goal

Replace the minimum fake/local boundaries with real, manual or transitional adapters for one explicitly selected controlled environment, proving end-to-end Wave-1 semantics through normalized vendor-neutral export without changing accepted domain/application meaning.

I7 stops before vendor/device rendering, configured-state reconciliation, provider/device execution and broad production rollout.

## Current stage

Environment/source decision gate before implementation.

Repository truth does not currently identify the first controlled environment, authoritative enterprise sources, transitional/manual bridges, concrete DCS payload encoding, or output serialization/handoff format. These must be selected explicitly before real adapter code.

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

## Blockers

D1-D4 are unresolved because the repository contains no accepted first controlled environment/source map.

Do not implement real adapters until those decisions are recorded.

## Validation

- core regression: `make test`;
- existing PostgreSQL proof: `make postgres-test` when relevant changes touch Access Policy persistence;
- harness/process changes: `make harness-check`;
- source adapter integration tests: exact commands/gates must be defined with each selected adapter;
- final candidate: `make check` plus every admitted adapter integration gate.

## Next

I8 — controlled coexistence/cutover proof for the selected I7 environment, including observable success/failure and rollback routing, still without vendor/device mutation.
