# Catalogue curation — functional requirements

Status: M7 PILOT CANDIDATE / non-canonical.

This artifact materializes the selected Resource Catalogue portion of catalogue curation. It does not replace canonical `docs/requirements/**` during the pilot and does not authorize product code changes.

## Resource identity and temporal facts

- `REQ-CAT-RC-001` — An admitted user can create/register an access-relevant Resource identity with required provenance and inspect its details.
- `REQ-CAT-RC-002` — An admitted user can add, end and replace time-qualified Resource endpoint/realization facts while historical facts remain distinguishable.
- `REQ-CAT-RC-003` — An admitted user can add, end and replace Resource Scope Affiliations without changing Resource identity.
- `REQ-CAT-RC-004` — An admitted user can maintain Resource Responsibility/contact assignments for supported references and roles.
- `REQ-CAT-RC-005` — The Resources workspace provides server-backed paging, supported search/filtering, scope-focused filtering, explicit missing-fact indication and navigation to admitted mutations.
- `REQ-CAT-RC-006` — Missing effective affiliation or realization does not hide or fabricate a Resource; missing relations are represented explicitly.

## Admission and trust boundary

- `REQ-CAT-AUTH-001` — Every catalogue mutation is admitted by Authority Management using authenticated actor identity and the owning use case's server-selected catalogue action/scope.
- `REQ-CAT-AUTH-002` — Client-supplied actor, catalogue authority scope or action time is not trusted for mutation authorization.
- `REQ-CAT-AUTH-003` — Resource affiliation, responsibility/contact role, catalogue/read visibility and unrelated policy actions do not by themselves grant catalogue curation authority.
- `REQ-CAT-AUTH-004` — Catalogue curation authority does not grant protected Connectivity/Checker/proposal/decision/Access Rule actions.
- `REQ-CAT-AUTH-005` — Direct HTTP mutation is rejected when authority is absent even if presentation state hides or disables the action.
- `REQ-CAT-AUTH-006` — Authorization denial is distinguishable from domain/structural validation, optimistic concurrency, idempotency and persistence/transport failures without leaking protected authority/provenance detail.

## Validation and authoring behavior

- `REQ-CAT-VAL-001` — Catalogue mutations reject invalid required references/provenance, invalid temporal intervals, prohibited overlaps, missing binding targets and invalid DCS semantics explicitly. For this RC pilot, only the RC-owned validation subset is materialized downstream.
- `REQ-CAT-UX-001` — Supported authoring uses backend discovery for cross-context references rather than requiring arbitrary internal stable-ID combinations.
- `REQ-CAT-UX-002` — Mutation workflows distinguish version/relation-ending operations from scalar edits, prevent accidental duplicate submission, surface relevant validation errors and distinguish authorization/domain/transport failures.

## Excluded neighboring requirements

Application hierarchy, Component Deployment binding and DCS authoring requirements remain S1 requirements in the source classification but are outside this bounded Resource Catalogue pilot. They are not silently transferred to Resource Catalogue ownership.

## Ownership boundary

These are observable product requirements. Resource Catalogue domain identities/invariants remain S2-owned; HTTP routes, DTOs and transaction mechanics remain S3-owned. Externally imposed/non-negotiable constraints, if later identified, remain S0-owned.