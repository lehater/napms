# Scoped Connectivity Inventory acceptance examples

Status: `G1 examples aligned to concrete ComponentDeployment and formal RuleChange decisions 2026-09-16`.

Canonical requirements:
- `docs/requirements/scoped-connectivity-inventory.md`.

## SCI-EX-01 — admitted responsibility scope yields local Resources

Given Actor A has effective `ReadScopedConnectivity` authority for scope `payments-prod`, R1 is affiliated with that scope and R2 is not, then R1 is local and R2 is not. Resource identity is not derived from authority assignment.

## SCI-EX-02 — authority does not manufacture Resource membership

Given Actor A may read `payments-prod` but no Resource is affiliated with it, the result is an authorized empty local inventory.

## SCI-EX-03 — Resource membership does not manufacture authority

Given R1 is affiliated with `payments-prod` but Actor A lacks `ReadScopedConnectivity`, A cannot read that scope inventory.

## SCI-EX-04 — ambiguous/unknown read authority fails closed

Given read authority cannot be established unambiguously, no local inventory data is returned and the authority problem is explicit.

## SCI-EX-05 — Resource with no current AddressSpace still appears

Given R1 is local but has no trustworthy current AddressSpace, R1 still appears and technical realization is unresolved.

## SCI-EX-06 — Resource with no ComponentDeployment still appears

Given R1 is local and no target ComponentDeployment references R1, R1 appears with an explicit empty deployment/connectivity child state.

## SCI-EX-07 — same Component on two Resources means two deployments

Given Component C1 is deployed on R1 as CD1 and on R2 as CD2, then CD1 and CD2 are distinct ComponentDeployments even though both reference C1.

Changing R1's AddressSpace does not change CD1 identity.

## SCI-EX-08 — redeployment creates another concrete endpoint

Given CD1 represents C1 on R1, when C1 is redeployed on R2, the target model creates another ComponentDeployment CD2 rather than mutating CD1's Resource or preserving a whole-Application deployment identity.

Policy for CD1 does not automatically authorize CD2.

## SCI-EX-09 — outgoing relationship relative to local side

Given local CD1 realizes Interaction source Component C1 and ACC defines C1 -> C2 with revision K1, the relationship is shown as outgoing relative to CD1.

## SCI-EX-10 — incoming relationship relative to local side

Given local CD2 realizes destination Component C2 of C1 -> C2 / K1, the relationship is shown as incoming while canonical direction remains C1 -> C2.

## SCI-EX-11 — replicas produce separate concrete policy subjects

Given CD-A1 and CD-A2 both realize source Component A on different Resources and CD-B1 realizes B, then `CD-A1 -> CD-B1` and `CD-A2 -> CD-B1` are separate concrete PolicyRule subjects.

## SCI-EX-12 — remote Resource known, current address unresolved

Given a concrete remote ComponentDeployment is known but its Resource has no current AddressSpace, the remote deployment/Resource context is shown and technical realization is explicitly unresolved.

## SCI-EX-13 — business Need is independent from current policy

Given a current Process-backed Connectivity Need exists but no effective PolicyRule exists, inventory may show `Need = Known` and `CurrentEffect = NotEffective`.

Need existence does not imply acceptance.

## SCI-EX-14 — effective policy may lack current business attribution

Given a PolicyRule is effective but current Need attribution is unavailable, inventory may show `Need = Unknown` and `CurrentEffect = Effective`; it must not fabricate a Need.

## SCI-EX-15 — Pending RuleChange is not current effect

Given Rule PR1 is effective with R1 and RuleChange RC2 proposes R2 in `Pending`, then inventory shows the Rule remains effective on R1 and `PendingChange = Yes`.

## SCI-EX-16 — Accepted initial change establishes current policy

Given PR1 has no effective revision and RC1 proposes R1 in `Pending`, when RC1 receives formal decision `Accepted`, PR1 becomes effective with R1.

No source/destination approval pair is required by baseline semantics.

## SCI-EX-17 — Rejected change creates no deny Rule

Given RC2 is Rejected, the previous effective revision remains unchanged and no semantic deny PolicyRule is created merely to represent rejection.

## SCI-EX-18 — external workflow may record final decision

Given a customer approval/ticket system completes its own procedure and an authorized integration records `Accepted` on Pending RC2, AP applies the same formal RuleChange transition without reproducing the external workflow stages.

## SCI-EX-19 — withdrawal clears effectiveness without rewriting history

Given PR1 is currently effective, when an admitted withdrawal action is recorded, `CurrentEffect = NotEffective`; the prior Accepted RuleChange remains historical truth rather than becoming Rejected.

## SCI-EX-20 — old acceptance cannot silently reactivate withdrawal

Given PR1 was withdrawn after RC1 had been Accepted, RC1 cannot silently restore current effect. A new RuleChange and explicit Accepted decision are required.

## SCI-EX-21 — one Rule may have several business justifications over time

Given several Connectivity Needs have historically justified changes for the same concrete directed pair, AP may retain one PolicyRule identity while preserving change/business provenance.

## SCI-EX-22 — request access reuses trusted semantic context

Given source CD-A1, destination CD-B1, exact revision K1 matching their Components, a valid Process-backed Connectivity Need and admitted proposal action, Request/Propose access creates or reuses the Rule for:

```text
CD-A1 + CD-B1
```

and creates:

```text
RuleChange(K1, Pending)
```

It does not make K1 effective until an explicit Accepted decision.

## SCI-EX-23 — deliberate submission requires business justification

Given deliberate proposal for an Interaction with no valid Process-backed Connectivity Need, the product does not fabricate a Need and does not submit the target RuleChange through the normal deliberate path.

## SCI-EX-24 — Resource owner metadata does not itself decide policy

Given a user is displayed as Resource owner/administrator, that metadata alone neither accepts nor rejects a RuleChange and does not establish action authority.

## SCI-EX-25 — Resource scope does not create approval sides

Given source and destination Resources have RC Scope Affiliations, those facts may be useful for inventory/authority/customer extensions but the baseline AP decision does not create one approval obligation per endpoint scope.

## SCI-EX-26 — effective but unresolved technical realization

Given a Rule is effective but either endpoint Resource lacks a usable AddressSpace or later target/policy-locator evidence is unresolved, `CurrentEffect = Effective` while realization is `Unresolved`.

## SCI-EX-27 — realization distinguishes missing and excess access

Given trustworthy comparable required and configured effective policy:
- required but absent technical access -> `MissingRequiredAccess`;
- technically present access with no current requirement -> `ExcessUnauthorizedAccess`;
- equivalent required/configured access -> `Satisfied`.

These are realization summaries, not RuleChange decision states.

## SCI-EX-28 — partial enrichment failure remains partial

Given local Resource/interaction rows are trustworthy but one Need, policy or realization enrichment is unavailable, the base row remains available and only the affected dimension is `Unknown`.

## SCI-EX-29 — top-level paging preserves Resource groups

Given more local Resources exist than one page, pagination is over the effective local Resource set. Resource groups are not split across top-level pages; bounded child collections expose explicit continuation/truncation.
