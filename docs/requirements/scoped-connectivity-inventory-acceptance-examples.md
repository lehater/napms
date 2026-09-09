# Scoped Connectivity Inventory acceptance examples — I16A

Status: `accepted I16A WP-02 specification-by-example baseline`.

Date: 2026-09-09.

## Purpose

Make the Scoped Connectivity Inventory semantics executable without turning the composition into a new source of business truth.

Canonical requirements:
- `docs/requirements/scoped-connectivity-inventory.md`.

## SCI-EX-01 — admitted responsibility scope yields local Resources

Given:
- Actor A has exactly one effective `ReadScopedConnectivity` Responsibility Assignment for scope `payments-prod` at T;
- Resource R1 has an effective Resource Scope Affiliation to `payments-prod` at T;
- Resource R2 has no effective affiliation to that scope at T.

When A reads Scoped Connectivity Inventory for `payments-prod` at T,

Then:
- R1 is in the local Resource set;
- R2 is not local;
- no ownership field on R1 is required;
- Resource identity is unchanged by the affiliation.

## SCI-EX-02 — authority does not manufacture Resource membership

Given:
- Actor A has `ReadScopedConnectivity` for `payments-prod`;
- no Resource has an effective Resource Scope Affiliation to `payments-prod`.

Then the result is an authorized empty local inventory.

The system must not infer local Resources from the Actor's authority assignment alone.

## SCI-EX-03 — Resource membership does not manufacture authority

Given:
- R1 is effectively affiliated with `payments-prod`;
- Actor A has no effective `ReadScopedConnectivity` for `payments-prod`.

Then A cannot read the scope as a local Scoped Connectivity Inventory.

This does not make R1 invisible as foreign catalogue data under the current global catalogue-read baseline.

## SCI-EX-04 — ambiguous scope authority fails closed

Given two conflicting/effective `ReadScopedConnectivity` assignments make `payments-prod` ambiguous under current Authority Management semantics,

When A requests the inventory,

Then no local Resource rows are returned for that scope and the ambiguity is explicit.

## SCI-EX-05 — Resource with no realization still appears

Given:
- R1 is effectively affiliated with the selected scope at T;
- R1 has no trustworthy current Resource Endpoint realization at T.

Then R1 still appears in the local Resource set.

Its endpoint/realization is shown as unresolved/unknown rather than silently dropping R1.

## SCI-EX-06 — Resource with no Component Deployment still appears

Given:
- R1 is local at T;
- ACC has no effective DeploymentResourceBinding to R1 at T.

Then R1 appears with an explicit no-components/no-connectivity child state.

The empty child state is not a technical failure.

## SCI-EX-07 — Component with no interactions exposes Add Connectivity context

Given:
- Component Deployment C1 is effectively bound to local R1;
- ACC has no exact directed interaction involving C1.

Then:
- R1 -> C1 appears;
- the workspace may show `No connectivity declared`;
- `Add connectivity` may be shown only when its downstream actions are independently admitted.

## SCI-EX-08 — outgoing relationship relative to local side

Given:
- C1 is bound to local R1;
- ACC defines exact interaction C1 -> C2 / DCS-Https;
- C2 is bound to foreign R2.

Then the row under R1/C1 is:
- direction = outgoing;
- remote Component = C2;
- remote Resource = R2;
- canonical source/destination remain C1/C2.

## SCI-EX-09 — incoming relationship relative to local side

Given:
- C2 is bound to local R2;
- ACC defines exact interaction C1 -> C2 / DCS-Https.

Then the row under R2/C2 is:
- direction = incoming;
- remote Component = C1;
- canonical source/destination remain C1/C2.

## SCI-EX-10 — both participants local

Given C1 and C2 are bound to Resources effectively affiliated with the same selected scope,

Then the same exact interaction may appear:
- under C1 as outgoing;
- under C2 as incoming.

The two tree paths do not create two Domain Interactions or two Access Rule identities.

## SCI-EX-11 — Component Deployment bound to multiple Resources

Given C1 has effective bindings to local R1 and local R2 at T,

Then C1 may appear under both Resource group rows.

Its stable Component Deployment identity remains one identity.

No one-to-one Resource/Component assumption is allowed.

## SCI-EX-12 — remote Component known, remote Resource unresolved

Given:
- exact interaction C1 -> C2 is known;
- C1 is local;
- C2 has no effective Resource binding/realization at T.

Then:
- remote Component C2 is shown;
- remote Resource is explicitly unresolved;
- the row is not described as missing connectivity;
- Add Connectivity is not offered merely because technical realization is unresolved.

## SCI-EX-13 — selected-scope Requirement summary

Given:
- exact interaction I;
- one Active/applicable Connectivity Requirement for I stored under selected scope S at T;
- Actor has `ReadScopedConnectivity` for S but not `ReadConnectivityRequirement`.

Then the coarse inventory may show:
- Need = Required;
- applicable coverage result.

It must not expose:
- Requirement ID;
- justification;
- audit/provenance;
- protected detail fields.

## SCI-EX-14 — Requirement in another scope is not selected-scope Need

Given:
- selected responsibility scope is S1;
- exact interaction I has no Requirement stored under S1;
- a matching Requirement exists under S2.

Then the selected-scope Need summary for S1 is not changed to Required merely because S2 contains a Requirement.

The foreign Requirement may still affect other independently accepted product views; its protected details are not leaked by this inventory.

## SCI-EX-15 — Decision summary is selected-scope specific

Given:
- selected scope S1;
- exact subject I;
- effective Allowed Decision exists for I/S1 at T.

Then Decision summary = Allowed.

If only a Decision for I/S2 exists, the S1 Decision summary is `NoFinalDecision`, not Allowed/NotAllowed inferred from S2.

## SCI-EX-16 — no final Decision is not a Decision outcome

Given the authoritative Decision query for I/S at T establishes no effective Decision,

Then the inventory may show `No final decision`.

This is an application/read absence result and must not be persisted as a third Connectivity Decision outcome.

## SCI-EX-17 — Decision uncertainty is Unknown

Given Decision persistence/selection is unavailable or ambiguous for I/S/T,

Then Decision summary = Unknown.

It must not be converted to `No final decision` or NotAllowed.

## SCI-EX-18 — coarse Policy summary without Rule detail authority

Given:
- exact matching Access Rule exists and is Active/effective at T;
- Actor has `ReadScopedConnectivity` but not `ReadAccessRule`.

Then the inventory may return:
- ruleExists = Yes;
- operationalState = Active;
- effectiveAtAsOf = Yes.

It must not expose:
- Rule ID;
- Rule Governance Scope;
- EffectiveWindow value;
- Decision/proposal provenance;
- Rule audit.

## SCI-EX-19 — policy can exist without selected-scope Need

Given:
- selected-scope Need current=None;
- exact matching Rule exists and is effective.

Then the row may show no current selected-scope Need and an effective Policy.

The composition must not manufacture a Requirement from Rule existence.

## SCI-EX-20 — covered/uncovered follows I14 semantics

Given a current selected-scope Requirement for exact interaction I at T:
- if an exact matching Rule contributes effective desired policy at T, coverage = Covered;
- if trustworthy Access Policy truth establishes no effective matching Rule, coverage = Uncovered;
- if policy truth is unavailable/ambiguous, coverage = Unknown.

Uncovered never means NotAllowed.

## SCI-EX-21 — Resource changes responsibility scope

Given:
- R1 was affiliated with S1 before T2;
- R1 is affiliated with S2 after T2;
- an existing Requirement/Decision/Rule stores governance scope S1.

Then after T2:
- R1 may appear local under S2;
- the existing Requirement/Decision/Rule governance scope remains S1;
- no identity or stored governance scope is silently rewritten.

## SCI-EX-22 — foreign remote catalogue data remains visible

Given:
- local R1/C1 communicates with foreign R2/C2;
- R2 belongs to another responsibility scope.

Then R2/C2 and their allowed catalogue presentation/endpoint data are readable in the current baseline.

This visibility grants no mutation authority and no protected Requirement/Decision/Rule detail access.

## SCI-EX-23 — one logical asOf

Given T is the requested logical time,

Then the same T is used for:
- ReadScopedConnectivity authority;
- Resource Scope Affiliation;
- Resource realization;
- DeploymentResourceBinding;
- Requirement currentness/alignment;
- Decision effectiveness;
- Rule effective-state evaluation.

The composition must not mix hidden wall-clock time into those facts.

## SCI-EX-24 — partial enrichment failure

Given:
- scope admission and local Resource/ACC relationship rows are trustworthy;
- Decision summary lookup fails;
- Need and Policy summary lookups succeed.

Then:
- the base relationship row remains available;
- Decision dimension is Unknown;
- trustworthy Need/Policy dimensions remain visible.

A later enrichment failure must not erase trustworthy catalogue topology or turn Unknown into false absence.

## SCI-EX-25 — top-level paging preserves Resource groups

Given more local Resources exist than one page,

Then pagination is over the effective local Resource set.

A Resource group is not split across top-level pages. If a child collection is separately bounded, truncation/continuation is explicit.
