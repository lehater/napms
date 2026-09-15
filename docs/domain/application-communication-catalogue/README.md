# Application Communication Catalogue domain

## Current target

Current ACC target authority:

- `target-model.md` — strategic target shape for Application / Component / Interaction / immutable traffic contracts;
- `target-tactical-model.md` — current MVP Tactical DDD, including immutable `InteractionContractRevision` semantics;
- `../../requirements/application-catalogue-domain-target.md` — accepted behavior and ACC/AD/RC split;
- `../application-deployment/boundary.md` + `../application-deployment/tactical-model.md` — deployment/placement owner;
- `../resource-catalogue/target-realization-model.md` — Resource AddressSpace owner;
- `../context-map.md` — cross-context contracts.

The superseded ACC-owned `ComponentDeployment` target explored in an earlier decision is not working-tree authority. Its still-valid consequences are represented in the current target documents above; the replaced decision itself remains available in Git history.

## Current implemented runtime

`tactical-model.md` describes the implemented I31/as-built model. Its ACC-owned `ApplicationDeployment`, `DeploymentInteraction`, Resource bindings, compatibility ComponentDeployment identities and `DirectedInteractionIdentity` are current runtime/compatibility facts, not target semantic ownership.

ADR-012 and ADR-013 are current as-built design decisions for that implementation. Existing UI/architecture/API contracts that describe I31 are likewise reconstruction authority for the as-built system while target ownership remains defined separately.

## Target boundary

```text
ACC: Application / Component / Interaction / InteractionContractRevision
AD:  ApplicationDeployment / ComponentPlacement -> ResourceRef
RC:  Resource -> effective HostAddress | Prefix
```

`Interaction` is the stable directed component-pair template. `InteractionContractRevision` is the immutable decision-relevant traffic snapshot. A material traffic change creates a new revision reference while preserving Interaction identity.

Migration must preserve referenced historical truth without promoting compatibility deployment identities back into ACC target ownership.
