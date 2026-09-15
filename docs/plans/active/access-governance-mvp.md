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
- a material change of approval obligations withdraws current authorization until the current obligations are satisfied again;
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

### Q2 — obligation change after placement/scope change — ACCEPTED

If a placement or Resource Scope Affiliation change leaves the effective approval obligations materially unchanged, current authorization remains effective.

If the effective approval obligations materially change, current authorization ceases to be effective and AG publishes `AuthorizationWithdrawn` with provenance identifying the obligation-change cause. The same governed subject may become authorized again only after the current obligations are satisfied and AG publishes a new `AuthorizationGranted`.

Historical Requests/approvals remain evidence and do not silently satisfy a materially changed obligation set. MVP introduces no separate `Suspended` product state. Exact treatment of still-valid individual consent facts is Tactical-open so long as no grant remains effective without all current obligations being satisfied.

### Q3 — overlapping Responsibility Scopes — CURRENT

RC permits one Resource to have several different effective Responsibility Scope affiliations; there is no accepted scope hierarchy or precedence rule.

Minimal MVP candidate for owner decision, not yet accepted:

```text
The first happy path supports exactly one distinct applicable Responsibility Scope
per governance side.

If more than one distinct Responsibility Scope is simultaneously applicable to a
source or destination side, approval obligations are unresolved for MVP and the pair
is not selectable/authorizable under the Q1 selection rule.
```

This is a fail-closed explicit deferral of generalized overlapping-scope semantics. It does not choose an arbitrary winning scope and does not introduce mandatory approval by every overlapping scope before a concrete requirement needs that behavior.

## Exit criteria

- Q1 has an accepted minimal selection rule sufficient for the MVP happy path;
- Q2 has an accepted consequence for an authorization whose approval obligations materially change;
- Q3 has an accepted rule for the smallest overlapping-scope case required by the MVP, or an explicit non-blocking deferral if overlap is outside the first happy path;
- `docs/requirements/access-governance-g1.md` carries the accepted observable behavior;
- Access Governance Tactical DDD can be revalidated without inventing product behavior;
- no implementation authorization is implied.

## Blockers

Only Q3 remains an S1 owner decision for this MVP governance checkpoint.

The repository contains no accepted hierarchy/precedence between simultaneously applicable Responsibility Scopes. For MVP, do not invent one.

## Next

Resolve Q3. Prefer the explicit fail-closed deferral above unless the first happy path requires multi-scope approval. After Q3 is accepted or explicitly deferred, evaluate G1 closure for the affected Access Governance behavior and return to Tactical AG revalidation.
