# Network Environment Operations — tactical model

Status: `S2 MVP Tactical checkpoint; TargetPolicyArtifact handoff aligned 2026-09-15`.

Date: 2026-09-15.

## Responsibility

Network Environment Operations owns the lifecycle and outcome of one controlled target mutation attempt downstream of accepted provider rendering.

A separate semantic boundary is justified because execution has its own operation identity, mutation authority, optimistic-concurrency boundary, failure/recovery vocabulary and audit lifecycle. It does not own Access Policy, APR change design, target placement or rendered configuration meaning.

## Input boundary

NEO consumes one already rendered artifact plus execution context:

```text
TargetPolicyArtifact {
    targetRef
    comparisonScope
    baseTargetCorrelation
    rendererIdentity
    rendererVersion
    artifactContent
    artifactDigest
    semanticEquivalenceEvidence
    intentProvenance
}

ExecutionContext {
    operationId
    actorId
    mutationAuthorityScope
    expectedPreStateRevision?
}
```

The artifact is immutable input to NEO for one operation intent. NEO may validate it and its correlations but may not rewrite provider policy semantics.

## Aggregate/value model

`NetworkOperation` is identified by `operationId` and binds:

```text
NetworkOperation
    operationId
    targetRef
    comparisonScope
    artifactDigest
    rendererIdentity/version
    actorId
    mutationAuthorityScope
    baseTargetCorrelation
    expectedPreStateRevision?
    orderedOperationEvents[]
    finalOutcome?
```

For MVP, `NetworkOperation` is the only durable-meaning execution aggregate required by this context.

The existing deterministic port-backed stub may remain an implementation/testing adapter. Durable storage is not a Tactical requirement until an implementation slice requires it.

## Outcomes

Apply transport outcome:

```text
Applied | Rejected | Unknown
```

Final operation outcome:

```text
Verified | Rejected | PreconditionFailed | Drift | Unknown
```

`Applied` is intermediate only. It never means verified desired state by itself.

`Verified` means the immediate execution adapter proved correspondence to the supplied artifact. It is not final semantic convergence proof; final convergence requires later provider observation/interpreter publication and APR comparison.

## Core operation flow

```text
TargetPolicyArtifact
    + ExecutionContext
        -> mutation authority check
        -> target/base pre-check
        -> provider apply
        -> immediate post-check
        -> NetworkOperation outcome
```

If any required precondition is unknown or contradictory, mutation fails closed.

## Invariants

1. One `operationId` binds exactly one target + artifact digest intent.
2. Reusing an operation id with different target/artifact intent is conflict/fail-closed.
3. Identical retry returns the established operation result and does not repeat mutation.
4. Mutation cannot start before explicit action-specific mutation authority admission and successful pre-check.
5. Expected revision or base target correlation mismatch prevents mutation.
6. Observed concurrent revision change before apply prevents mutation.
7. Unknown apply outcome cannot be converted into success or blindly retried.
8. `Verified` requires successful immediate post-check proving correspondence to the supplied artifact under the execution adapter contract.
9. Renderer/provider references and artifact digest are provenance/correlation, not policy-semantic identity.
10. NEO never rewrites APR or renderer semantics for device convenience.
11. Renderer failure/unsupported result cannot be converted into an executable operation.
12. Post-operation semantic convergence is external to the NetworkOperation outcome and is re-established through observation/interpreter/APR comparison.

## Mutation authority

Authority Management owns whether actor A may perform the required mutation action for scope S at time T.

NEO consumes that authority contract. It does not infer mutation permission from Resource owner, administrator, responsibility or contact metadata.

Exact target-to-authority-scope mapping remains an upstream Authority Management/integration contract unless a concrete NEO use case requires additional domain semantics.

## Concurrency and idempotency

The optimistic boundary is formed by:

```text
baseTargetCorrelation
+ expectedPreStateRevision when supplied
+ acquired pre-state revision
```

Stale or conflicting state gives `PreconditionFailed` and no mutation attempt.

`artifactDigest` plus target identity provides operation-intent correlation for retry/idempotency. It does not replace `operationId`.

## Recovery

MVP does not claim generic rollback safety.

- `Rejected` / `PreconditionFailed`: no mutation was accepted, so rollback is unnecessary.
- `Unknown`: no blind retry or rollback.
- `Applied` followed by `Drift`/`Unknown`: requires later reconciliation/operator handling until target-specific safe recovery semantics are accepted.

## Audit/provenance

A NetworkOperation preserves enough evidence to explain:

- who attempted the mutation and under which authority scope;
- which target/comparison scope was intended;
- which renderer/artifact digest was supplied;
- which APR intent/provenance the artifact represents;
- which base/revision preconditions were observed;
- apply transport result/reference;
- post-check observation;
- final operation outcome.

The exact storage/event schema is downstream implementation detail.

## MVP adapter

The first executable adapter may remain a deterministic in-process target stub with explicit scenario controls for:

- success -> `Verified`;
- explicit rejection;
- uncertain apply -> `Unknown`;
- stale/concurrent precondition -> `PreconditionFailed`;
- post-apply mismatch -> `Drift`;
- idempotent retry/conflicting operation reuse.

This proves execution orchestration semantics only, not compatibility with any real provider.

## Ownership boundaries

- Authority Management owns mutation authority.
- APR owns source-neutral verified change intent.
- Provider Policy Renderer owns provider-specific representation and equivalence proof.
- NEO owns controlled execution lifecycle/outcome.
- NEP owns target relevance/placement meaning.
- Provider Interpreter owns normalized configured effective-policy publication.
- TAE may preserve independently sourced evidence but does not become NEO operation truth automatically.

## Deliberately deferred

- production device transport;
- credentials/secrets model;
- generic rollback;
- multi-target transaction/orchestration;
- provider rendering inside NEO;
- final convergence lifecycle inside NEO;
- durable persistence mechanics unless implementation requires them.

## Tactical result

The existing NEO execution model is coherent for the additive MVP path. No new domain entity or lifecycle is required beyond `NetworkOperation`; the main revalidation change is the explicit `TargetPolicyArtifact` input boundary and separation of immediate execution verification from later semantic convergence.
