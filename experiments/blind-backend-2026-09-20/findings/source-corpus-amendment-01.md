# Source Corpus amendment 01

Priority: P1  
Status: CLOSED BY RECLASSIFICATION / downstream reevaluation required

## Failure

The initial blind Source Corpus correctly admitted the 2026-09-08 pre-implementation Wave-1 Product Requirements baseline, but its sanitization excluded several **observable product behaviors** together with tactical lifecycle design.

The omitted source-level behaviors were:

- first allowed materialization creates/resolves one authoritative current access and starts it Active;
- the same already-allowed semantic access must not duplicate authoritative current access on repeated materialization;
- an authorized actor can change Active <-> Inactive without a new permission decision while preserving identity/history;
- declarative effective conditions affect contribution at evaluation time without toggling stored Active/Inactive state;
- a domain-policy subset may be selected for export;
- only allowed + Active + condition-effective access contributes desired effect;
- selected but inactive/non-effective access contributes no export rows and missing realization for it is not an export-completeness failure.

## Evidence

Bootstrap provenance at commit `c403ceeda2837d8956e3d093fef95c1bd69d0c6f` explicitly says the greenfield repository copied accepted current product requirements and acceptance examples from the accepted pre-implementation baseline.

The omitted statements appear in those Product Requirements / acceptance examples as externally observable behavior and deliberately avoid prescribing API, persistence or deployment topology.

## Classification

This is **not INPUT_CONTAMINATION**:
- the source class was already admitted and provenance-backed;
- no existing NAPMS domain/architecture/API artifact was used to repair the blind design;
- only observable behavior from the allowed pre-implementation product source was restored.

It is a Source Corpus under-classification defect.

## Consequence

All downstream knowledge that relied on current-access identity/effectiveness is invalidated for semantic acceptance until reevaluated:

- Product Requirements;
- Access Policy tactical design;
- Application Design;
- Interface/API Design;
- Persistence Design;
- Component Design;
- Security/authorization where operations change;
- Verification/Test Design;
- Implementation Design/completion criteria.

The prior Harness `IMPLEMENTATION COMPLETE` result remains valid only as proof that the declared providers structurally close the graph. It is not semantic implementation readiness.

## Prevention rule

When sanitizing an admitted Product Requirements source, classify statements individually:
- observable outcome/lifecycle/acceptance semantics -> SOURCE_INPUT;
- exact entity identity/owner/aggregate/API/storage/technical mechanism -> downstream design unless independently product-owned.

Do not use the word “lifecycle” alone as evidence that a statement is tactical design.
