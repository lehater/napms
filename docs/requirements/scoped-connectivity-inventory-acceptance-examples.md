# Scoped Connectivity Inventory acceptance examples

Status: `G1 revalidated specification-by-example; AD target semantics aligned 2026-09-15`.

Date: 2026-09-15.

Canonical requirements:
- `docs/requirements/scoped-connectivity-inventory.md`.

## SCI-EX-01 — admitted responsibility scope yields local Resources

Given:
- Actor A has effective `ReadScopedConnectivity` authority for scope `payments-prod` at T;
- Resource R1 is effectively affiliated with `payments-prod` at T;
- Resource R2 is not.

Then R1 is local, R2 is not, and Resource identity is not derived from the actor's authority assignment.

## SCI-EX-02 — authority does not manufacture Resource membership

Given Actor A may read `payments-prod` but no Resource is affiliated with that scope, the result is an authorized empty local inventory.

## SCI-EX-03 — Resource membership does not manufacture authority

Given R1 is affiliated with `payments-prod` but Actor A lacks `ReadScopedConnectivity`, A cannot read that scope as a local inventory.

Catalogue visibility of R1 may still exist independently under the global Resource visibility policy.

## SCI-EX-04 — ambiguous/unknown authority fails closed

Given `ReadScopedConnectivity` authority for the requested scope cannot be established unambiguously/trustworthily, no local inventory data is returned and the authority problem is explicit.

## SCI-EX-05 — Resource with no current AddressSpace still appears

Given R1 is local but has no trustworthy current RC AddressSpace realization, R1 still appears and technical realization is shown as unresolved.

## SCI-EX-06 — Resource with no Component placement still appears

Given R1 is local and AD has no current ComponentPlacement referencing R1, R1 appears with an explicit empty deployment/placement/connectivity child state.

## SCI-EX-07 — one Component may have several current placements

Given ApplicationDeployment D1 contains Component C1 placements on R1 and R2,

Then:
- the same logical D1/C1 may appear under both Resources;
- D1 identity is the same in both projections;
- the system does not invent two ComponentDeployment identities merely because there are two Resources;
- an exact duplicate `(C1, R1)` placement relation is not represented twice.

Changing R1's AddressSpace does not change D1 or the `(C1, R1)` placement meaning.

## SCI-EX-08 — placement migration preserves logical deployment identity

Given D1/C1 is currently placed on R1,

When current placement changes so C1 is placed on R2 instead (or temporarily on both during ordinary scaling/migration),

Then D1 remains the same ApplicationDeployment while its placement set changes.

The governed subject changes only if the logical ApplicationDeployment or InteractionContractRevision identity changes, not merely because Resource placement changes.

## SCI-EX-09 — outgoing relationship relative to local side

Given C1 of source ApplicationDeployment D1 is placed on local R1 and ACC defines Interaction C1 -> C2 with current contract revision K1,

Then the row under R1/D1/C1 is outgoing, while canonical source/destination remain C1/C2.

## SCI-EX-10 — incoming relationship relative to local side

Given C2 of destination ApplicationDeployment D2 is placed on local R2 and ACC defines C1 -> C2 / K1,

Then the row under R2/D2/C2 is incoming and canonical source/destination remain C1/C2.

## SCI-EX-11 — both participants/local placements do not duplicate domain identity

Given D1/C1 and D2/C2 have placements on Resources in the same selected scope, the same governed interaction may appear through several local Resource/placement paths without creating duplicate Interaction, Access Request or Policy Rule identity.

## SCI-EX-12 — remote Resource known, current address unresolved

Given C1 -> C2 / K1 is known and D2/C2 has an applicable placement on Resource R2 but R2 has no current AddressSpace,

Then the remote ApplicationDeployment/Component/Resource context is shown and address realization is explicitly unresolved. The semantic interaction is not described as absent.

## SCI-EX-13 — business Need is independent from authorization

Given a current Process-backed Connectivity Need exists for Interaction I but there is no current authorization,

Then the inventory may show:
- Need = Known;
- effectiveAuthorization = No.

It must not infer approval from the Need.

## SCI-EX-14 — authorized access may lack current business attribution

Given a current Policy Rule is effectively authorized but current Process/Need attribution is unavailable,

Then the inventory may show:
- Need = Unknown or None according to authoritative business truth;
- effectiveAuthorization = Yes.

It must not fabricate a Need from Rule existence.

## SCI-EX-15 — one side approved, one side pending

Given an Access Request exists for a governed subject, source-side approval is valid, and destination-side approval is pending,

Then governance summary = PendingApprovals and effectiveAuthorization != Yes.

## SCI-EX-16 — bilateral approval produces authorization

Given both required sides validly approve the same current Request subject,

Then governance summary may be Approved and the resulting Access Policy truth may show one authoritative effective Rule for that subject.

## SCI-EX-17 — rejection creates no deny Rule

Given either required side rejects a pending Access Request,

Then governance summary = Rejected and no deny Policy Rule is created merely to represent the rejection.

## SCI-EX-18 — unilateral withdrawal revokes current authorization

Given a subject was previously approved by both sides and one currently authorized side withdraws consent,

Then:
- governance summary = Revoked;
- effectiveAuthorization = No after withdrawal;
- the original approved Request/history remains historical truth and is not rewritten as Rejected.

## SCI-EX-19 — one Rule may have several business justifications

Given two current Connectivity Needs and two approved Requests justify the same exact governed subject,

Then Access Policy may expose one current authoritative Rule for that subject while preserving many-to-one provenance.

## SCI-EX-20 — request access reuses trusted semantic context

Given:
- source ApplicationDeployment D1 with source Component C1 placed on selected local Resource R1;
- destination ApplicationDeployment D2 whose destination Component C2 realizes the other Interaction endpoint;
- existing immutable ACC `InteractionContractRevisionRef` K1 for C1 -> C2;
- valid Process-backed Connectivity Need;
- actor admitted to initiate access for the source scope,

When the actor selects Request access,

Then the system submits an Access Request for:

```text
K1 + D1 + D2
```

The current Resource placements are used for applicability/obligation resolution but are not embedded into governed-subject identity. The flow does not materialize a Policy Rule directly.

## SCI-EX-21 — request requires business justification

Given the user attempts deliberate Request access for an Interaction with no valid Process-backed Connectivity Need,

Then the product does not fabricate a Need and does not bypass Business Connectivity. The missing justification is explicit and must be established through the owning capability.

## SCI-EX-22 — owner/admin metadata does not grant approval

Given a user is shown as Resource owner/administrator but lacks effective approval authority for the relevant scope/action,

Then the user cannot satisfy that side's approval obligation merely because of the owner/admin metadata.

## SCI-EX-23 — same actor may approve both sides only with both authorities

Given Actor A independently has valid source-side and destination-side approval authority,

Then A may satisfy both obligations. If A has only one side's authority, the other obligation remains unresolved.

## SCI-EX-24 — authorized but unresolved technical realization

Given a Rule is effectively authorized but an applicable placement Resource has no current usable AddressSpace, or target/policy-locator evidence is unresolved,

Then:
- effectiveAuthorization = Yes;
- realization = Unresolved;
- the Rule is not silently omitted from desired policy semantics.

## SCI-EX-25 — realization distinguishes missing and excess access

Given trustworthy comparable required and configured effective policy:
- required but absent technical access -> MissingRequiredAccess;
- technically present access with no current requirement -> ExcessUnauthorizedAccess;
- equivalent required/configured access -> Satisfied.

These are realization summaries, not approval states.

## SCI-EX-26 — partial enrichment failure remains partial

Given local Resource/interaction rows are trustworthy but one governance or realization enrichment is unavailable,

Then the base row remains available and only the affected dimension is Unknown. Unknown is never converted into false absence or denial.

## SCI-EX-27 — top-level paging preserves Resource groups

Given more local Resources exist than one page, pagination is over the effective local Resource set. Resource groups are not split across top-level pages; bounded child collections expose explicit continuation/truncation.
