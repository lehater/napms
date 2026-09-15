# Authority Management — MVP Tactical DDD model

Status: `S2 MVP Tactical model aligned 2026-09-15`.

## Purpose

Own one question:

> may this trusted Actor perform this Action for this Scope at this effective time?

Authority Management (AM) owns effective actor/action/scope authority and the authority-assignment semantics needed to answer that question. It does not infer authority from Resource ownership, Resource responsibility metadata, UI selection or application hierarchy.

## Core correlation values

```text
ActorRef
GroupRef
RoleRef
ActionRef
ResponsibilityScopeRef
```

`ResponsibilityScopeRef` is a stable cross-context correlation value, not a separate Bounded Context.

- RC uses it for Resource Scope Affiliation;
- AM uses it for action authority;
- AG correlates those independent truths when deriving approval obligations.

AM does not own Resource-to-Scope membership.

## Authority model

The MVP authority path is:

```text
Actor
  -> effective Group Membership
      -> Group Role Assignment @ ResponsibilityScope
          -> Role permits Action
              -> EffectiveAuthority(actor, action, scope, time)
```

This supports the accepted distributed-governance rule that an employee gains approval/request/operation authority through role/group/scope assignment rather than by being listed as Resource owner/administrator/contact.

## Entity — AuthorityRole

```text
AuthorityRole {
    roleRef
    permittedActions: Set<ActionRef>
}
```

`roleRef` is stable role identity. Role display names/descriptions do not define authority identity.

The role contains only action permissions. Scope is attached by assignment, not embedded permanently into the role.

Changing a Role's current permissions changes future/current effective authority but does not rewrite historical decisions that already preserved their authority evidence.

Exact business role names are deliberately not frozen by Tactical DDD.

## Temporal fact — ActorGroupMembership

```text
ActorGroupMembership {
    membershipRef
    actorRef
    groupRef
    validFrom
    validUntil?
    provenanceRef
}
```

A membership states that an Actor is a member of one Group during its effective interval.

`membershipRef` is stable fact identity because authority decisions may need to explain which membership supported admission at a historical time.

AM may obtain membership from an external authoritative identity source, but the effective membership fact consumed by AM must retain source/provenance. External identity-system topology is not AM domain ownership.

## Temporal fact — GroupRoleScopeAssignment

```text
GroupRoleScopeAssignment {
    assignmentRef
    groupRef
    roleRef
    responsibilityScopeRef
    validFrom
    validUntil?
    provenanceRef
}
```

The assignment grants the Role to the Group within exactly one Responsibility Scope for its effective interval.

`assignmentRef` is stable fact identity because admission evidence may need to refer to the exact assignment basis.

No direct Resource identity belongs in this fact. Resources correlate through RC `ResourceScopeAffiliation`.

## Derived value — EffectiveAuthority

For one exact query:

```text
AuthorityQuery {
    actorRef
    actionRef
    responsibilityScopeRef
    effectiveTime
}
```

AM derives:

```text
EffectiveAuthority =
    Admitted(authorityEvidence)
  | Denied
  | Unknown
```

### Admitted

`Admitted` requires at least one complete effective path at the query time:

```text
ActorGroupMembership(actor, group)
AND GroupRoleScopeAssignment(group, role, scope)
AND AuthorityRole(role).permittedActions contains action
```

All matching positive bases for the same exact actor/action/scope may be retained in evidence. Duplicate positive paths do not create additional authority meaning.

### Denied

`Denied` means AM has sufficient authoritative knowledge for the query and no effective path grants the requested action in the exact requested scope.

### Unknown

`Unknown` means AM cannot establish a trustworthy admitted-or-denied answer because material membership/assignment/role evidence is unavailable, incomplete or unresolved.

Consumers that protect mutation/approval must fail closed on both `Denied` and `Unknown`.

## Authority evidence

```text
AuthorityEvidence {
    actorRef
    actionRef
    responsibilityScopeRef
    evaluatedAt
    supportingMembershipRefs[1..N]
    supportingAssignmentRefs[1..N]
    supportingRoleRefs[1..N]
    provenanceRefs[1..N]
}
```

This is an immutable derived explanation value, not a new aggregate.

A consuming context may preserve the relevant evidence/reference in its own historical decision provenance. Later membership/role/assignment changes do not rewrite the historical fact that authority was valid at decision time.

## Scope discovery

AM may also derive the set of scopes for which an Actor has effective authority for one Action at a time:

```text
EffectiveScopes(actorRef, actionRef, effectiveTime)
    -> Set<ResponsibilityScopeRef> | Unknown
```

The set contains distinct scope references; several authority paths to the same scope collapse to the same scope value.

If a consuming use case requires the user to operate in exactly one selected scope, ambiguity between several admitted scopes is that use case's selection problem. AM does not arbitrarily choose one scope.

A consumer may impose a stricter unique-basis rule for a particular accepted action contract, but that does not change the core meaning of effective authority.

## Domain operations

Minimum semantic operations:

```text
DefineRole / ChangeRolePermissions
RecordGroupMembership / EndGroupMembership
AssignRoleToGroupInScope / EndRoleAssignment
EvaluateEffectiveAuthority
ListEffectiveScopes
```

These are domain meanings, not frozen API/command names.

## Invariants

1. Authority is evaluated for an exact `(ActorRef, ActionRef, ResponsibilityScopeRef, effectiveTime)` tuple.
2. An Actor's authenticated identity is trusted input from the authentication/session boundary; caller payload does not manufacture ActorRef.
3. Group membership alone grants no action.
4. Role permission alone grants no action without an effective group/scope assignment and Actor membership.
5. Assignment to one Responsibility Scope does not grant the same action in another scope.
6. Resource Scope Affiliation/Responsibility/owner/admin/contact metadata never substitutes for AM authority.
7. Request initiation, approval, withdrawal, catalogue curation, protected reads and network execution may use distinct ActionRefs even when one Actor holds several of them.
8. Historical consuming decisions retain their authority evidence; later loss of authority changes current/future admission only.
9. `Unknown` never degrades to `Admitted`.
10. AM does not decide bilateral AG obligation logic or NEO mutation outcome; it only answers authority.

## No explicit deny policy in MVP

The accepted MVP authority model is positive grant by role assignment. It does not introduce explicit deny assignments, deny precedence, policy expressions or ABAC rule evaluation.

Absence of an effective positive grant under complete knowledge is `Denied`.

If explicit deny/precedence becomes a product requirement, it must be introduced as new authority semantics rather than inferred from missing assignments.

## Lifecycle classification

- AuthorityRole has stable identity and mutable current permitted-action meaning.
- ActorGroupMembership and GroupRoleScopeAssignment are temporal authority facts with stable fact references and effective intervals.
- EffectiveAuthority/AuthorityEvidence are derived immutable values for one query/time.
- ResponsibilityScopeRef is correlation value, not AM-owned aggregate identity.

No generic workflow/state machine is required.

## Deliberately deferred

- nested groups;
- role inheritance/hierarchy;
- explicit deny rules/precedence;
- quorum/multi-actor authority policies;
- attribute-expression/ABAC language;
- Organizational Unit mapping to Responsibility Scope;
- exact business role names such as whether approve and withdraw share one role;
- enterprise IAM synchronization mechanism;
- persistence/schema/transport representation.

## Tactical coherence result

AM now has sufficient target Tactical semantics for all current MVP consumers:

- AG can ask whether an Actor may request/approve/withdraw for one Responsibility Scope and time;
- AP/catalogue/workspaces can evaluate protected actions without inferring authority from ownership metadata;
- NEO can require independent mutation authority;
- historical decisions can retain authority basis without freezing current assignments forever;
- unknown authority fails closed;
- no future RBAC/ABAC framework is pre-built into the domain.
