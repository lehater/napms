# PLAN-010 — I10 Policy Operations Workspace

Status: `active`

## Goal

Complete the next operator-facing policy workspace slice without introducing new domain semantics:

```text
Access Rule Details
  -> Set / change / clear EffectiveWindow

Policy Views
  -> Effective Desired Policy(scope, asOf)
  -> Normalized Policy(scope, asOf)
```

I10 must reuse existing Access Policy, Authority Management, snapshot and normalization semantics.

## Current stage

**WP1 — admit policy-view scope discovery and HTTP/UI contracts.**

No new Authority action is required:
- EffectiveWindow mutation uses existing `SetRuleEffectiveWindow`;
- Effective Desired Policy and Normalized Policy use existing `ReadEffectiveDesiredPolicy`.

## Inputs

- `docs/engineering/current-state.md`;
- `docs/domain/access-policy/tactical-model.md`;
- `docs/requirements/wave1-semantic-contracts.md`;
- `docs/requirements/web-ui-requirements.md`;
- `docs/engineering/http-api-contract.md`;
- existing `SetAccessRuleEffectiveWindow`;
- existing `SelectAccessPolicyEffectiveDesiredPolicy`;
- existing normalized-policy HTTP handoff;
- I9 Access Rule workspace and session/runtime trust boundary.

## Accepted constraints

- actor identity comes only from authenticated session;
- mutation effective time comes only from runtime clock;
- Rule governance scope comes only from the authoritative Rule;
- EffectiveWindow uses offset-aware instants and half-open `[start, end)` semantics;
- `start < end` is required;
- clearing EffectiveWindow means no time-window restriction;
- policy views require explicit `scope` and explicit offset-aware `asOf`;
- denied/unknown policy-read authority returns no policy data;
- authorized empty effective policy is distinct from denied/unknown;
- normalized-policy presentation must preserve `Any`, `NotApplicable`, inclusive ranges and provenance;
- no approval/request lifecycle is introduced.

## Work packages

1. **ACTIVE — Contract/admission refinement.** Add policy-view scope discovery and admit EffectiveWindow mutation/effective-policy HTTP/UI surfaces in canonical contracts.
2. **Rule details capability.** Expose independent `SetRuleEffectiveWindow` admission alongside existing state mutation admission.
3. **EffectiveWindow HTTP slice.** Add PATCH route using trusted session actor/runtime time/stored Rule scope; prove set/change/clear/same-value/denied/unknown/invalid/persistence paths.
4. **Effective Desired Policy HTTP slice.** Add policy-scope discovery and effective-policy endpoint over the existing application query.
5. **Web UI — Rule EffectiveWindow.** Add set/change/clear controls and business history on Rule Details.
6. **Web UI — Policy Views.** Add Effective Policy and Normalized Policy navigation/screens with explicit scope + asOf and safe empty/error states.
7. **Runtime/PostgreSQL evidence.** Prove end-to-end EffectiveWindow mutation/evaluation and normalized-policy view through PostgreSQL.
8. **Final review/gates.** Run core, PostgreSQL, Web, harness and knowledge gates; close all P0/P1.

## Exit criteria

- browser can set/change/clear EffectiveWindow on an authorized Rule;
- Rule details show independent state/window mutation capabilities;
- Effective Desired Policy UI returns only authorized effective Rules for one scope/asOf;
- Normalized Policy UI preserves accepted normalized semantics/provenance;
- no caller-controlled actor/time/scope can bypass mutation authority;
- invalid/naive EffectiveWindow or asOf input fails explicitly rather than as 500;
- Domain/Application remain framework-independent;
- all repository gates are green;
- no open P0/P1 finding.

## Blockers

No current owner/product blocker.

## Next

Update canonical HTTP/UI contracts, then implement independent EffectiveWindow capability and transport tests before Web UI changes.
