# Access Policy tactical model

Status: `accepted D2 model through I4 effective-policy semantics`.

Date: 2026-09-08.

## Scope

This model defines the Access Policy consistency model required for proposal decision consumption, idempotent Rule materialization, authorized `Active <-> Inactive` mutation, the first declarative effective condition and effective desired-policy selection. Deferred Decision Domain, catalogue aggregates, recurring schedule semantics and normalized export projection are not designed here.

## Value objects

### RuleSemanticIdentity

Immutable value:

`SourceComponentDeploymentId + DestinationComponentDeploymentId + DcsContractRevisionId`

Equality is structural over those three stable identities. Technical address realization, actor ownership, governance scope and operational schedule are not members.

### ConnectivityDecisionRef

Carries exact `RuleSemanticIdentity`, `Allowed|NotAllowed`, and opaque decision/provenance reference where available. It does not expose internal decision policy/workflow.

### RuleGovernanceScope

Stable non-identity scope under which Authority Management evaluates actions on one authoritative AccessRule.

For materialization from `SubmitAccessRuleProposal`, the accepted proposal `authorityScope` becomes the materialized Rule's `RuleGovernanceScope`.

Rules:
- it is not part of `RuleSemanticIdentity`;
- later assignment/delegation/transfer/revocation changes which actors are authorized for that scope without silently changing the Rule's governance scope;
- ownership/responsibility changes do not silently rebind Rule governance scope;
- a later operation cannot substitute caller-supplied scope for the Rule's stored governance scope.

### EffectiveWindow

Optional absolute time condition on one AccessRule:

`EffectiveWindow(start, end)`

Invariants:
- `start` and `end` are offset-aware instants;
- `start < end`;
- it permits effect exactly when `start <= asOf < end`;
- absence means no time-window restriction;
- it does not mutate stored OperationalState.

Recurring/calendar/cron/frequency-duration semantics are not part of the first I4 condition vocabulary.

## Entity / aggregate boundary

### AccessRule

Aggregate root and authoritative business identity:
- `RuleId` stable surrogate identity;
- immutable `RuleSemanticIdentity`;
- stable non-identity `RuleGovernanceScope`;
- `OperationalState = Active|Inactive`;
- Connectivity Decision correlation/provenance;
- proposal/authority/catalogue provenance;
- business audit/provenance required by accepted behavior;
- optional `EffectiveWindow`;
- EffectiveWindow property-change audit/history.

Invariants:
- semantic identity cannot change after materialization;
- Rule governance scope does not silently change through actor/ownership/responsibility changes;
- operational-state transition preserves RuleId, RuleSemanticIdentity, RuleGovernanceScope and Connectivity Decision correlation;
- setting/changing/removing EffectiveWindow preserves the same identities/decision;
- EffectiveWindow evaluation is pure for an explicit logical `asOf` and does not consult hidden wall-clock time.

## Materialization domain operation

`materialize_or_resolve(AllowedDecision)` is an application/domain operation over the Access Policy authoritative repository/transaction boundary:

1. reject any decision not Allowed;
2. verify decision subject is the exact proposed semantic identity supplied by the use case;
3. find Rule by unique semantic identity;
4. if found, return existing Rule unchanged;
5. otherwise create Rule with new RuleId, state Active, accepted proposal authority scope as RuleGovernanceScope and decision correlation;
6. commit under authoritative uniqueness constraint on RuleSemanticIdentity;
7. on concurrent uniqueness race, resolve the winning existing Rule and return the same RuleId if its identity is exact.

The database uniqueness constraint is a persistence enforcement of the domain invariant, not the source of its meaning.

## Operational-state mutation

Semantic command:

`SetRuleOperationalState(ruleId, Active|Inactive)`

Application/domain behavior:

1. load the authoritative Rule by RuleId;
2. evaluate current/effective Authority Management permission for action `SetRuleOperationalState` using the Rule's stored `RuleGovernanceScope` and requested effective time;
3. denied/unknown authority fails closed and produces no state/audit mutation;
4. target state equal to current state produces explicit `AlreadyInRequestedState`; it is not an accepted transition and creates no audit record;
5. `Active -> Inactive` and `Inactive -> Active` are the only accepted transitions;
6. accepted transition preserves RuleId, RuleSemanticIdentity, RuleGovernanceScope and Connectivity Decision correlation;
7. accepted transition records business audit/provenance sufficient to reconstruct who/when/what: RuleId, from state, to state, actor, effective action time, evaluated RuleGovernanceScope and Authority Management provenance/reference;
8. state change and its audit record belong to one authoritative persistence transaction; failure cannot be reported as successful mutation.

A technical log timestamp is not a substitute for the effective business action time/audit record.

## EffectiveWindow mutation

Semantic command:

`SetRuleEffectiveWindow(ruleId, window|None, actor, effectiveTime)`

Behavior:

1. load authoritative Rule by RuleId;
2. evaluate Authority Management action `SetRuleEffectiveWindow` using the stored RuleGovernanceScope and effective action time;
3. denied/unknown/missing authority provenance fails closed;
4. requested value equal to current value returns explicit no accepted change and creates no audit;
5. accepted change preserves RuleId, RuleSemanticIdentity, RuleGovernanceScope, OperationalState and Connectivity Decision correlation;
6. accepted change records RuleId, old/new window, actor, effective action time, governance scope and authority provenance/reference;
7. property change and its audit commit atomically;
8. no new Connectivity Decision is required solely for this property change.

## Effective desired-policy selection

Semantic query/application command:

`SelectEffectiveDesiredPolicy(scope, asOf, actor)`

where `scope` is one RuleGovernanceScope.

Behavior:

1. Authority Management evaluates action `ReadEffectiveDesiredPolicy` for the requested scope and `asOf`;
2. denied/unknown/missing authority provenance returns no policy data;
3. Access Policy considers only authoritative Rules whose stored RuleGovernanceScope equals the authorized requested scope;
4. an `Inactive` Rule is excluded;
5. an `Active` Rule with no EffectiveWindow is included;
6. an `Active` Rule with EffectiveWindow is included exactly when `start <= asOf < end`;
7. the first implementation selects one governance scope at a time and accepts no arbitrary vendor/device/technical membership filters.

This is an Access Policy semantic selection only; Resource Catalogue/Application Communication Catalogue realization and normalized rows belong to later increments.

## Commands

- `SubmitAccessRuleProposal(sourceDeploymentId, destinationDeploymentId, dcsRevisionId, actor, scope, effectiveTime)`;
- internal application step `ConsumeConnectivityDecision(proposalSubject, decision)`;
- `MaterializeOrResolveAllowedRule(subject, decisionRef)`;
- `SetRuleOperationalState(ruleId, targetState, actor, effectiveTime)`;
- `SetRuleEffectiveWindow(ruleId, window|None, actor, effectiveTime)`;
- `SelectEffectiveDesiredPolicy(scope, asOf, actor)`.

No domain event is required merely for ceremony. Event-driven topology is not implied.

## Concurrency

Correctness requirement for materialization is linearizable enough at the Access Policy authoritative uniqueness boundary that concurrent/retried Allowed materializations for the same semantic identity yield one RuleId and no duplicate authoritative Rules.

Operational-state and EffectiveWindow mutations each require one authoritative transactional write boundary so business property state and the corresponding accepted-change audit are committed together. Detailed optimistic/pessimistic locking mechanics are infrastructure choices unless evidence requires stronger semantics.

## Errors / non-results

- authority denied/unknown -> action rejected;
- structurally invalid/unknown interaction -> no valid proposal;
- decision NotAllowed -> no Rule;
- decision subject mismatch -> invariant violation/rejected operation;
- unknown Rule for state mutation -> explicit not-found outcome, no audit;
- same operational state requested -> explicit `AlreadyInRequestedState`, no audit;
- same EffectiveWindow requested -> explicit no accepted property change, no audit;
- denied/unknown effective-policy read authority -> no selected policy data;
- persistence/transient failure -> no reported successful materialization or mutation unless authoritative outcome is established consistently.

## Later model growth

Recurring schedule/periodicity semantics remain deferred until a material accepted example requires them. Normalized export reads effective Access Policy selection but does not mutate Rule identity.
