# Policy Realization Reconciliation — G1 Requirements Passport

Status: `cross-capability G1 checkpoint; ownership/BC grouping unresolved`.

Date/source: stakeholder revalidation, 2026-09-14.

## Problem / outcome

The system must distinguish what is semantically authorized from what the network currently realizes. Approval/revocation and network convergence are separate facts.

## Observable requirements

1. Current semantic authorization and observed technical realization shall be represented as independent truths.
2. The system shall distinguish missing required access from technically present access that is no longer required/authorized.
3. Reconciliation shall compare normalized effective permit semantics, not raw vendor ACL rows.
4. Conceptually, reconciliation shall distinguish `common = required ∩ observed`, `missing = required - observed`, and `excess = observed - required`.
5. A Policy Rule that cannot yet be translated to technical predicates because address/endpoint/placement/policy-locator evidence is missing shall remain semantically valid while realization is reported as unresolved with a reason.
6. Required technical policy shall be derived from the aggregate of all effective semantic authorizations.
7. A normalized technical predicate may be supported by multiple Policy Rules; deduplication shall preserve provenance.
8. Revoking one authorization shall not remove technical access still required by another effective authorization.
9. Revocation shall trigger recomputation/reconciliation of aggregate desired effective policy rather than an assumed one-to-one deletion of a historical ACL line.
10. Observed technical state shall carry freshness/provenance sufficient to distinguish fresh observation from stale last-known state.
11. Successful execution of a network change shall not by itself prove convergence. A post-check shall compare subsequently observed normalized effective state with desired state.
12. Missing required access and still-present unauthorized/excess access shall remain semantically distinguishable so downstream consumers may prioritize them differently.

## Semantic-to-technical materialization

For MVP, the working derivation is:

```text
Policy Rule
    source/destination Deployment
        -> exactly one Resource per Deployment
        -> all current ResourceEndpoints
        -> current corporate-visible prefix, when present
    Interaction
        -> required protocol/port semantics
    => normalized technical predicates
```

Technical candidate predicates are then scoped through NEP candidate enforcement locations/policy locators and target-specific required policy before APR designs a correction.

## Normalization principle

Internal network-policy reasoning should operate on normalized effective allowed/permit space. Vendor-specific ordering, deny/default semantics, objects/groups and syntax are interpreted at integration boundaries. Provider-specific rendering belongs at the execution/adapter boundary rather than in the semantic policy model.

## Important negative requirements

- `Authorized` is not `Realized`.
- `Revoked` is not `RemovedFromFirewall`.
- NEO command success is not proof of post-state convergence.
- One Policy Rule is not assumed to equal one firewall/ACL row.
- No-address/unresolved realization is not silently treated as an empty required policy.
- Stale observed state must not be presented as fresh certainty.

## Capability clues, not BC decisions

- Required Access Materialization
- Target Policy Projection
- Policy Realization Reconciliation
- APR semantic comparison/change design
- NEO execution/post-check

The first three may be application composition rather than peer Bounded Contexts. This passport intentionally does not decide that boundary.
