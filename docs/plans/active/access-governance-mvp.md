# Access Governance MVP behavior convergence

Status: `active S1 MVP behavior resolution`.

Date: 2026-09-15.

## Goal

Resolve only the Access Governance product behavior required to continue the first end-to-end happy path from accepted ACC/RC/AD semantics into bilateral authorization and Access Policy handoff.

Preserve the accepted bilateral model; do not design richer workflow, generalized scope algebra or implementation machinery unless the happy path requires it.

## Inputs

Accepted behavior already retained in `docs/requirements/access-governance-g1.md`:

- an Access Request applies a Process-backed Connectivity Need to a concrete source/destination ApplicationDeployment pair;
- a deployment pair is selectable for a declared Interaction when each deployment can realize the corresponding endpoint Component and the current placements needed to determine approval obligations are resolvable;
- source and destination approval obligations are independent;
- grant requires both required sides;
- either required side may reject a pending request;
- either authorized side may later withdraw its consent;
- Authority Management determines actor/action/scope authority;
- Resource Responsibility metadata is not approval authority;
- Access Policy consumes AuthorizationGranted / AuthorizationWithdrawn.

Upstream foundation now available:

```text
ACC Interaction / Component semantics
+ AD ApplicationDeployment / ComponentPlacement -> ResourceRef
+ RC Resource / ResourceScopeAffiliation / CurrentResourceRealization
```

## S1 decisions

### Q1 — selectable ApplicationDeployment pair — ACCEPTED

A pair is selectable when each ApplicationDeployment can realize the corresponding Interaction endpoint Component and the current placements needed to determine approval obligations are resolvable.

For MVP this does not add cross-application compatibility rules, planned/future deployment semantics or fallback inference.

### Q2 — obligation change after placement/scope change — CURRENT

Product decision still required. Minimal candidate for owner decision:

```text
If a placement or Resource Scope Affiliation change does not change the effective
approval obligations for the governed subject, current authorization remains valid.

If the effective approval obligations materially change, the current authorization
ceases to be effective and AG emits AuthorizationWithdrawn with provenance identifying
the obligation-change cause. The subject may become authorized again only after the
currently required obligations are approved.
```

For MVP, do not add a separate `Suspended` state. Do not treat an address or placement change alone as a withdrawal; the trigger is a material change of approval obligations.

Prior approval history remains historical evidence and must not silently satisfy a changed obligation set. Whether an unchanged individual obligation may reuse still-valid consent is Tactical-open unless the happy path demonstrates the need.

This candidate is non-authoritative until explicitly accepted at S1.

### Q3 — overlapping Responsibility Scopes

Unknown: when several Responsibility Scopes simultaneously apply to one side, which approval obligations are required?

Do not freeze obligation cardinality or scope-precedence semantics until S1 accepts a rule.

## Exit criteria

- Q1 has an accepted minimal selection rule sufficient for the MVP happy path;
- Q2 has an accepted consequence for an authorization whose approval obligations materially change;
- Q3 has an accepted rule for the smallest overlapping-scope case required by the MVP, or an explicit non-blocking deferral if overlap is outside the first happy path;
- `docs/requirements/access-governance-g1.md` carries the accepted observable behavior;
- Access Governance Tactical DDD can be revalidated without inventing product behavior;
- no implementation authorization is implied.

## Blockers

Q2 and Q3 remain S1 owner decisions. Repository evidence does not currently contain accepted answers.

For MVP, prefer the smallest behavior that preserves bilateral authorization correctness and does not create a hidden automatic grant when placement/scope meaning changes.

## Next

Obtain the Q2 owner decision. Promote it into `docs/requirements/access-governance-g1.md` only after explicit acceptance. Then address Q3 only to the extent overlapping Responsibility Scopes are required by the first happy path.
