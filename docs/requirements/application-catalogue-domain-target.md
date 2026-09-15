# Application / Deployment / Resource requirements

Status: `accepted current target`.

## Scope

These requirements define application communication semantics and the ownership split between Application Communication Catalogue (ACC), Application Deployment (AD) and Resource Catalogue (RC).

## ACC

ACC shall:
1. model an Application as a reusable definition containing Components;
2. define each directed Interaction between a source Component and destination Component;
3. keep Interaction independent from deployment, Resource and address realization;
4. preserve decision-relevant traffic as immutable `InteractionContractRevision` snapshots;
5. require each revision to contain one or more vendor-neutral traffic alternatives;
6. treat the complete alternative set in one revision as one atomic communication contract;
7. publish stable opaque Application, Component, Interaction and InteractionContractRevision references.

## AD

AD shall:
1. model `ApplicationDeployment` as the stable logical deployment identity of one Application;
2. model `ComponentPlacement` as `(ComponentRef, ResourceRef)` within that deployment;
3. allow zero, one or many distinct Resource placements per Component;
4. preserve ApplicationDeployment identity across ordinary scaling, Resource migration and placement replacement while logical deployment continuity remains;
5. publish Resource references without copying Resource address realization.

## RC

RC shall:
1. own Resource identity and effective network AddressSpace;
2. expose at most one effective AddressSpace per Resource for the current scope;
3. represent AddressSpace as `HostAddress | Prefix`;
4. allow AddressSpace changes without changing Resource identity.

## Current relationship

```text
ACC Component
    -> AD ComponentPlacement
        -> ResourceRef
            -> RC AddressSpace [0..1]
                = HostAddress | Prefix
```

A Resource without a resolved current AddressSpace makes downstream technical materialization unresolved. A Prefix remains a Prefix unless a later consumer has an explicit supported interpretation.

## Invariants

- Interaction identity contains no deployment, Resource or address identity.
- Changing interaction traffic creates a new immutable contract revision.
- A consumer cannot silently use only a preferred subset of an atomic revision.
- ApplicationDeployment identity is independent from individual placements.
- A ComponentPlacement references exactly one Component and one Resource.
- Exact duplicate `(ComponentRef, ResourceRef)` pairs are invalid within one deployment.
- Address changes do not redefine Resource, ApplicationDeployment or Interaction identity.
- Cross-context persistence must not depend on database foreign keys into another BC's private schema.
