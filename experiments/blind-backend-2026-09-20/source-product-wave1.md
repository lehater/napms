# Sanitized initial Wave-1 product input

Source class: SOURCE_INPUT / initial accepted product requirements.  
Provenance: NAPMS bootstrap commit `c403ceeda2837d8956e3d093fef95c1bd69d0c6f`, 2026-09-08.  
Provenance artifact states that NAPMS was a curated greenfield extraction from an accepted pre-implementation baseline and explicitly copied accepted current product requirements and acceptance examples.

Only observable product behavior/scope is retained here. Domain identities, ownership, lifecycle structures and technical solution choices embedded in the historical requirement documents are excluded.

## Accepted outcome/scope

- The first product slice covers an end-to-end path from application-backed connectivity intent/request through a permission decision and current desired-access state to a complete, explainable, vendor-neutral normalized policy export.
- Provider/device-specific rendering, direct firewall/provider execution and configured-state reconciliation are outside that first slice.
- Users operate on trusted semantic catalogue/domain references rather than raw firewall/vendor syntax when enough semantic information exists.
- Permission to submit/request connectivity is distinct from the decision whether connectivity is allowed.
- A denied connectivity decision must not create effective desired access.
- Current effective desired access can be selected for export at one logical evaluation time.
- The exported result must be vendor-neutral and sufficiently explainable for downstream human use or later provider-specific realization.
- If required information for any included effective access cannot be truthfully resolved, the product must not present the result as a complete successful export.
- Diagnostic partial information may be returned only as an explicitly non-success/degraded result.
- Normalization may expand one semantic access requirement into multiple technical rows when necessary, but must not broaden/narrow its meaning or erase independent business provenance.
- The product must preserve enough end-to-end provenance to explain how business/request intent, decision, current desired access and source facts contributed to exported policy.

## Accepted acceptance semantics retained from the pre-implementation baseline

- Authority to request/propose connectivity does not by itself mean the connectivity is allowed.
- A denied decision produces no effective desired access.
- Technical realization changes alone do not silently rewrite the business permission/intention they realize.
- Missing or stale required realization information blocks a successful complete policy export for affected effective access.
- Access that is not currently effective contributes no export output and does not create an export-completeness failure solely because its realization is absent.
- Equivalent technical effects originating from independently meaningful access intent remain independently explainable when merging would lose provenance.

## Explicit exclusions from this sanitized source

The historical requirement files also contain exact semantic identities, named domain owners, lifecycle/state choices, idempotency models, tactical concepts and cross-context contracts. Those are not admitted as source input for this blind reconstruction.
