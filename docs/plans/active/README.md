# Active execution

Current: `application-deployment-boundary.md`

Lifecycle stage: `S2 affected-edge convergence / audit`.

Implementation authorization: `none`.

## Current baseline

```text
ACC Application / Component / InteractionContractRevision
        |
        v
AD ApplicationDeployment / ComponentPlacement -> ResourceRef
        |
        v
RC Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
```

Canonical target authority:

- `docs/domain/strategic-model.md` — responsibilities/boundaries;
- `docs/domain/context-map.md` — relationships/contracts;
- `docs/domain/strategic-model.json` — machine-readable projection;
- `docs/plans/active/application-deployment-boundary.md` — current execution/audit plan.

## Current blockers

Access Governance has three S1 behavior questions: selectable ApplicationDeployment pairs, authorization behavior when placement/scope changes alter approval obligations, and obligations under overlapping Responsibility Scopes.

AG Tactical G2 is therefore not currently valid for the affected subject/obligation slice. Downstream APR work must not assume the old ComponentDeployment subject or ResourceEndpoint materialization.

## Next

Finish branch validation, then resume foundational Tactical work in dependency order `ACC + RC -> AD -> AM -> affected BC/AG/AP`, followed by downstream RPM/NEP/TAE/APR/NEO as contracts permit.
