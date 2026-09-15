# Authority Management — Tactical DDD model

## Purpose

Authority Management answers one question:

> may this trusted Actor perform this Action for this Responsibility Scope at this effective time?

AM owns effective actor/action/scope authority and the assignment semantics needed to answer that question. It does not infer authority from Resource ownership, responsibility metadata, UI selection or application hierarchy.

## Correlation values

```text
ActorRef
GroupRef
RoleRef
ActionRef
ResponsibilityScopeRef
```

`ResponsibilityScopeRef` is a stable cross-context correlation value, not a separate Bounded Context. RC uses it for Resource Scope Affiliation, AM uses it for action authority, and AG correlates those independent truths when deriving approval obligations. AM does not own Resource-to-Scope membership.

## Authority model

```text
Actor
  -> effective Group Membership
      -> Group Role Assignment @ ResponsibilityScope
          -> Role permits Action
              -> EffectiveAuthority(actor, action, scope, time)
```

Authority comes from role/group/scope assignment rather than Resource owner, administrator, contact or responsibility metadata.

## AuthorityRole

```text
AuthorityRole {
    roleRef
    permittedActions: Set<ActionRef>
}
```

`roleRef` is stable role identity. Display names and descriptions do not define authority identity. A role owns action permissions; scope belongs to the assignment.

Changing current role permissions changes current and subsequent effective authority. Consuming contexts preserve the authority evidence relevant to decisions they need to explain.

## ActorGroupMembership

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

A membership states that an Actor belongs to one Group during its effective interval. `membershipRef` is stable fact identity. Membership may originate in an external identity source, but AM retains the effective fact and its provenance without owning the external identity-system topology.

## GroupRoleScopeAssignment

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

The assignment grants one Role to one Group within exactly one Responsibility Scope for its effective interval. `assignmentRef` is stable fact identity. Resource identity does not belong in the assignment; Resource correlation is provided by RC `ResourceScopeAffiliation`.

## EffectiveAuthority

For one exact query:

```text
AuthorityQuery {
    actorRef
    actionRef
    responsibilityScopeRef
    effectiveTime
}

EffectiveAuthority =
    Admitted(authorityEvidence)
  | Denied
  | Unknown
```

`Admitted` requires at least one complete effective path:

```text
ActorGroupMembership(actor, group)
AND GroupRoleScopeAssignment(group, role, scope)
AND AuthorityRole(role).permittedActions contains action
```

All matching positive bases may be retained in evidence. Duplicate positive paths do not create additional authority meaning.

`Denied` means AM has sufficient authoritative knowledge and no effective path grants the requested action in the exact requested scope.

`Unknown` means material membership, assignment or role evidence is unavailable, incomplete or unresolved. Consumers protecting approval or mutation fail closed on both `Denied` and `Unknown`.

The authority model is positive-grant based. It contains no explicit deny assignments, deny precedence, policy-expression language, nested-group semantics or role inheritance. Under complete knowledge, absence of an effective positive grant is `Denied`.

## AuthorityEvidence

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

`AuthorityEvidence` is an immutable derived explanation value, not an aggregate. A consuming context may preserve the evidence needed for its own durable decision provenance; later assignment changes do not rewrite an already made decision.

## Scope discovery

```text
EffectiveScopes(actorRef, actionRef, effectiveTime)
    -> Set<ResponsibilityScopeRef> | Unknown
```

Several authority paths to the same scope collapse to one scope value. When a use case requires exactly one selected scope, selection among several admitted scopes belongs to that use case; AM does not choose arbitrarily.

## Domain operations

```text
DefineRole / ChangeRolePermissions
RecordGroupMembership / EndGroupMembership
AssignRoleToGroupInScope / EndRoleAssignment
EvaluateEffectiveAuthority
ListEffectiveScopes
```

These names express domain meaning rather than transport/API commands.

## Invariants

1. Authority is evaluated for an exact `(ActorRef, ActionRef, ResponsibilityScopeRef, effectiveTime)` tuple.
2. Actor identity is trusted input from the authentication/session boundary; caller payload does not manufacture it.
3. Group membership alone grants no action.
4. Role permission alone grants no action without an effective group/scope assignment and Actor membership.
5. Assignment to one Responsibility Scope grants nothing in another scope.
6. Resource Scope Affiliation, responsibility, owner, administrator or contact metadata never substitutes for AM authority.
7. Distinct protected actions may use distinct ActionRefs even when one Actor holds several of them.
8. `Unknown` never degrades to `Admitted`.
9. AM does not decide AG bilateral obligation logic or NEO mutation outcome.
10. AuthorityRole has stable identity and mutable current permissions; memberships and assignments are temporal facts; EffectiveAuthority and AuthorityEvidence are derived values.
