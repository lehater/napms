# Active execution

Current: none.

The selected next implementation increment is the Full Vendor-Neutral Policy Export defined by `docs/requirements/first-mvp-vendor-neutral-policy-export.md`.

Current accepted product slice:

```text
AP current effective Policy Rules
        +
ACC InteractionContractRevision
        +
AD ApplicationDeployment + ComponentPlacement
        +
RC Resource + AddressSpace
        |
        v
Full Vendor-Neutral Policy Export
        |
        +--> table
        `--> CSV/vendor-neutral data
```

The exported policy must carry access-list-oriented source/destination address, protocol and port/range semantics while remaining independent of firewall, device, ACL and provider context.

The previous AP-free Required Access Matrix selection is superseded.

No product workstream is active yet. Because the selected slice now starts from authoritative Access Policy truth, the next lifecycle step is a narrow S2 revalidation of the AP -> export composition and policy-creation handoff before S3 Architecture starts. No implementation authorization exists.

## Next

Enter S2 only for the selected AP + ACC + AD + RC export slice when explicitly started. Confirm that the export consumes public owner contracts, owns no independent policy truth and does not require NEP/device semantics. Then proceed through S3/S4. Production-code implementation remains forbidden until S4 reaches G4 for an explicit scope.
