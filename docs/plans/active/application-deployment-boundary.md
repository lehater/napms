# Application Deployment boundary convergence

Status: `audit completed on branch; validation/review remains before main`.

Date: 2026-09-15.

## Goal

Converge ACC/AD/RC ownership and minimum Resource network realization without speculative endpoint modelling.

## Executed

- [x] AD owns `ApplicationDeployment` and `ComponentPlacement`;
- [x] ACC owns Application/Component/Interaction only, not deployment/Resource binding;
- [x] RC owns Resource and at most one effective `AddressSpace = HostAddress | Prefix` per Resource/time;
- [x] AD binds `ComponentPlacement -> ResourceRef` only;
- [x] RPM uses AP + ACC + AD + RC + NEP public contracts;
- [x] old `DirectedInteractionIdentity` replaced by `GovernedInteractionSubject`;
- [x] multi-address/interface/VIP/exposure explicitly deferred;
- [x] repository-wide stale-reference audit completed and recorded in `docs/audits/application-deployment-stale-reference-audit-2026-09-15.md`;
- [x] target/canonical documentation corrected;
- [x] intentional runtime/history references classified;
- [x] obsolete active revalidation plan removed;
- [x] strategic-model validator aligned to current JSON projection;
- [ ] execute/review `make knowledge-check` evidence;
- [ ] ready-for-main decision.

## Current model

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

## Active S1 questions

1. What product constraints determine selectable source/destination ApplicationDeployment pairs for an Access Request?
2. If placement or Resource Scope Affiliation changes alter approval obligations, what happens to current authorization?
3. When several Responsibility Scopes apply to one governance side, what approval obligations are required?

AG Tactical G2 for the affected subject/obligation slice is not valid until these are resolved.

## Tactical follow-up

```text
ACC + RC -> AD -> AM -> affected BC/AG/AP convergence
```

Then continue RPM/NEP/TAE/APR/NEO. A future confirmed need for multiple addresses/interfaces reopens only the affected RC/AD/RPM edge.
