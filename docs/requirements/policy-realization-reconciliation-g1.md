# Policy Realization Reconciliation — G1 Requirements Passport

Status: `G1 revalidated for concrete Component Deployment policy endpoints 2026-09-16`.

## Problem / outcome

The system must distinguish what is semantically authorized from what the network currently realizes. Authorization, technical materialization, configured-policy observation, reconciliation and execution are separate truths.

## Observable requirements

1. Current semantic authorization and configured technical realization shall remain independent truths.
2. Reconciliation shall distinguish missing required access from technically present access not explained by current required policy.
3. Comparison shall use normalized effective permit semantics, not raw provider ACL rows.
4. For complete comparable permit spaces:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

5. A semantically authorized Policy Rule remains authoritative when technical materialization is unresolved; the realization outcome is `Unresolved/Uncomparable`, not silent omission.
6. Required technical policy is derived from the aggregate of all effective semantic authorizations.
7. Equivalent technical predicates may be supported by several Policy Rules; deduplication preserves provenance.
8. Withdrawal of one authorization shall not remove technical access still required by another current authorization.
9. Withdrawal/regrant or an approved traffic-revision change changes required policy by recomputation; it is never interpreted as “edit/delete the provider ACL row originally created for this Rule”.
10. Configured technical state carries freshness/provenance sufficient to distinguish trustworthy current evidence from stale/unknown evidence.
11. Execution success does not prove semantic convergence; convergence requires later provider observation/interpretation and comparison again.
12. `missing`, `excess`, `Realized`, `Drift`, `Uncomparable` and semantic authorization remain distinct meanings.
13. In the first remediation slice, automatic remediation is additive-only on `missing`; `excess` is report/audit evidence and does not authorize automatic removal/narrowing without a separately accepted managed-policy scope.

## Current semantic-to-technical materialization

For one effective Policy Rule:

```text
Policy Rule
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    revisionRef

ACC exact Interaction Contract Revision
    -> owning Interaction
    -> source/destination ComponentRef
    -> complete immutable trafficAlternatives

source Component Deployment
    -> expected source ComponentRef
    -> exactly one ResourceRef for first MVP

destination Component Deployment
    -> expected destination ComponentRef
    -> exactly one ResourceRef for first MVP

RC each ResourceRef
    -> effective AddressSpace [0..1] = HostAddress | Prefix

supported technical pair
    -> NEP FirewallCandidate[] / accessListNames[]
    -> TargetRequiredPolicy[] grouped by ComparisonScope
```

The materializer shall verify that each concrete Component Deployment realizes the corresponding endpoint Component of the exact revision's Interaction.

A replica of a Component on another Resource is a different Component Deployment. It contributes required technical policy only when effective policy authorizes a concrete connection using that deployment; materialization does not automatically expand one Rule across every replica of the same Component definition.

A missing/unavailable Component Deployment, Resource binding or AddressSpace is distinct from an empty required policy.

For the first end-to-end NEP edge, only `HostAddress -> HostAddress` pairs are submitted to NEP. `Prefix` remains valid RC truth but makes the current target-specific materialization unresolved; it is never expanded into hosts merely to continue the pipeline.

The current comparison scope is:

```text
ComparisonScope = firewallId + accessListName
```

A missing candidate target or missing access-list locator leaves the affected required materialization unresolved rather than creating an empty policy.

## Configured-policy interpretation

Provider ordering, deny/default behavior, objects/groups, aliases and native syntax are interpreted by the Provider Policy Interpreter integration capability before APR comparison.

APR receives a `ConfiguredEffectivePolicySnapshot` with explicit scope, completeness, unsupported-semantics information, freshness and provenance.

TAE may record source-qualified technical evidence but does not decide which evidence is the current complete configured-policy truth for APR. Traffic-derived evidence may separately feed recognition of access candidates; such recognition is not effective policy.

## APR outcome

APR compares one complete `TargetRequiredPolicy` with one complete configured snapshot for the same ComparisonScope.

```text
Realized <=> missing is empty AND excess is empty
Drift    <=> missing is non-empty OR excess is non-empty
```

Mismatched/incomplete/unknown/unsupported inputs are `Uncomparable`, not `Drift` or `Realized`.

## Current remediation boundary

```text
missing != empty
    -> APR may produce VerifiedChangeIntent(ENSURE-PERMIT)

excess
    -> report/audit only
    -> no automatic REMOVE/NARROW/REPLACE

Realized or Uncomparable
    -> no mutation intent
```

An additive verified intent must cover the selected missing permit space and must not narrow already configured access. If `excess` also exists, additive remediation may satisfy all required permits while excess remains; final `Realized` still requires a new observation/comparison.

## Important negative requirements

- `Authorized` is not `Realized`.
- `Withdrawn` is not `RemovedFromFirewall`.
- NEO success is not convergence proof.
- one Policy Rule is not one provider ACL row.
- unresolved materialization is not empty required policy.
- incomplete configured evidence is not empty configured policy.
- `excess` is not automatic deletion authority.
- Resource address changes do not redefine the concrete Component Deployment pair authorized by a Rule.
- a second deployment of the same Component does not inherit another deployment's Policy Rule automatically.

## Current ownership constraints for S2

The current requirements establish these semantic facts without deciding final Bounded Context boundaries:

- ACC owns Application/Component/Interaction and immutable revision traffic meaning;
- concrete Component Deployment truth must identify one Component on one Resource;
- RC owns Resource AddressSpace;
- current Policy Rule truth identifies the concrete directed Component Deployment pair and exact current revision;
- target-specific materialization remains derived composition and owns no independent authorization/deployment/resource truth;
- NEP/APR/provider/NEO responsibilities remain separate from semantic authorization.

The final owner/name of Component Deployment and the governance/current-policy context split are S2 decisions.
