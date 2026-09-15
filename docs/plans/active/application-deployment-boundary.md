# Application Deployment boundary convergence

Status: `active MVP foundational tactical convergence`.

Date: 2026-09-15.

## Goal

Converge the minimum ACC/RC/AD semantics required for the first end-to-end happy path while preserving context ownership and stable identities. Defer speculative lifecycle, revision, migration, optimization and edge-case machinery until a concrete requirement needs it.

## Inputs

- accepted strategic ownership: ACC owns Application/Component/Interaction, AD owns ApplicationDeployment/ComponentPlacement, RC owns Resource realization;
- accepted AD binding: `ComponentPlacement -> ResourceRef`;
- accepted current RC realization: at most one effective `AddressSpace = HostAddress | Prefix` per Resource;
- accepted MVP ACC target in `docs/domain/application-communication-catalogue/target-model.md`;
- known AG S1 questions remain downstream blockers and are not to be solved speculatively here.

## Executed

- [x] AD owns `ApplicationDeployment` and `ComponentPlacement`;
- [x] ACC owns Application/Component/Interaction only, not deployment/Resource binding;
- [x] RC owns Resource and at most one effective `AddressSpace = HostAddress | Prefix` per Resource/time;
- [x] AD binds `ComponentPlacement -> ResourceRef` only;
- [x] multi-address/interface/VIP/exposure explicitly deferred;
- [x] repository-wide stale-reference audit recorded in `docs/audits/application-deployment-stale-reference-audit-2026-09-15.md`;
- [x] minimal MVP ACC target checkpointed;
- [x] MVP execution rule established: thin happy path first, deeper modelling only under demonstrated pressure.

## Current model

```text
ACC Application / Component / Interaction
        |
        v
AD ApplicationDeployment
   ComponentPlacement -> ResourceRef
        |
        v
RC Resource -> effective AddressSpace [0..1]
               AddressSpace = HostAddress | Prefix
```

## Exit criteria

- active resume capsule passes Harness plan validation;
- MVP ACC decision is durable in canonical target documentation;
- current ACC/RC/AD ownership remains non-contradictory;
- next session can start minimal RC Tactical modelling without reopening deferred ACC extensions;
- no implementation authorization is implied by this plan.

## Blockers

No blocker prevents this documentation checkpoint from merging.

Downstream Access Governance still has S1 behavior questions about selectable ApplicationDeployment pairs, authorization after placement/scope changes, and overlapping Responsibility Scopes. They become blocking only when the thin vertical slice reaches the affected governance behavior.

## Next

Start with the minimal Resource Catalogue Tactical model, then immediately revalidate the minimal Application Deployment model against ACC + RC. Continue the smallest downstream governance/network/policy path required to produce a working rule; defer deeper modelling until the happy path exposes a concrete gap.
