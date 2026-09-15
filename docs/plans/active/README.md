# Active execution

Current: first implementation MVP — Required Access Matrix.

Lifecycle stage: `S2`
Stage state: `ACCEPTED`
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Selected slice

```text
ACC
  InteractionContractRevision
        +
AD
  ApplicationDeployment
  Component -> Resource placements
        +
RC
  Resource -> AddressSpace
        |
        v
Required Access Matrix materialization
        |
        +--> table
        `--> vendor-neutral export
```

Canonical product contract: `docs/requirements/first-mvp-required-access-matrix.md`.

The materialization input is an explicit set of:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

A successful result expands every applicable source placement × destination placement × traffic alternative. Missing required owner truth produces explicit `Unresolved`; incomplete output is never presented as a complete policy.

The first implementation does not require governance, authorization, firewall/ACL placement, configured-state comparison, provider rendering or device execution.

## Next

Enter S3 Architecture only for this selected slice. S3 must define composition boundaries, dependency direction, consistency/read semantics, output contract, UI/export seam and executable architecture checks without widening the product scope.

Production-code implementation remains forbidden until S4 reaches G4 for an explicit scope.
