# Active execution

Current: `required-policy-materialization-mvp.md`
Goal: continue the thin MVP vertical path from accepted Access Governance and Access Policy semantics into one target-specific technical required-policy result consumable by APR.
Current task: converge the minimum `TargetRequiredPolicy` shape and unresolved semantics for one currently authorized governed interaction.
Lifecycle stage: `S2`
Stage state: `IN_PROGRESS`
Lifecycle basis: accepted Access Governance G1 behavior, revalidated AG/AP Tactical checkpoints, and ADR-020 derived-composition ownership.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## MVP execution rule

Build the smallest working end-to-end happy path, not a feature-complete domain model. Define only semantics required by that path; preserve stable context boundaries, identities and public contracts; defer revisions, richer lifecycle/state machines, migration machinery, optimization and edge-case semantics until concrete pressure appears. Prefer a thin vertical path across contexts over completing each context in depth first.

Current progression:

```text
ACC + RC -> AD
        -> AG bilateral authorization
        -> AP current semantic Policy Rule
        -> RPM TargetRequiredPolicy
        -> APR comparison
```

## Completed checkpoint

Access Governance S1/S2 MVP work is complete for the current path:

- Q1 deployment-pair selection accepted;
- Q2 material obligation-change withdrawal/regrant behavior accepted;
- Q3 overlapping Responsibility Scopes are fail-closed/unsupported in the MVP happy path;
- `AccessRequest` historical truth is separated from current `GovernedAuthorization` truth;
- AP consumes only `AuthorizationGranted` / `AuthorizationWithdrawn` and needs no extra obligation-change state.

Broader multi-scope governance semantics remain deliberately deferred and do not block this path.

## Working set

Read first:

- `docs/plans/active/required-policy-materialization-mvp.md`
- `docs/decisions/ADR-020-required-policy-materialization-is-derived-composition.md`
- `docs/domain/access-policy/tactical-model.md`
- `docs/domain/application-deployment/boundary.md`
- `docs/domain/resource-catalogue/tactical-model.md`
- `docs/domain/network-enforcement-placement/target-tactical-model.md`

Expand to ACC/APR documents only when the concrete materialization contract requires them.

## Current baseline

```text
AP effective Policy Rule
+ ACC Interaction traffic semantics
+ AD ComponentPlacements -> ResourceRefs
+ RC ResourceRef -> HostAddress | Prefix
+ NEP FirewallCandidate -> AccessListLocator[]
        |
        v
RPM TargetRequiredPolicy | unresolved
        |
        v
APR
```

RPM is a derived composition, not a peer Bounded Context. Missing/ambiguous input must remain explicit unresolved state and must not be collapsed into empty required policy.

## Gate

No current S1 Access Governance blocker remains for the first happy path.

The current work is semantic composition only. No implementation authorization exists.

## Next

Define the minimum deterministic `TargetRequiredPolicy` output for one authorized interaction and the exact conditions that produce `unresolved`, then revalidate the APR handoff.
