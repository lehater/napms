# Active execution

Current: `domain-erd-revalidation.md` — bounded-context discovery/model revalidation before implementation.

Goal: identify and lock target domain problems/models context by context, preserve unresolved future work as context-local problem registers, and avoid implementing against unresolved or obsolete semantics.

Current task: no bounded-context slice is actively being advanced on this branch. The NEP slice is checkpointed after `G1 PASS`; another bounded context may be selected independently.

Lifecycle stage: `S2`

Stage state: `NOT_STARTED`

Lifecycle basis: NEP `S0/G0` and `S1/G1` are complete for the current slice; `docs/requirements/network-enforcement-placement-core.md` is the canonical accepted S1 owner. S2 Domain Design has not yet been revalidated against those requirements.

Implementation authorization: `none`

Authorized scope: `none`

Authorization basis: `none`

## Working set

Read first:
- `docs/plans/active/domain-erd-revalidation.md`
- `docs/engineering/context-problems/README.md`

Expand only when the selected bounded-context slice requires it. If NEP is resumed, additionally read:
- `docs/requirements/network-enforcement-placement-core.md`
- `docs/domain/network-enforcement-placement/target-tactical-model.md`
- `docs/architecture/network-enforcement-placement-boundary.md`
- `docs/process/domain-design-stage.md`

## NEP recovery facts

- `S0 Problem/Evidence` passed G0 for this slice.
- Accepted problem: for each technical source/destination pair, determine every known Firewall that is a candidate enforcement location and the ACL/policy names where that pair may be affected. Candidate relevance is not proof of an end-to-end forwarding path.
- `S1 Requirements` passed G1. The accepted behavior is in `docs/requirements/network-enforcement-placement-core.md`.
- The public result is `TrafficPairResult -> EnforcementLocation[0..N]`, where each location contains `firewallId`, `accessListNames[0..N]` and metadata with `snapshotCollectedAt?` plus `decisionSource`.
- Candidate membership uses `Include > Exclude > Routing`; routing alternatives/VRFs/ECMP are all considered, and a routing-independent Include may create a candidate even with no network snapshot.
- A candidate remains in the result even with no ACL/policy name.
- Snapshot staleness is diagnostic only in MVP; the latest successful usable state continues to drive the result and its freshness is exposed downstream.
- Local branches/interfaces/attachment topology are decision evidence, not required public output for this use case.
- NEP owns enforcement-location selection, not ACL bodies, desired policy change, reconciliation, rendering or execution.
- No runtime migration or implementation is authorized.

## Later-stage design input discovered during S1

The user explicitly preferred routing/interface facts and ACL binding/name facts for this use case to be refreshed together so that the result has one coherent freshness date rather than mixed-age decision data.

This is **not an S1 implementation requirement**. S1 requires truthful, unambiguous freshness provenance in the observable result. The acquisition coordination mechanism — one logical refresh/poll, session/command arrangement, storage swap and related realization — belongs to S3 Architecture/Design and must be revalidated there rather than being silently promoted into Requirements.

## Harness evidence from this slice

The NEP S1 discussion exposed a Harness defect: an explicit user proposal about realization can be incorrectly written as a higher-level requirement. The corresponding Harness correction is isolated on branch `harness/semantic-level-classification`; it classifies statements independently by semantic owner/stage and by decision status/obligation.

## Other recovery facts

- Access Policy Realization remains parked and is not active execution.
- APR unresolved future work remains at `docs/engineering/context-problems/access-policy-realization.md`.
- A parked context or completed gate does not authorize implementation.
- Another bounded-context slice may enter S0/S1 while NEP waits at S2; lifecycle progression is scoped per slice rather than globally synchronized across contexts.

## Blockers

No repository blocker. NEP can resume at S2 when selected; another bounded context can be selected and started independently.

## Gate

`NEP G1 PASS`. Next NEP gate is G2 after Domain Design revalidation. There is no G4 implementation lease.

## Next

Select the next bounded-context slice. If NEP is resumed, start from S2 and compare the existing domain model/ADR against the newly accepted S1 requirements instead of assuming the previous NEP target model remains valid unchanged.
