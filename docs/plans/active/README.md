# Active execution

Current: none.

The selected next implementation increment is the Required Access Matrix defined by `docs/requirements/first-mvp-required-access-matrix.md`.

Current accepted product slice:

```text
ACC InteractionContractRevision
        +
AD ApplicationDeployment + ComponentPlacement
        +
RC Resource + AddressSpace
        |
        v
Required Access Matrix
        |
        +--> table
        `--> vendor-neutral export
```

No S3 Architecture task is active yet. No implementation authorization exists.

## Next

Enter S3 Architecture only for this selected slice when explicitly requested. Production-code implementation remains forbidden until S4 reaches G4 for an explicit scope.
