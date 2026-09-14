# Scoped Connectivity Inventory acceptance examples

Status: `G1 revalidated specification-by-example`.

Date: 2026-09-14.

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

## SCI-EX-04 — ambiguous scope authority fails closed

Given authority for `ReadScopedConnectivity` is ambiguous, no local inventory data is returned for that scope and the ambiguity is explicit.

## SCI-EX-05 — Resource with no current address still appears

Given R1 is local but has no trustworthy current Endpoint/address realization, R1 still appears and technical realization is shown as unresolved.

## SCI-EX-06 — Resource with no ComponentDeployment still appears

Given R1 is local and ACC has no ComponentDeployment on R1, R1 appears with an explicit empty deployment/connectivity child state.

## SCI-EX-07 — exactly one Resource per ComponentDeployment

Given ComponentDeployment C1 exists on Resource R1,

Then:
- C1 appears under R1;
- C1 does not simultaneously belong to R2;
- moving the Component to R2 creates a different ComponentDeployment reference rather than rebinding C1.

Endpoint/address changes on R1 do not create a new ComponentDeployment.

## SCI-EX-08 — outgoing relationship relative to local side

Given C1 is deployed on local R1 and ACC defines C1 -> C2 / Contract-Https,

Then the row under R1/C1 is outgoing, remote participant is C2, and canonical source/destination remain C1/C2.

## SCI-EX-09 — incoming relationship relative to local side

Given C2 is deployed on local R2 and ACC defines C1 -> C2 / Contract-Https,

Then the row under R2/C2 is incoming and canonical source/destination remain C1/C2.

## SCI-EX-10 — both participants local

Given C1 and C2 are deployed on Resources in the same selected scope, the same exact interaction may appear under C1 as outgoing and C2 as incoming without creating duplicate interaction or Policy Rule identity.

## SCI-EX-11 — remote Resource known, current address unresolved

Given C1 -> C2 is known and C2's Resource is known but has no current address,

Then the remote ComponentDeployment/Resource are shown and address realization is explicitly unresolved. The interaction is not described as absent.

## SCI-EX-12 — business Need is independent from authorization

Given a current Process-backed Connectivity Need exists for interaction I but there is no current authorization,

Then the inventory may show:
- Need = Known;
- effectiveAuthorization = No.

It must not infer approval from the Need.

## SCI-EX-13 — authorized access may lack current business attribution

Given a current Policy Rule is effectively authorized for subject I but current Process/Need attribution is unavailable,

Then the inventory may show:
- Need = Unknown or None according to authoritative business truth;
- effectiveAuthorization = Yes.

It must not fabricate a Need from Rule existence.

## SCI-EX-14 — one side approved, one side pending

Given an Access Request exists for I, source-side approval is valid, and destination-side approval is pending,

Then governance summary = PendingApprovals and effectiveAuthorization != Yes.

## SCI-EX-15 — bilateral approval produces authorization

Given both required sides validly approve the same current Request subject,

Then governance summary may be Approved and the resulting Access Policy truth may show one authoritative effective Rule for that subject.

## SCI-EX-16 — rejection creates no deny Rule

Given either required side rejects a pending Access Request,

Then governance summary = Rejected and no deny Policy Rule is created merely to represent the rejection.

## SCI-EX-17 — unilateral withdrawal revokes current authorization

Given a subject was previously approved by both sides and one currently authorized side withdraws consent,

Then:
- governance summary = Revoked;
- effectiveAuthorization = No after the withdrawal takes effect;
- the original approved Request/history remains historical truth and is not rewritten as Rejected.

## SCI-EX-18 — one Rule may have several business justifications

Given two current Connectivity Needs and two approved Requests justify the same exact authorization subject,

Then Access Policy may expose one current authoritative Rule for that subject while preserving many-to-one provenance.

## SCI-EX-19 — request access reuses trusted semantic context

Given:
- local source ComponentDeployment C1;
- destination ComponentDeployment C2;
- existing ACC interaction contract C1 -> C2;
- valid Process-backed Connectivity Need;
- actor admitted to initiate access for the source scope,

When the actor selects Request access,

Then the system reuses the trusted source/destination/interaction subject and submits an Access Request into bilateral governance. It does not materialize a Policy Rule directly.

## SCI-EX-20 — request requires business justification

Given the user attempts deliberate Request access for an interaction with no valid Process-backed Connectivity Need,

Then the product does not fabricate a Need and does not bypass Business Connectivity. The missing justification is explicit and must be established through the owning capability.

## SCI-EX-21 — owner/admin metadata does not grant approval

Given a user is shown as Resource owner/administrator but lacks effective approval authority for the relevant scope/action,

Then the user cannot satisfy that side's approval obligation merely because of the owner/admin metadata.

## SCI-EX-22 — same actor may approve both sides only with both authorities

Given Actor A independently has valid source-side and destination-side approval authority,

Then A may satisfy both obligations. If A has only one side's authority, the other obligation remains unresolved.

## SCI-EX-23 — authorized but unresolved technical realization

Given a Rule is effectively authorized but the Resource has no current usable address or placement/policy-locator evidence,

Then:
- effectiveAuthorization = Yes;
- realization = Unresolved;
- the Rule is not silently omitted from desired policy semantics.

## SCI-EX-24 — realization distinguishes missing and excess access

Given trustworthy comparable required and observed policy:
- required but absent technical access -> MissingRequiredAccess;
- technically present access with no current authorization requirement -> ExcessUnauthorizedAccess;
- equivalent required/observed access -> Satisfied.

These are realization summaries, not approval states.

## SCI-EX-25 — partial enrichment failure remains partial

Given local Resource/interaction rows are trustworthy but one governance or realization enrichment is unavailable,

Then the base row remains available and only the affected dimension is Unknown. Unknown is never converted into false absence or denial.

## SCI-EX-26 — top-level paging preserves Resource groups

Given more local Resources exist than one page, pagination is over the effective local Resource set. Resource groups are not split across top-level pages; bounded child collections expose explicit continuation/truncation.
