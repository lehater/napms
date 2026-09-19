# Test Design portability research — NAPMS first MVP

Status: research candidate.
Input rule: accepted NAPMS design knowledge only. Existing implementation and executable tests are not evidence.

## Question

Does the Test Design boundary observed in Nutrition survive in a materially different system: browser + HTTP application API + authorization + multiple domain modules + PostgreSQL + policy materialization?

## Existing Verification Design

NAPMS already has a strong accepted `MVP-TEST-INTENT`: verification levels and named acceptance scenarios. That is useful evidence for the distinction because it lets this experiment ask whether a downstream Test Design adds non-duplicative knowledge.

Verification Design says, for example, that unauthorized mutation must be denied with owner state unchanged. Test Design must make the observable contract executable without deciding production internals.

## Executable test contracts

### TD-RC-01 Resource lifecycle/history

Given a Resource with current realization/scope/responsibility facts, when a current fact is replaced or ended, supported read behavior returns the new current fact immediately and retains the ended fact with validity/provenance history.

No test may require direct table inspection as the product oracle.

Traces: MVP-RC-014, Resource Catalogue tactical model, Resource Detail UI.

### TD-ACC-01 Cross-application interaction rejection

Given Components owned by different Applications, attempting to create one Interaction between them is rejected atomically and creates no Interaction identity.

Traces: MVP-ACC-006.

### TD-ACC-02 Published traffic revision immutability

Given a published InteractionContractRevision, changing traffic semantics creates a new revision identity. The previous revision remains resolvable with unchanged semantics.

Traces: MVP-ACC-007.

### TD-AD-01 Deployment identity

Given one Component deployed to Resource A, representing deployment of the same Component to Resource B requires a distinct ComponentDeployment identity; the original deployment is not silently retargeted.

Traces: MVP-AD-008.

### TD-BC-01 Process-backed connectivity need is required

Given an otherwise valid RuleChange whose referenced ConnectivityNeed is not current/process-backed according to accepted BC semantics, submission is rejected with no Access Policy mutation.

Traces: MVP-BC-004.

### TD-AP-01 Decision preserves prior effective revision

Given an effective accepted policy revision and a later Pending or Rejected change, current effective policy remains the prior accepted revision.

Traces: MVP-POL-002.

### TD-AP-02 Withdrawal changes current view, not history

Given an effective PolicyRule, withdrawal removes it from current policy export while historical decision/change records remain available through their owner semantics.

Traces: MVP-AP-009.

### TD-AUTH-01 Admission is backend-owned

For every protected mutation, absence of effective Authority Management admission denies the operation and leaves owner state unchanged.

Caller-supplied actor/authority fields, browser state and persistence manipulation cannot substitute for backend admission.

Traces: MVP-AUTH-005, MVP-SEC-012.

### TD-AUTH-02 Identity comes from session boundary

Given a protected HTTP operation, application actor identity is derived from the authenticated backend session. A request body/query/header field that is not the accepted session mechanism cannot override that identity.

Traces: security architecture + implementation readiness.

### TD-EXP-01 Complete-or-Unresolved

Given an effective policy rule whose materialization lacks a required current AddressSpace, policy export returns explicit Unresolved causes and no partial success payload.

Traces: MVP-EXP-003.

### TD-EXP-02 Prefix semantics are preserved

Given a policy endpoint represented as Prefix, successful materialization/export retains Prefix semantics and does not expand it into host rows.

Traces: MVP-EXP-010.

### TD-EXP-03 Table/CSV semantic equivalence

Given one successful materialized current policy, table/JSON representation and CSV export encode the same policy rows/meaning modulo representation-specific formatting.

Traces: MVP-E2E-001.

### TD-E2E-01 Complete authoring-to-export journey

Given admitted actor and empty accepted MVP state, execute only supported browser/API operations to create two addressed Resources, one Application with two Components, one HTTPS TCP/443 Interaction revision, deployments, Process-backed ConnectivityNeed, RuleChange and decision.

The final current export is complete, contains the accepted TCP/443 relation and has semantically equivalent table and CSV forms. No hidden/manual state fabrication is permitted.

Traces: MVP-E2E-001.

### TD-HTTP-01 Rejection is atomic

For each mutation whose domain/admission validation rejects the command, observable owner state before and after is semantically identical. HTTP error mapping must not expose a successful mutation.

Traces: implementation readiness, quality requirements.

### TD-HTTP-02 Stable owner identifiers

Successful create/publish operations return stable owner identifiers usable by later supported journey operations. Clients are not required to discover database identifiers through persistence access.

Traces: implementation readiness/OpenAPI.

### TD-PERSIST-01 Cross-module references preserve ownership

Integration scenarios create cross-module relationships only through stable owner identifiers and owner contracts. Replacing a provider test double with a conforming provider implementation must not require consumer knowledge of provider tables/ORM types.

Traces: system rules, persistence, module contracts.

### TD-SEC-01 Failure categories remain distinguishable

Authorization denial, domain rejection, Unresolved materialization and infrastructure uncertainty remain observably distinguishable in application/diagnostic evidence. Credentials/session secrets are not required as assertion material.

Traces: MVP-OBS-013, security/observability design.

### TD-QUAL-01 Infrastructure uncertainty is not success

Inject an accepted persistence/transport uncertainty at a mutation boundary. The operation cannot be reported as successful unless accepted commit/completion semantics are established.

Traces: MVP-QUAL-011.

## Architecture/contract evidence

Structural verification must reject:
- domain/application modules depending on HTTP or persistence representations;
- consumer modules reading another module's tables as integration;
- browser/UI becoming authority for domain invariants/admission;
- internal HTTP between in-process modules;
- policy materialization bypassing provider-owned contracts;
- Access Policy depending on provider persistence internals.

The concrete structural-test mechanism is implementation-local.

## Property/state-machine opportunities

The following deserve generated/state-machine testing rather than only examples:
- PolicyRule change/decision/withdrawal lifecycle;
- InteractionContractRevision append-only behavior;
- current-versus-history temporal facts;
- complete-or-Unresolved materialization under missing provider facts;
- authorization invariance: denied operations preserve owner state;
- representation equivalence between table/JSON and CSV.

No property-testing framework is mandated.

## TDD readiness protocol

For each implementation slice:
1. select traceable Test Design contracts;
2. materialize the smallest executable public/contract test;
3. demonstrate RED due to missing intended behavior;
4. implement minimum behavior;
5. GREEN;
6. refactor;
7. run applicable structural/integration/property evidence;
8. route any new semantic decision upstream instead of encoding it in the test or production code.

Private helper tests, fixture construction, mocking style, exact test file layout and framework-specific assertion syntax remain implementation freedoms.

## Comparison with accepted Test Intent

The accepted Test Intent already owns verification levels and scenario intent. Test Design adds:
- explicit precondition/operation/oracle boundaries;
- atomicity/no-mutation oracles;
- identity and history preservation rules;
- substitute/provider boundary expectations;
- forbidden test oracles such as direct table inspection for product behavior;
- property/state-machine candidates;
- precise TDD materialization protocol.

This is not a restatement of verification levels. It is an executable-contract refinement.

## Portability result

The boundary observed in Nutrition survives NAPMS despite materially different domain and delivery architecture.

Common invariant:
- Verification Design owns what evidence is required.
- Test Design owns executable observable contracts/scenarios/properties and their traceability.
- Test implementation owns concrete framework code.
- Product/domain/architecture Authorities remain owners of semantic truth.

NAPMS additionally shows that Test Design is valuable where verification already has named scenarios: it refines those scenarios into executable oracles without stealing design ownership.

## Dependency finding

Semantic Test Design should consume Verification Design plus accepted product/domain/application/architecture/interface/data/security/quality/component knowledge. It should normally precede terminal Implementation Design so implementation choices can preserve testability.

Technology-specific test realization can be refined after Implementation Design without moving semantic test truth downstream.

## Recommendation for Harness research

Two-project evidence now supports a reusable optional `TEST-DESIGN` Authority/skill. It should not make TDD universally mandatory.

Recommended semantics:
- optional when a project wants explicit executable test contracts before coding or when implementation agents otherwise must invent material test oracles;
- capability `test-design` is consumed by implementation/coding consumers when selected;
- TDD RED/GREEN sequence is project engineering policy/process, not a universal Harness invariant;
- test code is not a CanonicalArtifact merely because TDD writes it before production code.






## Graph-model caveat discovered by experiment

The current NAPMS canonical graph makes accepted Test Intent depend on Implementation Readiness. Attempting to place semantic Test Design after Test Intent and before Implementation Design creates a cycle. This is evidence that the current NAPMS ordering conflates verification intent with downstream implementation-readiness. The portability result therefore supports a future split/reordering rather than forcing the candidate capability into the current implementation consumer graph during research.
