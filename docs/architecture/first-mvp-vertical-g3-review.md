# First MVP vertical — G3 architecture review

Status: `G3 PASS for first MVP vertical`.

Date: 2026-09-15.

Architecture under review: `docs/architecture/first-mvp-vertical.md`.

## Review scope

Evaluate whether the first G2-accepted semantic vertical can be implemented in the current modular-monolith repository without inventing new product/domain decisions or violating ownership/dependency boundaries.

## Challenge findings

### P0

None remaining.

No architecture issue requires changing accepted semantic identity, ownership, approval behavior, RPM/APR meaning, additive remediation or NEO execution semantics.

### P1 — AG -> AP atomicity against current self-commit repository style — RESOLVED

Current PostgreSQL repositories commonly expose mutation methods over an injected `Connection` and an explicit `commit()` operation. Some existing repositories also rollback internally on local mutation failure.

For the target AG -> AP handoff:

- use one focused transaction-controlled application scope/Unit of Work for the authorization transition;
- AG and AP repositories receive the same operation-scoped PostgreSQL connection/transaction;
- mutation methods do not commit independently inside this target path;
- the coordinator commits once only after AG current authorization and AP idempotent fact application both succeed;
- on any failure, rollback the local transaction;
- keep `factRef` idempotency so a future outbox migration does not change semantics.

This is a bounded modular-monolith consistency mechanism, not a Shared Kernel and not peer SQL.

Implementation must not reuse a repository method that commits internally in the middle of this handoff; adapt/extract the transaction-controlled target repository path instead.

### P1 — NEP target query absent from current runtime — RESOLVED AS REQUIRED MIGRATION INCREMENT

Current NEP runtime models proven/current path/attachment-oriented selection and has no runtime `accessListName` result matching the accepted target contract.

Therefore the architecture choice is no longer optional:

```text
Implement NEP target query first:
AnalyzeTrafficPairs(HostAddress pairs)
    -> FirewallCandidate[]
       -> accessListName[]
       -> freshness/provenance
```

It must be implemented inside NEP using NEP-owned current routing/policy-binding state and accepted ADR-018 semantics.

The `policy_realization` workflow must not adapt old `ForwardingPath` / `EnforcementAttachment` results into target candidate/locator semantics.

This is an implementation gap under already accepted NEP target architecture, not an S1/S2 reopen.

### P1 — AD target ownership differs from current physical ACC deployment model — RESOLVED BY BOUNDED CONSUMER ADAPTER

Current runtime exposes ApplicationDeployment and deployment-interaction Resource sets through the ACC target read API, while accepted semantic ownership is AD and target placement meaning is Component -> Resource independent of one Interaction.

For the first implementation slice, a `policy_realization` workflow infrastructure adapter may consume the existing ACC public target read API and publish the workflow-owned `DeploymentPlacementPort` result only when target meaning is unambiguous.

Conservative compatibility rule:

1. inspect active deployment connectivity rows involving the requested Component;
2. read effective Resource sets for the relevant sides at the selected logical time;
3. if there is one evidence set, publish that Resource set as temporary placement projection;
4. if the Component appears in several selected interactions, publish only when all applicable evidence sets agree on the same effective Resource set;
5. no evidence, conflicting sets or incomplete paging/evidence -> `UnresolvedPlacement`, never empty placement truth.

The adapter lives in `workflows/policy_realization/infrastructure`, not in a pseudo-AD façade package, and never queries ACC tables directly.

Removal trigger: dedicated AD runtime/application API owns ComponentPlacement.

### P1 — RC target AddressSpace differs from endpoint runtime — RESOLVED BY BOUNDED CONSUMER ADAPTER

A workflow infrastructure adapter may call an RC public application query/projection that returns current effective realization evidence for a Resource.

Projection rule:

```text
exactly one effective corporate-visible address -> CurrentResourceRealization
zero -> unresolved
more than one -> unresolved
```

Endpoint identity never crosses the adapter. Prefix is preserved and then fails closed at the HostAddress-only RPM/NEP edge.

If the required resource-based RC application query does not yet exist, adding that query inside RC is part of the implementation slice; workflow SQL is forbidden.

Removal trigger: accepted ResourceAddressFact/CurrentResourceRealization runtime migration.

### P1 — APR current orchestration encodes superseded model — RESOLVED BY REPLACEMENT BOUNDARY

Retain only source-neutral permit-space algebra whose behavior matches the accepted exact set operations.

Do not adapt target flow through:

- `ManagedReconciliationScope`;
- old `EnforcementPlacement` desired-policy derivation;
- legacy ComponentDeployment interaction identity;
- generic `Add | Remove | Replace` remediation choice.

Implement a new APR target application use case over `TargetRequiredPolicy + ConfiguredEffectivePolicySnapshot`, yielding `Realized | Drift | Uncomparable` and optional additive `VerifiedChangeIntent`.

### P2 — renderer physically lives under APR — RESOLVED BY RECLASSIFICATION

Existing Cisco ASA rendering logic is useful implementation evidence and may be reused at the algorithm level, but target rendering must live behind `ProviderRendererPort` outside APR domain/application semantics.

For the first vertical, place the concrete adapter under `workflows/policy_realization/infrastructure/provider_renderer/` unless a later architecture decision establishes another integration owner.

Target adapter input is `VerifiedChangeIntent`, with explicit `accessListName` from ComparisonScope. It must produce `TargetPolicyArtifact` only when semantic equivalence can be established. Existing renderer output without equivalence evidence is insufficient by itself.

### P2 — NEO target artifact input differs from current raw command — RESOLVED BY ADAPTATION

Retain current NEO authority, idempotency, pre-acquire, optimistic revision, apply outcome and post-check orchestration.

Adapt the inbound application command/projector so TargetPolicyArtifact provides renderer identity, content, digest, comparison scope, base correlation and intent provenance.

No NEO semantic redesign is required.

### P2 — code taxonomy did not list new target contexts/workflow — RESOLVED

`docs/architecture/code-structure.md` now records target `access_governance`, `application_deployment` and `policy_realization` ownership plus the bounded migration-adapter rule.

## Consistency/failure review

The architecture preserves these fail-closed boundaries:

- unresolved AG scope obligations -> no grant;
- unresolved AD/RC projection -> no RPM output;
- Prefix -> unresolved before NEP;
- missing NEP target/locator -> unresolved;
- configured-policy incomplete/unknown/unsupported -> APR Uncomparable;
- excess-only drift -> no mutation;
- renderer unsupported/equivalence unknown -> no artifact;
- semantic basis changed before execution -> no NEO call;
- mutation authority unknown/denied -> no apply;
- target/base precondition conflict -> no apply;
- unknown apply -> no blind retry.

No distributed transaction or global snapshot is claimed.

## Architecture completion result

`G3 PASS` for this exact first MVP vertical.

An implementer can now choose code/migration slices without making a new product/domain/architecture decision.

This does not authorize implementation. Proceed to S4 Implementation Readiness and G4 for a bounded implementation lease.
