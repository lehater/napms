# Access Governance MVP Tactical revalidation

Status: `active S2 MVP Tactical revalidation`.

Date: 2026-09-15.

## Goal

Revalidate the minimum Access Governance Tactical DDD model against the accepted MVP G1 behavior without introducing implementation machinery or broader governance features.

## Accepted inputs

The S1 checkpoint now establishes:

- governed subject = `InteractionContractRevisionRef + sourceApplicationDeploymentRef + destinationApplicationDeploymentRef`;
- a selectable pair must realize the corresponding Interaction endpoint Components;
- current placements/scope facts must resolve approval obligations;
- MVP requires exactly one distinct applicable Responsibility Scope per governance side;
- source and destination obligations are independent and both are required for grant;
- either pending side may reject;
- either authorized side may later withdraw its current consent;
- a material change of current approval obligations withdraws current authorization;
- unchanged obligations preserve current authorization;
- historical approvals never silently restore withdrawn authorization;
- AP consumes only `AuthorizationGranted` / `AuthorizationWithdrawn`.

## Current Tactical task

Define only the semantic roots/value objects/invariants needed to represent:

1. immutable Access Request history and approval basis;
2. one source-side and one destination-side Approval Obligation for the MVP;
3. historical approve/reject decisions with Authority Management evidence;
4. current effective authorization independently from historical Requests;
5. withdrawal/regrant behavior when consent or current obligations change;
6. the AG -> AP grant/withdrawal handoff.

Do not define persistence tables, REST shapes, queues, retries, optimistic-lock fields, generalized scope precedence, multi-scope approval algebra or a separate Suspended state.

## Exit criteria

- `docs/domain/access-governance/target-tactical-model.md` is aligned with accepted Q1/Q2/Q3;
- historical Request truth is separated from current authorization truth;
- no stale Request/approval can silently reactivate authorization;
- obligation-change behavior can be expressed without changing governed-subject identity;
- AP handoff remains only `AuthorizationGranted` / `AuthorizationWithdrawn`;
- remaining unknowns are explicitly deferred and non-blocking for the first happy path;
- no implementation authorization is implied.

## Next

Complete the Tactical revalidation, then revalidate the affected Access Policy edge and continue the thin vertical MVP path.
