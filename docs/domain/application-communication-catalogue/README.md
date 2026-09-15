# Application Communication Catalogue domain

Current ACC authority:

- `target-model.md` — Application / Component / Interaction / immutable traffic-contract shape;
- `target-tactical-model.md` — Tactical DDD for immutable `InteractionContractRevision` semantics;
- `../../requirements/application-catalogue-domain-target.md` — accepted ACC/AD/RC behavior;
- `../application-deployment/` — deployment and placement owner;
- `../resource-catalogue/` — Resource and AddressSpace owner;
- `../context-map.md` — cross-context contracts.

```text
ACC: Application / Component / Interaction / InteractionContractRevision
AD:  ApplicationDeployment / ComponentPlacement -> ResourceRef
RC:  Resource -> AddressSpace = HostAddress | Prefix
```

`Interaction` is the stable directed Component-pair template. `InteractionContractRevision` is the immutable traffic snapshot used by consumers. A material traffic change creates a new revision while preserving Interaction identity.
