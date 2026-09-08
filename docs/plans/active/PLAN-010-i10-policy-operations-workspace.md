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

**WP8 — final architecture/security review and repository gates.**

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

1. **DONE — Contract/admission refinement.** Canonical HTTP/UI contracts admit EffectiveWindow mutation and asOf-bound policy-view scope discovery.
2. **DONE — Rule details capability.** Independent SetRuleEffectiveWindow admission is exposed alongside state mutation admission.
3. **DONE — EffectiveWindow HTTP slice.** PATCH route and runtime tests cover set/change/clear/same-value/denied/invalid/spoofing semantics.
4. **DONE — Effective Desired Policy HTTP slice.** Application-level scope discovery and effective-policy endpoint are implemented with explicit asOf.
5. **DONE — Web UI — Rule EffectiveWindow.** Rule Details support set/change/clear and EffectiveWindow history.
6. **DONE — Web UI — Policy Views.** Effective and Normalized Policy screens preserve explicit scope/asOf and normalized provenance semantics.
7. **DONE — Runtime/PostgreSQL evidence.** End-to-end EffectiveWindow -> selection -> normalized export is covered through PostgreSQL.
8. **ACTIVE — Final review/gates.** Run core, PostgreSQL, Web, harness and knowledge gates; close all P0/P1.

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

Run final architecture/security review and all repository gates; close P0/P1 before I10 absorption.
