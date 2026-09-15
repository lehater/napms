# Network Environment Operations — Tactical DDD model

## Responsibility

Network Environment Operations owns the lifecycle and outcome of one controlled target mutation attempt downstream of provider rendering.

NEO owns operation identity, mutation admission, optimistic-concurrency protection, execution outcome and operation provenance. It does not own Access Policy, APR change design, target placement, rendered policy meaning or general technical-evidence acquisition.

NEO may read target state only when that read is required to protect or verify one mutation operation. General polling, evidence collection and technical-state acquisition remain outside NEO.

## Input boundary

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

The rendered artifact is immutable input for one operation intent. NEO may validate the artifact and its correlations but may not reinterpret or rewrite provider policy semantics.

## NetworkOperation

```text
NetworkOperation {
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
}
```

`operationId` identifies one controlled mutation intent.

## Outcomes

Apply transport outcome:

```text
Applied | Rejected | Unknown
```

Final operation outcome:

```text
Verified | Rejected | PreconditionFailed | Drift | Unknown
```

`Applied` is intermediate and never means semantic convergence by itself.

`Verified` means the immediate execution adapter proved correspondence to the supplied artifact. Semantic convergence remains established through provider observation/interpreter publication and APR comparison.

## Operation flow

```text
TargetPolicyArtifact
    + ExecutionContext
        -> mutation authority check
        -> target/base pre-check
        -> provider apply
        -> immediate post-check
        -> NetworkOperation outcome
```

Any unknown or contradictory required precondition fails closed.

## Mutation authority

Authority Management owns whether an Actor may perform the required mutation action for a Responsibility Scope at an effective time. NEO consumes that authority decision and does not infer permission from Resource owner, administrator, responsibility or contact metadata.

Target-to-authority-scope correlation is an integration/architecture contract unless additional domain semantics are explicitly owned elsewhere.

## Concurrency and idempotency

The optimistic-concurrency boundary combines:

```text
baseTargetCorrelation
+ expectedPreStateRevision when supplied
+ acquired pre-state revision
```

A stale or conflicting state produces `PreconditionFailed` without mutation.

One `operationId` binds exactly one target + artifact-digest intent. Reuse with different intent is a conflict and fails closed. An identical retry returns the established operation result without repeating mutation.

`artifactDigest` plus target identity correlates operation intent but does not replace `operationId`.

## Recovery

- `Rejected` or `PreconditionFailed`: no accepted mutation, so rollback is unnecessary.
- `Unknown`: no blind retry or rollback.
- `Applied` followed by `Drift` or `Unknown`: requires reconciliation/operator handling; NEO makes no generic rollback-safety claim.

## Provenance

A NetworkOperation preserves enough evidence to explain:

- actor and mutation-authority scope;
- target and comparison scope;
- renderer identity/version and artifact digest;
- APR intent provenance;
- base/revision preconditions;
- provider apply result/reference;
- immediate post-check observation;
- final operation outcome.

Storage/event representation belongs to Architecture and implementation.

## Ownership boundaries

- Authority Management owns mutation authority.
- APR owns source-neutral verified change intent.
- Provider Policy Renderer owns provider-specific representation and semantic-equivalence evidence.
- NEO owns controlled execution lifecycle and outcome.
- NEP owns enforcement-target relevance and placement meaning.
- Provider Policy Interpreter owns normalized configured effective-policy publication.
- TAE owns normalized source-qualified technical evidence.
- acquisition capabilities own source-specific collection and translation into TAE contracts.

Acquisition and NEO may share technical provider/device access infrastructure when Architecture chooses that realization, but shared infrastructure does not merge their semantic responsibilities.

## Invariants

1. One `operationId` binds exactly one target + artifact-digest intent.
2. Conflicting reuse of an operation id fails closed.
3. Identical retry does not repeat mutation.
4. Mutation cannot start before action-specific authority admission and successful pre-check.
5. Expected revision or base-target mismatch prevents mutation.
6. Concurrent revision change observed before apply prevents mutation.
7. Unknown apply outcome cannot be converted into success or blindly retried.
8. `Verified` requires an immediate post-check proving correspondence to the supplied artifact under the execution adapter contract.
9. Renderer/provider references and artifact digest are correlation/provenance, not policy-semantic identity.
10. NEO never rewrites APR or renderer semantics for device convenience.
11. Renderer failure or unsupported output cannot become an executable operation.
12. Final semantic convergence is external to the NetworkOperation outcome.
13. Operation-scoped reads do not make NEO the technical-evidence acquisition owner.
