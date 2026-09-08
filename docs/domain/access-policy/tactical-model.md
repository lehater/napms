# Access Policy tactical model

Status: `accepted D2 model for first Walking Skeleton`.

Date: 2026-09-08.

## Scope

Only the Access Policy consistency model required for proposal decision consumption and idempotent Rule materialization is designed here. Deferred Decision Domain, catalogue aggregates and later-wave models are not designed.

## Value objects

### RuleSemanticIdentity

Immutable value:

`SourceComponentDeploymentId + DestinationComponentDeploymentId + DcsContractRevisionId`

Equality is structural over those three stable identities. Technical address realization, actor ownership and operational schedule are not members.

### ConnectivityDecisionRef

Carries exact `RuleSemanticIdentity`, `Allowed|NotAllowed`, and opaque decision/provenance reference where available. It does not expose internal decision policy/workflow.

## Entity / aggregate boundary

### AccessRule

Aggregate root and authoritative business identity:
- `RuleId` stable surrogate identity;
- immutable `RuleSemanticIdentity`;
- `OperationalState = Active|Inactive`;
- Connectivity Decision correlation/provenance;
- audit/provenance required by accepted behavior;
- later supported declarative operational properties.

Invariant: semantic identity cannot change after materialization.

## Materialization domain operation

`materialize_or_resolve(AllowedDecision)` is an application/domain operation over the Access Policy authoritative repository/transaction boundary:

1. reject any decision not Allowed;
2. verify decision subject is the exact proposed semantic identity supplied by the use case;
3. find Rule by unique semantic identity;
4. if found, return existing Rule unchanged;
5. otherwise create Rule with new RuleId, state Active and decision correlation;
6. commit under authoritative uniqueness constraint on RuleSemanticIdentity;
7. on concurrent uniqueness race, resolve the winning existing Rule and return the same RuleId if its identity is exact.

The database uniqueness constraint is a persistence enforcement of the domain invariant, not the source of its meaning.

## Commands for first skeleton

- `SubmitAccessRuleProposal(sourceDeploymentId, destinationDeploymentId, dcsRevisionId, actor, scope, effectiveTime)`;
- internal application step `ConsumeConnectivityDecision(proposalSubject, decision)`;
- `MaterializeOrResolveAllowedRule(subject, decisionRef)`.

No domain event is required merely for ceremony. An auditable materialization record may be emitted/persisted if needed by the chosen implementation; event-driven topology is not implied.

## Concurrency

Correctness requirement is linearizable enough at the Access Policy authoritative uniqueness boundary that concurrent/retried Allowed materializations for the same semantic identity yield one RuleId and no duplicate authoritative Rules.

Implementation may use unique key + transaction/upsert/retry, serializable operation or equivalent. Exact database mechanism belongs WP-03/engineering design.

## Errors / non-results

- authority denied/unknown -> proposal action rejected before materialization;
- structurally invalid/unknown interaction -> no valid proposal;
- decision NotAllowed -> no Rule;
- decision subject mismatch -> invariant violation/rejected operation;
- persistence/transient failure -> no reported successful materialization unless authoritative Rule can be resolved consistently.

## Later model growth

Active<->Inactive transition and declarative operational properties extend the same AccessRule aggregate when their implementation increment begins. Export reads Access Policy state but does not mutate Rule identity.