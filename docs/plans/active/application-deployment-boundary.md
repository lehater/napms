# Application Deployment boundary convergence

Status: `executed on branch; stale-reference audit and validation remain before main`.

Date: 2026-09-15.

## Goal

Converge ACC/AD/RC ownership and the minimum Resource network realization without speculative endpoint modelling.

## Plan

1. Add AD as owner of `ApplicationDeployment` and `ComponentPlacement`.
2. Remove deployment/Resource-binding ownership from ACC.
3. Keep RC authoritative for Resource identity, scope/responsibility and address realization.
4. Use the minimum current RC realization: one effective `AddressSpace = HostAddress | Prefix` per Resource/time.
5. Keep AD binding at `ComponentPlacement -> ResourceRef`; no endpoint/address selection in AD.
6. Route RPM through ACC traffic semantics + AD placements + RC Resource AddressSpace + NEP placement.
7. Replace old deployment-pair `DirectedInteractionIdentity` with `GovernedInteractionSubject` using InteractionContractRevision + source/destination ApplicationDeployment identities.
8. Keep multi-address/interface/VIP/deployment-specific exposure as future extension only when a confirmed use case requires it.
9. Audit remaining repository references to old ACC-owned deployment and ResourceEndpoint target semantics; classify target drift vs intentional legacy/current-state.
10. Validate canonical docs/JSON and CI evidence. Do not merge to `main` until review is complete.

## Executed

- [x] AD boundary introduced;
- [x] ACC deployment ownership removed from canonical target;
- [x] old RC -> ACC deployment binding superseded;
- [x] old `DirectedInteractionIdentity` superseded;
- [x] RC target realization simplified from ResourceEndpoint to Resource-level HostAddress-or-Prefix;
- [x] AD/RC network binding question closed for current scope;
- [x] ACC target model aligned;
- [x] application catalogue target requirements aligned with accepted AD split;
- [x] strategic-model.md, context-map.md and strategic-model.json aligned;
- [x] Tactical dependency order corrected to `ACC + RC -> AD -> AM`;
- [ ] repository-wide stale-reference audit completed;
- [ ] intentional legacy/current-state references marked where needed;
- [ ] branch validation/CI evidence reviewed;
- [ ] ready-for-main decision.

## Accepted current model

```text
ACC Component / InteractionContractRevision
        |
        v
AD ApplicationDeployment
   ComponentPlacement -> ResourceRef
        |
        v
RC Resource -> effective AddressSpace [0..1]
               AddressSpace = HostAddress | Prefix
```

No `ResourceEndpoint`, endpoint purpose, interface selection or deployment-specific exposure is part of the current target.

## Active S1 questions

1. What product constraints determine selectable source/destination ApplicationDeployment pairs for an Access Request?
2. If placement or Resource Scope Affiliation changes alter approval obligations, what happens to current authorization?
3. When several Responsibility Scopes apply to one governance side, what approval obligations are required?

## Tactical follow-up

Foundational order:

```text
ACC + RC -> AD -> AM -> affected BC/AG/AP convergence
```

Then continue RPM/NEP/TAE/APR/NEO. A future confirmed need for multiple addresses/interfaces reopens only the affected RC/AD/RPM edge rather than pre-loading endpoint abstractions now.