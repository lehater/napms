# First MVP vertical — target architecture

Status: `S3 architecture candidate for G3`.

Date: 2026-09-15.

## Purpose

Realize the G2-accepted first MVP semantic vertical with the smallest architecture that preserves context ownership, fail-closed behavior and migration boundaries.

This architecture deliberately avoids a big-bang rewrite. Target application contracts are introduced first; current runtime structures may satisfy them only through explicit compatibility adapters that cannot weaken target semantics.

## Accepted semantic path

```text
ACC InteractionContractRevision
    -> AD ApplicationDeployment / ComponentPlacement
    -> RC Resource / HostAddress realization
    -> AG bilateral authorization
    -> AP current Policy Rule
    -> RPM TargetRequiredPolicy
    -> PPI ConfiguredEffectivePolicySnapshot
    -> APR exact comparison
    -> VerifiedChangeIntent(ENSURE-PERMIT)
    -> Provider Policy Renderer
    -> TargetPolicyArtifact
    -> NEO controlled mutation
```

The current MVP limitations remain semantic constraints, not architecture choices:

- one applicable ResponsibilityScope per AG side;
- HostAddress-to-HostAddress only at the first RPM -> NEP edge;
- Prefix causes unresolved and is never host-expanded;
- APR remediation is additive-only on `missing`;
- `excess` is report/audit only;
- provider rendering must preserve semantics or fail closed;
- NEO execution success is not final semantic convergence proof.

## Architecture shape

The MVP stays a modular monolith with one PostgreSQL deployment and in-process application calls.

No message broker, new deployable service, distributed transaction, durable workflow engine or generic service bus is introduced.

Two distinct application segments are retained:

```text
A. Governance transition
   AG request / decisions / withdrawal
       -> AG current authorization
       -> AP current Policy Rule projection

B. Technical realization
   AP current Policy Rule
       -> cross-context policy_realization workflow
       -> RPM / PPI / APR / renderer / NEO
```

Human approval lifecycle is therefore not modelled as one synchronous workflow ending in a firewall mutation.

## Segment A — AG -> AP

### Ownership

`contexts/access_governance` is the target owner of:

- AccessRequest history;
- bilateral ApprovalDecision history;
- GovernedAuthorization current grant state;
- authorization grant/withdrawal facts.

`contexts/access_policy` remains owner of current semantic Policy Rule truth.

### Application handoff

AG application use cases return explicit semantic handoff facts:

```text
AuthorizationGranted(subject, provenance, factRef)
AuthorizationWithdrawn(subject, provenance, factRef)
```

AP exposes an idempotent application command that applies one authorization fact to its own repository.

Neither context imports the peer domain model. Contracts are application-level values.

### MVP consistency strategy

For the modular-monolith MVP, AG current-authorization transition and AP application of the corresponding authorization fact are coordinated in one local PostgreSQL transaction through the composition/bootstrap boundary.

Rules:

- AG writes only AG-owned tables/repository;
- AP writes only AP-owned tables/repository;
- the coordinator invokes public application commands and never writes peer tables directly;
- failure in either context rolls back the local transaction;
- AP fact application remains idempotent by `factRef` so later migration to outbox/asynchronous delivery does not change semantics.

This intentionally uses the existing single-process/single-database deployment to avoid an unnecessary broker while preventing the unsafe case where AG withdrawal commits but AP remains currently authorized.

Revisit trigger: AG/AP become separately deployed or no longer share a transaction-capable local database boundary. At that point replace the local atomic handoff with transactional outbox + idempotent consumer, without changing the semantic contract.

## Segment B — policy_realization workflow

### Workflow owner

Create a cross-context workflow under:

```text
backend/src/napms/workflows/policy_realization/
    application/
    infrastructure/
    presentation/   # only if an HTTP/CLI entrypoint is actually needed
```

The workflow owns no authoritative business truth and no independent lifecycle.

Its responsibility is to coordinate already-owned application contracts for one explicit realization attempt.

It must not persist copies of peer domain aggregates. Rebuildable diagnostics/correlation values may be returned or logged; durable workflow state is deferred until a concrete recovery/user journey requires it.

### High-level flow

```text
1. read current AP Policy Rule / governed subject
2. resolve ACC immutable interaction traffic contract
3. resolve AD component placements
4. resolve RC current Resource realization
5. compose supported HostAddress TrafficPairs
6. ask NEP for every candidate firewall/access-list locator
7. derive complete TargetRequiredPolicy[] or unresolved
8. obtain ConfiguredEffectivePolicySnapshot for one comparison scope through PPI
9. run APR exact comparison
10. if missing != empty, obtain VerifiedChangeIntent(ENSURE-PERMIT)
11. render through Provider Policy Renderer
12. revalidate the semantic basis is still current
13. execute TargetPolicyArtifact through NEO
14. expose operation result; later convergence remains a separate observation/compare cycle
```

The workflow stops immediately on an unresolved/unknown/unsupported state that makes the next step unsafe.

## Consumer-owned workflow ports

Keep the first implementation small. The workflow application layer owns semantic-facing ports, while infrastructure adapters call source-context application APIs.

```text
CurrentPolicyPort
    getCurrentPolicy(subject/ref, logicalTime)

InteractionContractPort
    getInteractionContract(revisionRef)

DeploymentPlacementPort
    getPlacements(applicationDeploymentRef, componentRef, logicalTime)

ResourceRealizationPort
    getCurrentRealization(resourceRef, logicalTime)

EnforcementCandidatePort
    analyzeHostPairs(trafficPairs)

ConfiguredPolicyPort
    getConfiguredSnapshot(comparisonScope)

ProviderRendererPort
    render(verifiedChangeIntent, targetCapabilities, baseCorrelation)

NetworkOperationPort
    execute(targetPolicyArtifact, executionContext)
```

APR comparison/change verification remains an APR application/domain call, not a workflow-owned port when both packages are in-process.

RPM remains a pure/derived application composition inside the workflow boundary; it gets no repository and no independent persistence.

Do not split ports further unless actual change locality or testing pressure requires it.

## Dependency direction

```text
workflows/policy_realization/application
    -> workflow-owned port contracts / value contracts
    -> APR public application contract

workflow infrastructure adapters
    -> ACC application/read API
    -> AD application/read API or temporary AD compatibility API
    -> RC application/read API
    -> AP application/read API
    -> NEP application/query API
    -> PPI integration capability
    -> Provider Renderer integration capability
    -> NEO application API

platform/bootstrap
    -> assembles concrete adapters + workflow
```

Forbidden:

- importing another context's `domain` package from the workflow or peer context;
- direct SQL against peer-owned schemas;
- exposing peer ORM/repository objects as public contracts;
- putting orchestration semantics in `platform`;
- making RPM a context/repository merely for convenience.

## Time and snapshot correlation

One offset-aware `logicalTime` is selected at realization-attempt start for semantic/current-as-of reads that support it:

- AP current-policy selection;
- AD placement projection;
- RC Resource realization;
- ACC immutable contract reference does not require temporal mutation semantics once revision is selected.

NEP target semantics are current-state only. The workflow therefore does not fake historical `asOf` for NEP; it retains NEP `snapshotCollectedAt` freshness in `TargetRequiredPolicy` provenance.

PPI publishes its own evidence/effective time and completeness. APR comparability uses explicit scope/completeness/provenance rather than pretending every source was read at one globally atomic instant.

No cross-context read transaction is required.

## Semantic-basis freshness before mutation

A realization attempt may span enough time for authorization/placement/required-policy basis to change before execution.

Before invoking NEO, the workflow performs a lightweight semantic-basis revalidation using opaque provenance/correlation from `VerifiedChangeIntent`:

- the AP Policy Rule/grant basis used by the intent must still be current;
- the target comparison scope must still be the one represented by the rendered artifact;
- if current basis is missing, changed or unknown, no mutation is requested.

This check is owned by the workflow/application adapters; NEO does not interpret AP/AG semantics.

The check reduces stale-intent risk but is not claimed as a distributed atomic lock with the provider. Concurrent change after the check is handled by NEO target preconditions and by the later convergence cycle. The MVP does not introduce distributed locking.

## Failure and unresolved propagation

Fail closed end to end:

| Condition | Architecture result |
|---|---|
| AG obligation resolution 0 or >1 scope | no grant / no AP current rule |
| AD placement projection incomplete/ambiguous | RPM unresolved; stop |
| RC target projection has no address | RPM unresolved; stop |
| RC target projection has Prefix | RPM unresolved for current edge; stop |
| legacy RC exposes >1 effective address | compatibility projection unresolved; stop |
| NEP has no candidate or candidate has no access-list locator | RPM unresolved; stop |
| PPI incomplete/unknown/unsupported | APR Uncomparable; stop |
| APR Realized | no change; successful no-op result |
| APR excess-only drift | report drift; no mutation |
| renderer unsupported/equivalence unknown | no artifact; stop |
| semantic-basis revalidation changed/unknown | no NEO call |
| mutation authority denied/unknown | NEO PreconditionFailed |
| target revision/base correlation stale | NEO PreconditionFailed |
| apply Unknown | no blind retry |
| post-check Drift/Unknown | return operation outcome; later reconciliation required |

Partial technical output may be retained for diagnostics but must never be upgraded to a complete `TargetRequiredPolicy`, `VerifiedChangeIntent` or executable artifact.

## Migration seams

### Application Deployment — temporary ACC-backed compatibility adapter

Target semantic ownership is AD, but current runtime `ApplicationDeployment` and deployment-side Resource bindings live physically under `application_catalogue`.

For the first slice:

- expose a narrow AD-compatible application projection through an adapter over ACC's existing public target read contract;
- consumers depend on `DeploymentPlacementPort`, not ACC persistence/domain types;
- direct reads of `napms_application_catalogue` tables from AG/RPM/workflow are forbidden.

Important fail-closed rule:

Current ACC Resource bindings are interaction-side facts, while target `ComponentPlacement` is component-to-Resource placement truth independent of one Interaction. The compatibility adapter may publish target placement only where current data maps unambiguously to the requested deployment + component. Conflicting interaction-side bindings or otherwise non-unique meaning produce `UnresolvedPlacement`; they must not be merged/guessed into canonical AD truth.

Removal trigger: a dedicated `contexts/application_deployment` runtime owns ApplicationDeployment/ComponentPlacement persistence and publishes the target application API. Then the compatibility adapter is deleted rather than retained as a facade.

### Resource Catalogue — endpoint-runtime compatibility projection

Current RC runtime is still endpoint/realization based; target RC is `Resource -> AddressSpace[0..1]`.

For the first slice, implement a target read projection behind `ResourceRealizationPort`:

```text
legacy effective realizations for Resource at logicalTime
    -> exactly one corporate-visible effective address => target CurrentResourceRealization
    -> zero => unresolved
    -> more than one => unresolved
```

The adapter must not choose one legacy endpoint/address arbitrarily and must not expose endpoint identity downstream.

If the one address is a Prefix, preserve it as Prefix; the workflow then stops at the current HostAddress-only RPM/NEP edge.

Removal trigger: RC persistence/application model is migrated to the accepted ResourceAddressFact / CurrentResourceRealization target.

### Network Enforcement Placement — target query adapter

Current NEP runtime still implements the older selection model; the accepted `AnalyzeTrafficPairs -> FirewallCandidate/accessListName` target query is not yet the runtime contract.

The first implementation must either:

1. add the target NEP application query using current NEP-owned state behind NEP's own boundary; or
2. temporarily adapt current NEP application results only if every target field and completeness/freshness meaning can be produced without inventing a proven-path claim.

The workflow must not adapt NEP private persistence itself.

If current data cannot provide target candidate + locator semantics faithfully, the first implementation increment is the NEP target query rather than a fake workflow adapter.

### Access Governance

There is no target `contexts/access_governance` runtime package today. Legacy Connectivity Decision is migration evidence and must not be renamed/reused as the bilateral target merely to save work.

Create the target AG package when implementation is authorized. Reuse technical repository/authority patterns where useful, not legacy single-decision semantics.

### Access Policy

Current AP `RuleSemanticIdentity` is based on legacy source/destination ComponentDeployment + DCS revision and materializes from a legacy Allowed decision.

For target implementation, replace the semantic identity/handoff path with the accepted governed subject and AG grant/withdrawal contract. Existing repository/application infrastructure may be adapted where it does not encode the superseded identity/lifecycle.

Do not maintain two authoritative current Rule meanings for the same target path. Legacy compatibility reads may remain only for unaffected old runtime journeys until their migration removal condition is met.

### APR

Retain/adapt the existing source-neutral region algebra where its semantics match the accepted effective-permit operations.

Replace for the target slice:

- `ManagedReconciliationScope` as target comparison ownership;
- old EnforcementPlacement-driven desired-policy derivation;
- old ComponentDeployment interaction identity;
- generic `No-op | Add | Remove | Replace` remediation choice.

New APR application contracts consume `TargetRequiredPolicy` + `ConfiguredEffectivePolicySnapshot` directly and may emit only additive `VerifiedChangeIntent(ENSURE-PERMIT)` for this slice.

### Provider Policy Renderer

Current provider rendering code physically inside APR is migration evidence. Move/reimplement target rendering behind `ProviderRendererPort` as an integration adapter outside APR core semantics.

No new bounded context is created.

The first supported provider adapter may be deterministic/stubbed if it can establish the required semantic-equivalence guarantee; unsupported providers fail closed.

### NEO

Retain/adapt current NEO use case, ports, idempotency and pre/post-check flow.

Adapt its inbound command so `TargetPolicyArtifact` is the source of renderer identity/content/digest/base correlation/provenance rather than treating those raw fields as independent policy meaning.

No NEO rewrite is required.

## Retain / adapt / replace summary

| Runtime area | Disposition | Reason |
|---|---|---|
| ACC immutable traffic/read APIs | Retain/adapt | useful owner contract; deployment data needs migration seam |
| ACC-owned ApplicationDeployment storage | Temporary compatibility source | physical owner differs from accepted target AD ownership |
| RC endpoint-based realization | Temporary compatibility projection | target requires one Resource AddressSpace |
| legacy Connectivity Decision | Do not promote to target AG | bilateral/history/current-grant semantics differ |
| AP persistence/application shell | Adapt | current identity/decision contract is superseded |
| NEP current selection runtime | Adapt only if target query semantics can be proven; otherwise add target query | target candidate meaning differs from proven/old placement model |
| APR region algebra | Retain/adapt | source-neutral set operations are useful |
| APR old desired/managed-scope orchestration | Replace for target slice | wrong ownership/identity/remediation vocabulary |
| APR-embedded renderer | Move/reclassify behind integration port | rendering is not APR domain ownership |
| NEO application flow/stub | Retain/adapt | authority/idempotency/precondition/outcome semantics already fit |

## Persistence and transactions

Authoritative persistence remains context-owned.

First-slice expected target writes:

- AG: AccessRequest / decision history / current GovernedAuthorization;
- AP: current target Policy Rule projection;
- NEO: NetworkOperation if/when durable persistence is required by the implementation slice.

RPM, PPI snapshots, APR comparison results, VerifiedChangeIntent and rendered artifact do not gain durable business identity merely because implementation may cache/log them.

The only intentional cross-context atomic transaction in the MVP architecture is the local AG-current-authorization -> AP-current-rule handoff described above. All technical realization reads/computations and external execution remain outside that transaction.

## Idempotency and retries

- AG -> AP fact application: idempotent by factRef.
- RPM/APR pure derivation: safe to recompute.
- PPI/renderer: deterministic or correlation-aware; unsupported/unknown fails closed.
- NEO: existing operationId + target + artifactDigest idempotency retained.
- NEO `Unknown` apply: never blind retry.

No generic workflow retry engine is introduced.

## Observability

Carry one realization-attempt correlation id through workflow logs/diagnostics.

Preserve owner-specific provenance rather than inventing a global business identity for the workflow.

At minimum diagnostics identify:

- governed subject / AP Rule reference;
- comparison scope where known;
- unresolved owner/reason;
- source freshness/provenance references;
- renderer identity/artifact digest when produced;
- NEO operation id/outcome when execution is attempted.

## Security and authority

- AG request/approve/withdraw permissions are checked through Authority Management at their owning application use cases.
- Reading protected AP/RC/AD data uses existing read-authority contracts where required.
- Network mutation authority is checked independently by NEO immediately before apply.
- Resource responsibility/contact metadata never substitutes for actor authority.
- Workflow orchestration does not grant authority by being able to call a port.

## Architecture invariants

1. No workflow or adapter becomes an authoritative semantic owner.
2. No peer-private database access is used for convenience.
3. Target cross-context values do not expose legacy ComponentDeployment, ResourceEndpoint or managed-reconciliation identity.
4. Legacy compatibility adapters can only narrow to accepted target meaning; ambiguity becomes unresolved.
5. One current target comparison key is `firewallId + accessListName` end to end.
6. Missing/incomplete/unknown never becomes empty/success.
7. The first technical realization path remains HostAddress-only at the NEP edge.
8. `excess` never becomes automatic removal in the MVP.
9. Provider rendering is outside APR core and NEO does not render.
10. NEO never applies without explicit mutation authority and target/base preconditions.
11. No distributed infrastructure is introduced without concrete pressure.
12. Compatibility seams have explicit removal triggers and must not become permanent alternate owners.

## G3 challenge checklist

Before G3 PASS verify:

- the AG -> AP local atomic handoff is feasible with current bootstrap/database transaction support;
- target AD compatibility projection can be fail-closed without pretending per-interaction binding is canonical ComponentPlacement;
- RC target projection can preserve the one-address invariant over current data;
- NEP target query can be implemented/adapted without reviving proven-path semantics;
- APR algebra can be reused without importing old target identity/remediation types;
- provider renderer has a concrete integration location outside APR core;
- NEO adaptation does not require semantic redesign;
- no P0/P1 architecture issue forces a new S1/S2 decision.

If any item cannot be satisfied, rework S3 or reopen only the affected upstream stage.
