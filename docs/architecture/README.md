# Architecture map

This directory contains the architecture required to reconstruct and evolve NAPMS. Both **as-built** and **target** architecture are current project truth when the implemented system intentionally differs from the accepted target.

## Current as-built architecture

- `current-architecture.md` — integrated as-built application/runtime architecture and compatibility boundaries for the implemented product. Where it describes an older semantic model, it is implementation reconstruction truth, not target-domain authority.
- `application-catalogue-target-boundary.md` — implemented Application Catalogue boundary and its target-facing ownership constraints.
- `catalogue-curation-boundary.md` — catalogue composition, authority and persistence boundary used by the implemented curation product.
- `scoped-connectivity-inventory.md` — implemented owner-preserving connectivity read composition.
- `network-context-candidate-boundary.md` — implemented Checker/network-context composition boundary.
- `network-enforcement-placement-boundary.md` — implemented/compatibility NEP architecture needed by existing product paths.

## Current target / cross-cutting architecture

- `code-structure.md` — module/dependency taxonomy and structural guardrails.
- `technical-access-evidence-boundary.md` — current TAE structural boundary.
- `network-environment-operations-boundary.md` — current NEO structural boundary.
- `enterprise-identity-authoritative-sources-boundary.md` — authoritative-source extension seams.

Target semantic authority remains with current `docs/domain/` and `docs/requirements/` owners. As-built architecture must not silently redefine those target semantics.

There is not yet an accepted S3 architecture contract for the selected Full Vendor-Neutral Policy Export MVP. The selected target slice starts from current effective AP Policy Rules and composes AP + ACC + AD + RC into one complete table/CSV result containing source/destination AddressSpace, protocol and port/range semantics without firewall/device/provider context.

Before S3, the changed selection requires a narrow S2 revalidation of the AP -> export composition and policy-creation handoff. Architecture must then remain scoped to owner-preserving policy materialization, coherent reads, table/export delivery and compatibility with the existing as-built normalized policy export.

Do not remove an as-built architecture contract merely because its capability has been implemented: it remains project documentation while it is needed to reconstruct the current system. Remove only architecture that no longer describes either current as-built or current target design.
