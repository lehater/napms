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

Unknown: when current placement or Resource Scope Affiliation changes alter the required approvers/scopes, does an existing authorization remain valid, require reapproval, suspend, or withdraw?

This is product behavior and must not be invented by Tactical DDD.

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

Resolve Q2. Promote only an explicit owner decision into `docs/requirements/access-governance-g1.md`. Then address Q3 only to the extent overlapping Responsibility Scopes are required by the first happy path.
