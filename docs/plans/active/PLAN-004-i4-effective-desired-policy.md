# PLAN-004 — I4 effective desired-policy selection

Status: `active`

## Goal

Define and implement the minimum accepted Access Policy semantics for declarative effective conditions and authorized effective desired-policy selection at one logical `as-of`, without broadening Wave-1 Rule properties or prematurely introducing export/catalogue infrastructure.

## Current stage

I4 Domain/Application/Ports core is implemented and the core-only hosted gate passed. PostgreSQL adaptation is now admitted: persist EffectiveWindow + property audit atomically, support exact RuleGovernanceScope reads behind the application port, and prove stale/concurrent property mutation plus logical-as-of selection without moving effectiveness semantics into SQL.

Accepted Wave-1 truth establishes the predicate:

```text
contributes_effect =
    authoritative from Allowed
    AND operational state == Active
    AND supported declarative effective conditions permit at as-of
```

and requires effective read/export authority for the selected domain-policy scope.

Exact condition representation, property-change application behavior and selection-membership semantics remain intentionally under-specified and must be resolved before implementation.

## Inputs

Canonical inputs:

- `docs/requirements/wave1-product-requirements.md` — REQ-W1-006 and REQ-W1-008;
- `docs/requirements/wave1-acceptance-examples.md` — E8 and E11;
- `docs/requirements/wave1-quality-scenarios.md` — QS-06 and export-related scenarios;
- `docs/requirements/wave1-semantic-contracts.md` — C5 and C6;
- `docs/requirements/wave1-normalized-export-trace.md`;
- `docs/requirements/wave1-story-use-case-trace.md`;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/domain/ubiquitous-language.md`;
- `docs/architecture/wave1-domain-message-flows.md` — F3;
- `docs/architecture/wave1-context-definitions.md`;
- `docs/architecture/wave1-data-ownership.md`;
- `docs/engineering/wave1-first-implementation-backlog.md`;
- current Access Policy Domain/Application/Ports/PostgreSQL implementation and tests.

## Accepted behavior already fixed

- only authoritative Rules materialized from Allowed decisions participate;
- `Inactive` Rules never contribute desired effect;
- `Active` does not by itself guarantee current effect when a supported declarative condition is false;
- declarative operational conditions do not redefine RuleSemanticIdentity or Connectivity Decision subject;
- schedule/periodicity must not periodically toggle stored `Active/Inactive`;
- effective desired policy is evaluated for a logical `as-of`;
- selected but non-effective Rules are excluded before later technical projection;
- missing technical realization for a non-effective Rule does not make later export incomplete;
- selection/filter semantics are domain-policy semantics, not vendor/device syntax;
- read/export action requires effective Authority Management permission for scope/time.

## Bounded semantic decisions before code

### D1 — Minimum supported declarative condition set

Known:
- schedule/periodicity and supported frequency/duration are Wave-1 declarative Rule data;
- E8 requires at least one time-sensitive condition that is true for some `as-of` values and false for others.

Unknown:
- the smallest concrete condition vocabulary for the first implementation: absolute validity window, recurring schedule, frequency/duration, or a bounded combination.

Guardrail:
- do not implement a generic rule-expression engine or cron/calendar DSL without accepted evidence.

### D2 — Property assignment/change behavior

Known:
- declarative conditions belong to the authoritative AccessRule and do not change Rule identity or require a new Connectivity Decision by themselves.

Unknown:
- how an authorized actor sets/changes/removes these properties in Wave 1;
- whether property change is part of I4 command behavior and what business audit/provenance is required.

Guardrail:
- do not mutate Rule properties through direct repository/DB shortcuts.

### D3 — Domain-policy selection membership and authority scope

Known:
- actor selects a domain-policy subset;
- Authority Management evaluates read/export action for the selected policy scope;
- selection is domain-policy scoped.

Unknown:
- the minimum first selection shape;
- whether `RuleGovernanceScope` is also the selection-membership scope, or whether selection needs a distinct accepted policy-scope relation.

Guardrail:
- do not treat caller-supplied arbitrary filters as proof that selected Rules belong to an authorized scope.

## Work packages

1. Resolve D1-D3 at the highest affected requirements/Tactical DDD/application-contract layer.
2. Update Tactical DDD/semantic contracts/message flows only where the accepted meaning requires it.
3. Implement condition evaluation and effective-selection Domain/Application/Ports core with fakes/in-memory data.
4. Prove authority fail-closed, Active/Inactive behavior, condition true/false boundaries, logical `as-of` and selection isolation.
5. Close all P0/P1 core/model/authority/temporal findings and pass the core gate.
6. Only after core PASS, add the minimum PostgreSQL read/property persistence adaptation required by the accepted I4 behavior.
7. Record I4 PASS only after exact-candidate gates succeed.

## Exit criteria

- minimum supported declarative condition vocabulary is explicit and no broader than accepted Wave-1 needs;
- property assignment/change semantics are explicit or explicitly deferred with a viable I4 fixture/input boundary;
- domain-policy selection membership is explicit and cannot be authorization-substituted by caller filters;
- authority denied/unknown yields no effective-policy data;
- `Inactive` Rule is excluded regardless of condition;
- `Active` Rule with false condition is excluded;
- `Active` Rule with true/no restrictive condition is included when selected and authorized;
- evaluation uses the requested logical `as-of`, not wall-clock time hidden in Domain/Application;
- Rule identity/decision/governance semantics remain unchanged by condition evaluation;
- no export realization/catalogue facts are introduced prematurely;
- no open P0/P1 semantic, authority, temporal or architecture issue;
- I4 result is recorded in canonical engineering state.

## Accepted bounded decision

### R1 — First declarative condition: optional absolute EffectiveWindow

Implement exactly one first condition shape:

`EffectiveWindow(start, end)`

Semantics:
- both boundaries are explicit offset-aware instants;
- interval is half-open: `start <= asOf < end`;
- `start < end` is required;
- no condition means always effective subject to Allowed + Active;
- the condition does not mutate stored Active/Inactive state.

Explicitly defer recurring/calendar/cron/frequency-duration schedules until a concrete material Wave-1 example requires them. This satisfies E8 with the smallest testable temporal model and avoids inventing timezone/calendar recurrence semantics.

### R2 — Property mutation: SetRuleEffectiveWindow

Add authorized command:

`SetRuleEffectiveWindow(ruleId, window | None, actor, effectiveTime)`

Rules:
- use the Rule's stored RuleGovernanceScope for current Authority Management evaluation;
- stable action identity: `SetRuleEffectiveWindow`;
- changing/removing the window preserves RuleId, RuleSemanticIdentity, RuleGovernanceScope and Connectivity Decision;
- same value is no accepted change;
- accepted change is business-audited with RuleId, old/new window, actor, effective action time, governance scope and authority provenance/reference;
- property state + audit commit atomically;
- no new Connectivity Decision is required solely for this property change.

This is required to make REQ-W1-006 operational rather than only fixture/test data, and REQ-W1-013 already requires relevant Rule property history.

### R3 — First selection scope: RuleGovernanceScope

First I4 selection command:

`SelectEffectiveDesiredPolicy(scope, asOf, actor)`

Rules:
- stable authority action identity: `ReadEffectiveDesiredPolicy`;
- the requested `scope` is a RuleGovernanceScope;
- after permission is established for that scope/asOf, Access Policy selects authoritative Rules whose stored RuleGovernanceScope equals that scope;
- include only Rules that are Active and whose EffectiveWindow is absent or true at `asOf`;
- no arbitrary vendor/device/technical filters;
- first implementation selects one governance scope at a time; multi-scope composition may combine separately authorized selections later.

This reuses the already accepted stable Rule governance boundary and avoids inventing a second policy-scope taxonomy/mapping with no current evidence.

## Alternatives rejected for first I4 increment

- generic expression/cron/calendar rule engine — unsupported breadth;
- fixed recurring-period model — forces frequency/timezone/calendar semantics with no accepted example;
- declarative condition only in tests/fixtures — does not implement "maintain" property behavior or required property history;
- separate PolicySelectionScope entity/relation — new domain concept without evidence;
- arbitrary caller filters as selection membership — authorization-substitution risk.

## Blockers

None currently known.

## Validation

- living DDD/contract changes: `make knowledge-check`;
- active-plan/harness changes: `make harness-check`;
- core candidate: `make test`;
- PostgreSQL adaptation, if admitted after core PASS: `make postgres-test`;
- final multi-area candidate: `make check` plus any admitted PostgreSQL integration gate.

## Next

I5 — immutable coherent Export Snapshot assembly from Access Policy + Resource Catalogue + Application Communication Catalogue facts with fail-closed completeness behavior.
