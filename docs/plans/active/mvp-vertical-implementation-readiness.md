# First MVP vertical — Implementation Readiness

Status: `S4 readiness; Slice 1 evaluated G4 PASS`.

Date: 2026-09-15.

## Accepted upstream basis

- G2 PASS: first MVP semantic vertical.
- G3 PASS: `docs/architecture/first-mvp-vertical-g3-review.md`.
- Architecture: `docs/architecture/first-mvp-vertical.md`.
- MVP behavior: exact comparison, additive-only ENSURE-PERMIT, fail-closed unresolved semantics.

## Implementation strategy

Do not attempt a big-bang migration. Implement the target inside-out in bounded slices. Each later infrastructure slice requires its own applicable G4 lease.

## Slice 1 — target technical-realization core — G4 PASS

### Goal

Create an executable, infrastructure-free target core from a current AP Policy Rule projection through RPM/APR to renderer/NEO ports, proving the first happy path and fail-closed behavior with fakes.

This slice intentionally starts after current semantic authorization exists. It does not implement AG/AP persistence or real owner adapters yet.

### Authorized production scope

Create/modify only:

```text
backend/src/napms/workflows/policy_realization/application/**
backend/src/napms/contexts/access_policy_realization/domain/<new target MVP modules>
backend/src/napms/contexts/access_policy_realization/application/<new target MVP modules>
```

Existing legacy APR modules may be imported only for narrowly verified reusable source-neutral value/algebra code. Do not edit old orchestration/rendering in this slice unless required to extract a pure reusable primitive without changing legacy behavior.

### Authorized test scope

```text
backend/tests/policy_realization/**
backend/tests/access_policy_realization/<new MVP core tests>
backend/tests/architecture/test_dependency_rules.py
backend/tests/architecture/test_access_policy_realization_boundary.py
```

Architecture tests may be extended only to enforce accepted target boundaries introduced by this slice.

### Target contracts to implement

Workflow application values/ports sufficient to express:

- current Policy Rule projection with governed subject/provenance;
- immutable Interaction traffic contract projection;
- Component placement projection;
- Resource realization = HostAddress | Prefix | unresolved;
- NEP candidate result with firewallId/accessListName/freshness;
- TargetRequiredPolicy / unresolved result;
- ConfiguredEffectivePolicySnapshot completeness;
- ProviderRendererPort;
- NetworkOperationPort;
- semantic-basis revalidation port/correlation.

APR target core sufficient to express:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required

Realized | Drift | Uncomparable

VerifiedChangeIntent {
    operation = ENSURE-PERMIT
    permitSpace = selected missing space
    comparisonScope
    baseConfiguredCorrelation
    provenance
}
```

### Core flow behavior

Prove at least:

1. one authorized HostAddress pair + one NEP locator + complete configured snapshot with missing access -> one ENSURE-PERMIT intent -> renderer port -> NEO port;
2. exact equality -> Realized, no renderer/NEO call;
3. excess-only drift -> reported Drift, no renderer/NEO call;
4. Prefix on either side -> RPM unresolved, no APR mutation path;
5. missing/ambiguous placement or Resource realization -> unresolved;
6. candidate with no access-list locator -> unresolved for that affected materialization;
7. configured Incomplete/Unknown/unsupported -> Uncomparable;
8. renderer unsupported/equivalence failure -> no NEO call;
9. semantic-basis revalidation changed/unknown -> no NEO call;
10. multiple candidates/locators remain separate comparison scopes; no arbitrary winner.

### Explicit non-goals

- Access Governance implementation;
- Access Policy target persistence/identity migration;
- PostgreSQL migrations;
- ACC-backed AD compatibility adapter;
- RC compatibility adapter;
- real NEP target query;
- provider interpreter integration;
- concrete provider renderer;
- NEO adaptation/wiring;
- HTTP/UI;
- Prefix-aware NEP;
- removal/narrowing of excess access.

### Migration/data impact

None. No schema or durable state change in Slice 1.

### Required checks

At minimum:

```text
pytest targeted new core tests
pytest backend/tests/architecture/test_dependency_rules.py
pytest backend/tests/architecture/test_access_policy_realization_boundary.py
make harness-check
make knowledge-check
```

Run the broader backend/core gate if available and proportionate after targeted tests are green.

### Completion evidence

Slice 1 is complete when:

- target core contracts compile without importing peer context domains;
- target APR comparison/additive intent tests pass;
- one fake-driven end-to-end technical-realization test reaches fake NEO only on missing permit;
- all fail-closed test cases prevent mutation;
- architecture checks prove the workflow/application dependency boundary;
- no existing legacy tests are intentionally redefined.

### G4 evaluation

`G4 PASS` for Slice 1 only.

Upstream behavior/domain/architecture are accepted; no schema/migration decision is required; exact affected modules and executable proof are known; no P0/P1 decision is delegated to implementation.

## Slice 2 — NEP target query — future G4

Implement accepted ADR-018 target query inside NEP:

```text
AnalyzeTrafficPairs(HostAddress pairs)
-> FirewallCandidate[]
-> accessListName[] + freshness/provenance
```

Current old ForwardingPath/EnforcementAttachment result is not a compatibility source for target output. Exact code/schema impact must be mapped before Slice 2 G4.

## Slice 3 — owner projection adapters / RPM wiring — future G4

- ACC public-read -> fail-closed temporary AD placement adapter in workflow infrastructure;
- RC public query -> fail-closed CurrentResourceRealization adapter;
- AP target current-rule read projection;
- concrete RPM wiring to NEP target query.

No peer SQL. Each adapter has removal trigger from G3.

## Slice 4 — AG + AP target authorization path — future G4

- new `contexts/access_governance` target core/application/persistence;
- target AP governed-subject identity/fact application;
- focused transaction-controlled AG -> AP handoff;
- migrations and legacy coexistence boundaries.

Requires a separate S4 schema/migration impact pass before G4.

## Slice 5 — configured-policy / renderer / NEO integration — future G4

- PPI publication of ConfiguredEffectivePolicySnapshot;
- concrete provider renderer behind workflow infrastructure port;
- semantic equivalence proof for supported first provider/stub;
- adapt NEO inbound command to TargetPolicyArtifact;
- bootstrap integration and integration tests.

## Slice 6 — HTTP/UI/E2E happy path — future G4

Only after the preceding core/infrastructure slices expose stable application entrypoints. Keep UI outside domain ownership and prove one user-visible end-to-end happy path.

## Dependency order

Slice 1 is independent core foundation and is first.

Slices 2 and 4 can be developed independently after Slice 1 but are both required for the complete target journey.

Slice 3 depends on Slice 1 and the NEP target query portion of Slice 2.

Slice 5 depends on Slice 1 and concrete configured/target contracts; full end-to-end wiring also depends on Slice 3.

Slice 6 depends on the application entrypoints from prior slices.

Do not serialize independent work merely for roadmap neatness.

## Readiness guardrail

The current implementation lease covers Slice 1 only. Any production code outside its Authorized scope returns to S4/G4.
