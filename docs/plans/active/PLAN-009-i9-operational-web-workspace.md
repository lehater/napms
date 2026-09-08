# PLAN-009 — I9 Operational Web Workspace

Status: `active`

## Goal

Turn the I8 Web UI from a proposal-only vertical slice into the first operational Access Policy workspace without expanding into the deferred Connectivity Decision/approval domain.

Primary user outcome:

```text
Access Rules list
  -> Rule Details
  -> admitted Active / Inactive change
```

Follow-on I9 slices may add EffectiveWindow, Effective Desired Policy UI and Normalized Policy UI only after the first workspace slice is proven.

## Current stage

**WP1 — resolve workspace read authority semantics before implementation.**

The workspace must not reuse mutation authority as implicit read authority and must not expose authoritative Rule data before an explicit backend authorization decision.

## Inputs

- `docs/engineering/current-state.md`;
- `docs/requirements/web-ui-requirements.md`;
- `docs/ui/`;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/requirements/wave1-story-use-case-trace.md`;
- `docs/architecture/wave1-domain-message-flows.md`;
- `docs/engineering/http-api-contract.md`;
- existing `SetRuleOperationalState` application behavior and PostgreSQL repository;
- I8 HTTP/runtime/session boundary and React application shell.

## Decision gate

### D1 — Access Rule workspace read authority — OPEN

Current accepted Authority vocabulary contains:
- `ProposeConnectivity`;
- `SetRuleOperationalState`;
- `SetRuleEffectiveWindow`;
- `ReadEffectiveDesiredPolicy`.

There is no accepted authority action for listing or viewing authoritative Access Rules including inactive/out-of-window Rules.

Recommended decision:
- add explicit `ReadAccessRule` authority;
- evaluate it against each Rule's stored `RuleGovernanceScope`;
- list queries return only Rules from scopes where the actor has unambiguous effective `ReadAccessRule` authority;
- details fail closed when the actor lacks/has ambiguous read authority;
- read authority does not imply mutation authority;
- mutation buttons are admitted independently by the existing `SetRuleOperationalState` authority check.

This is an Authority/Access Policy semantic extension and must be accepted before core implementation.

## Planned work packages

1. **ACTIVE — Read authority decision.** Resolve D1 and update canonical Authority/Access Policy/UI requirements if accepted.
2. **Access Rule read-side.** Add core application queries/ports for authorized list and details; no HTTP/framework dependency.
3. **HTTP contract.** Add use-case-oriented list/details/state routes and stable semantic mappings.
4. **State mutation HTTP slice.** Attach trusted session actor/runtime time to existing `SetRuleOperationalState`; preserve stored governance scope and audit semantics.
5. **Web UI workspace.** Add Access Rules navigation, server-backed list, Rule Details and admitted Active/Inactive action.
6. **Runtime/DB evidence.** Prove positive, denied, unknown, not-found, already-in-state and persistence-failure paths.
7. **Final review/gates.** Run core, PostgreSQL, Web, harness and knowledge gates; close P0/P1.

## Exit criteria

- Access Rule list/details use explicit accepted read authority and fail closed;
- read authorization does not imply state-mutation authorization;
- list/details expose authoritative Rule semantics without DB CRUD leakage;
- state mutation uses the existing accepted application/domain command and business audit;
- browser can navigate list -> details -> Active/Inactive through real HTTP/PostgreSQL boundaries;
- no approval/request-lifecycle semantics are introduced;
- Domain/Application remain framework-independent;
- all repository gates green;
- no open P0/P1 findings.

## Blockers

D1 is the only current product/domain blocker.

## Next

Resolve D1. If accepted, update canonical semantic truth first, then implement the read-side core and tests before HTTP/Web adapters.
