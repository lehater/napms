# Application Communication Catalogue domain

## Current target

Current ACC target authority:

- `target-model.md` — strategic target shape for Application / Component / Interaction / immutable traffic contracts;
- `target-tactical-model.md` — current MVP Tactical DDD, including immutable `InteractionContractRevision` semantics;
- `../../requirements/application-catalogue-domain-target.md` — accepted behavior for ACC communication meaning, concrete Component deployment and RC realization;
- `../application-deployment/boundary.md` + `../application-deployment/tactical-model.md` — target concrete ComponentDeployment owner;
- `../resource-catalogue/target-realization-model.md` — Resource AddressSpace owner;
- `../context-map.md` — cross-context contracts.

## Current implemented runtime

`tactical-model.md` describes the implemented I31/as-built model. Its ACC-owned `ApplicationDeployment`, `DeploymentInteraction`, Resource bindings, compatibility ComponentDeployment identities and `DirectedInteractionIdentity` are current runtime/compatibility facts, not target semantic ownership.

ADR-012 and ADR-013 remain current as-built design decisions for that implementation. Existing UI/architecture/API contracts that describe I31 are likewise reconstruction authority while target ownership is defined separately.

The target now also uses the term `ComponentDeployment`, but with different semantics and ownership: target Application Deployment owns one concrete Component instance on one Resource. This must not be confused with the ACC-owned compatibility ComponentDeployment identities retained by the implemented runtime.

## Target boundary

```text
ACC: Application / Component / Interaction / InteractionContractRevision
AD:  ComponentDeployment(ComponentRef, ResourceRef)
RC:  Resource -> effective HostAddress | Prefix
```

`Interaction` is the stable directed component-pair template inside one Application. `InteractionContractRevision` is the immutable decision-relevant traffic snapshot. A material traffic change creates a new revision reference while preserving Interaction identity.

An exact revision reference resolves its owning Interaction/endpoints. Changing ACC-current revision never silently changes an existing Policy Rule; Policy Rule revision changes follow the Access Policy lifecycle.

Migration must preserve referenced historical as-built truth without promoting compatibility ACC deployment identities into target ownership.
