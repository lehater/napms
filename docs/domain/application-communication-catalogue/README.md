# Application Communication Catalogue domain

## Current target

Current ACC target authority:

- `target-model.md` — strategic target shape for Application / Component / Interaction / immutable traffic contracts;
- `target-tactical-model.md` — current MVP Tactical DDD, including immutable `InteractionContractRevision` semantics;
- `../../requirements/application-catalogue-domain-target.md` — accepted behavior and ACC/AD/RC split;
- `../application-deployment/boundary.md` + `../application-deployment/tactical-model.md` — deployment/placement owner;
- `../resource-catalogue/target-realization-model.md` — Resource AddressSpace owner;
- `../context-map.md` — cross-context contracts.

ADR-015 is retained as superseded rationale/history. It is no longer target authority for ACC-owned `ComponentDeployment` or `DirectedInteractionIdentity`.

## Current implemented runtime

`tactical-model.md` describes the implemented I31/current-state model. Its ACC-owned `ApplicationDeployment`, `DeploymentInteraction`, Resource bindings, compatibility ComponentDeployment identities and `DirectedInteractionIdentity` are runtime/migration facts, not target semantic ownership.

Historical ADR-012/013 and existing UI/architecture contracts may still describe that implementation and must be read as current-state/migration evidence.

## Target boundary

```text
ACC: Application / Component / Interaction / InteractionContractRevision
AD:  ApplicationDeployment / ComponentPlacement -> ResourceRef
RC:  Resource -> effective HostAddress | Prefix
```

`Interaction` is the stable directed component-pair template. `InteractionContractRevision` is the immutable decision-relevant traffic snapshot. A material traffic change creates a new revision reference while preserving Interaction identity.

Migration must preserve referenced historical truth without promoting legacy deployment identities back into ACC target ownership.
