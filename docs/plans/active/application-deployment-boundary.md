# Application Deployment boundary convergence

Status: `executed on branch; review/audit pending before main`.

Date: 2026-09-15.

## Goal

Apply the accepted Application Deployment Boundary Challenge without leaking Tactical implementation choices into Strategic DDD.

## Plan

1. Add **Application Deployment (AD)** as the target owner of logical `ApplicationDeployment` identity/lifecycle and Component-to-Resource placement truth.
2. Remove deployment/placement ownership from **Application Communication Catalogue (ACC)** while retaining Application, Component, Interaction and immutable traffic-contract ownership.
3. Keep **Resource Catalogue (RC)** authoritative for Resource identity/lifecycle, responsibility/scope and technical realization.
4. Re-route affected Context Map edges: add ACC -> AD, RC -> AD, AD -> AG, AD -> RPM and AM -> AD; remove RC -> ACC deployment binding; narrow ACC -> AG/RPM.
5. Replace deployment-pair `DirectedInteractionIdentity` with the strategic `GovernedInteractionSubject` composed from ACC InteractionContractRevision identity and source/destination AD ApplicationDeployment identities.
6. Keep exact AD/RC network exposure and endpoint shape Tactical-open; do not promote `ResourceEndpointRef`, `DeploymentEndpointBinding`, Environment, listener/interface, VIP or provider runtime concepts without use-case evidence.
7. Promote governance behavior exposed by migration/scope changes to active S1 questions instead of inventing policy in Tactical DDD.
8. Align `strategic-model.md`, `context-map.md` and `strategic-model.json`.
9. Audit remaining documentation/code references to old ACC-owned deployment semantics and classify them as target-documentation drift versus intentional legacy/runtime state.
10. Do not merge/push to `main` until review and audit are complete.

## Executed changes

- [x] branch `strategic/application-deployment-boundary` created from `main`;
- [x] `strategic-model.md` updated to eleven target BCs and new ownership;
- [x] `strategic-model.json` updated with participant/edge/invariant projection;
- [x] `context-map.md` updated with affected-edge contracts and Mermaid flow;
- [x] old strategic `RC -> ACC` deployment binding superseded;
- [x] old ACC-owned `DirectedInteractionIdentity` superseded;
- [x] S1 governance questions made explicit;
- [x] Tactical-open network contract kept intentionally unresolved;
- [ ] repository-wide stale-reference audit completed;
- [ ] affected documentation classified/updated;
- [ ] branch validation/CI evidence reviewed;
- [ ] ready-for-main decision.

## Accepted minimal AD semantics

```text
ApplicationDeployment
    ApplicationDeploymentId
    ApplicationRef

ComponentPlacement
    ApplicationDeploymentRef
    ComponentRef
    ResourceRef
```

Identity rule: an `ApplicationDeployment` preserves identity while continuity of the same logical deployment is preserved; ordinary scaling, migration and Component placement replacement do not alone create a new identity.

`ComponentPlacement` is an access-domain placement fact, not automatically a process/container/pod/provider runtime instance.

## Active S1 questions

1. What product constraints determine which source/destination `ApplicationDeployment` pair may be selected for an Access Request?
2. If placement or Resource Scope Affiliation changes alter approval obligations, does existing authorization remain valid, require reapproval, warn, or withdraw?
3. When several Responsibility Scopes apply to one governance side, what approval obligations are required?

## Tactical follow-up

After strategic documentation and stale-reference audit converge, resume Tactical DDD in the order:

```text
RC -> AD -> ACC -> affected AG/AP contract convergence
```

Then continue downstream RPM/NEP/TAE/APR/NEO work. The exact RC/AD network-exposure contract must be discovered from use cases rather than inferred from the former `ResourceEndpoint` model.
