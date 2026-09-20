# Sanitized initial Wave-1 product input

Source class: SOURCE_INPUT / initial accepted product requirements.  
Provenance: NAPMS bootstrap commit `c403ceeda2837d8956e3d093fef95c1bd69d0c6f`, 2026-09-08.  
Provenance artifact states that NAPMS was a curated greenfield extraction from an accepted pre-implementation baseline and explicitly copied accepted current product requirements and acceptance examples.

Only observable product behavior/scope is retained here. Exact domain identity tuples, named domain owners, aggregate boundaries, persistence, APIs and technical realization from the historical documents remain excluded.

## Accepted outcome/scope

- The first product slice covers an end-to-end path from application-backed connectivity intent/request through a permission decision and current desired-access state to a complete, explainable, vendor-neutral normalized policy export.
- Provider/device-specific rendering, direct firewall/provider execution and configured-state reconciliation are outside that first slice.
- Users operate on trusted semantic catalogue/domain references rather than raw firewall/vendor syntax when enough semantic information exists.
- Permission to submit/request connectivity is distinct from the decision whether connectivity is allowed.
- A denied connectivity decision must not create effective desired access.
- The permission decision remains correlated to the exact submitted access meaning; later identity-defining semantic change must not silently inherit/rewrite the historical decision.
- Reprocessing the same already-allowed semantic access must not create duplicate authoritative current access solely because it was processed again.
- On first successful allowed materialization, the resulting current desired access is operationally active.
- An authorized actor can switch allowed current desired access Active <-> Inactive without requiring a new permission decision; identity/history and prior decision provenance are preserved and the transition is auditable.
- An allowed access may carry supported declarative effective conditions. These conditions determine whether it contributes desired effect at evaluation time without changing its permission identity or periodically rewriting stored Active/Inactive state.
- Current effective desired access can be selected as a domain-policy subset for export; selection must not depend on vendor/device syntax.
- Effective contribution at the export evaluation time requires: allowed authoritative access + Active operational state + declarative effective conditions satisfied.
- The export is evaluated for one logical evaluation time.
- Inactive or conditionally non-effective selected access contributes no rows and missing realization for it does not make export incomplete.
- The exported result must be vendor-neutral and sufficiently explainable for downstream human use or later provider-specific realization.
- If required information for any included effective access cannot be truthfully resolved, the product must not present the result as a complete successful export.
- Diagnostic partial information may be returned only as an explicitly non-success/degraded result.
- Normalization may expand one semantic access requirement into multiple technical rows when necessary, but must not broaden/narrow its meaning or erase independent business provenance.
- The product must preserve enough end-to-end provenance to explain how business/request intent, permission decision, current operational state/effective condition and source facts contributed to exported policy.

## Accepted acceptance semantics retained from the pre-implementation baseline

- Authority to request/propose connectivity does not by itself mean the connectivity is allowed.
- A denied decision produces no effective desired access.
- First allowed materialization yields one stable authoritative current-access identity and Active operational state.
- Repeated processing of the same allowed semantic access resolves the same authoritative current access rather than duplicating it.
- Active -> Inactive removes desired effect while preserving identity/history/permission provenance.
- Inactive -> Active restores possible desired effect without a new permission decision, subject to current declarative conditions.
- A supported time/effective condition can make an Active access non-effective at one evaluation time and effective at another without changing stored Active/Inactive state.
- Technical realization changes alone do not silently rewrite the business permission/intention they realize.
- Missing or stale required realization information blocks a successful complete policy export only for selected access that is effective at evaluation time.
- Equivalent technical effects originating from independently meaningful access intent remain independently explainable when merging would lose provenance.

## Deliberately not imported from the historical product files

- the exact tuple/fields that define semantic Access Rule identity;
- exact tactical entity/aggregate/value-object/state-machine representation beyond observable Active/Inactive behavior;
- named Bounded Context/domain owner assignments;
- API/DTO/transport shape;
- persistence/storage/event-log mechanisms;
- implementation-specific idempotency mechanism;
- provider-specific realization.

Those remain blind downstream design decisions.
