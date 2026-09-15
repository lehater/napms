# Policy Realization Reconciliation — G1 Requirements Passport

Status: `G1 revalidated and aligned to current ACC/AD/RC/NEP/APR ownership 2026-09-15`.

## Problem / outcome

The system must distinguish what is semantically authorized from what the network currently realizes. Authorization, materialization, configured-policy observation, reconciliation and execution are separate truths.

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

5. A semantically authorized Policy Rule remains valid when technical materialization is unresolved; the realization outcome is `Unresolved/Uncomparable`, not silent omission.
6. Required technical policy is derived from the aggregate of all effective semantic authorizations.
7. Equivalent technical predicates may be supported by several Policy Rules; deduplication preserves provenance.
8. Withdrawal of one authorization shall not remove technical access still required by another current authorization.
9. Withdrawal/regrant changes required policy by recomputation; it is never interpreted as “delete the ACL line originally created for this Rule”.
10. Configured technical state carries freshness/provenance sufficient to distinguish trustworthy current evidence from stale/unknown evidence.
11. Execution success does not prove semantic convergence; convergence requires later provider observation/interpretation and comparison again.
12. `missing`, `excess`, `Realized`, `Drift`, `Uncomparable` and semantic authorization remain distinct meanings.
13. In the first MVP, automatic remediation is additive-only on `missing`; `excess` is report/audit evidence and does not authorize automatic removal/narrowing without a separately accepted managed-policy scope.

## Current semantic-to-technical materialization

For one effective Access Policy Rule:

```text
GovernedInteractionSubject
    InteractionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef

ACC InteractionContractRevision
    -> source/destination ComponentRef
    -> complete immutable trafficAlternatives

AD source ApplicationDeployment + source Component
    -> all current applicable ComponentPlacement(ResourceRef)

AD destination ApplicationDeployment + destination Component
    -> all current applicable ComponentPlacement(ResourceRef)

RC each ResourceRef
    -> effective AddressSpace [0..1] = HostAddress | Prefix

supported technical pairs
    -> NEP FirewallCandidate[] / accessListNames[]
    -> TargetRequiredPolicy[] grouped by ComparisonScope
```

Every applicable placement is part of completeness. Downstream materialization must not arbitrarily choose one Resource when a Component has several placements.

A complete empty placement set and an unavailable/unresolved placement result are distinct.

For the first end-to-end MVP edge, only `HostAddress -> HostAddress` pairs are submitted to NEP. `Prefix` remains valid RC truth but makes the current materialization unresolved; it is never expanded into hosts merely to continue the pipeline.

The current comparison scope is:

```text
ComparisonScope = firewallId + accessListName
```

A missing candidate target or missing access-list locator leaves the affected required materialization unresolved rather than creating an empty policy.

## Configured-policy interpretation

Provider ordering, deny/default behavior, objects/groups, aliases and native syntax are interpreted by the Provider Policy Interpreter integration capability before APR comparison.

APR receives a `ConfiguredEffectivePolicySnapshot` with explicit scope, completeness, unsupported-semantics information, freshness and provenance.

TAE may record source-qualified technical evidence but does not decide which evidence is the current complete configured-policy truth for APR.

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
- Resource address/placement changes do not redefine semantic authorization subject identity by themselves.

## Current ownership

- AP owns current semantic authorization.
- ACC owns immutable InteractionContractRevision traffic meaning.
- AD owns ApplicationDeployment and ComponentPlacement truth.
- RC owns Resource AddressSpace.
- NEP owns candidate Firewall/policy-locator relevance.
- RPM is derived composition producing complete TargetRequiredPolicy or unresolved.
- Provider Policy Interpreter owns provider-native interpretation.
- APR owns comparison, semantic delta, accepted change design and semantic verification.
- Provider Policy Renderer owns provider-native rendering of verified intent.
- NEO owns controlled mutation lifecycle/outcome.

No additional peer Bounded Context is introduced merely for the composition steps above.
