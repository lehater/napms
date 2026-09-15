# Policy Realization Reconciliation requirements

## Purpose

Keep semantic authorization, required technical policy, observed configured policy, reconciliation and execution as separate truths.

## Required comparison behavior

1. Current semantic authorization and configured technical realization are independent.
2. Reconciliation distinguishes missing required access from configured access not explained by current required policy.
3. Comparison operates on normalized effective permit semantics rather than raw provider ACL rows.
4. For complete comparable permit spaces:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

5. An authorized Policy Rule remains valid when technical materialization is unresolved; the realization result is unresolved/uncomparable rather than silently omitted.
6. Required technical policy is derived from the aggregate of all effective semantic authorizations.
7. Equivalent technical predicates may be supported by several Policy Rules; technical deduplication preserves provenance.
8. Withdrawal of one authorization does not remove technical access still required by another current authorization.
9. Withdrawal or regrant changes required policy by recomputation, never by identifying one provider row as “owned” by one Policy Rule.
10. Configured technical state carries enough completeness/freshness/provenance information for APR to determine whether comparison is trustworthy.
11. Execution success does not prove semantic convergence; convergence requires later provider observation/interpretation and comparison.
12. `missing`, `excess`, `Realized`, `Drift`, `Uncomparable` and semantic authorization remain distinct meanings.
13. Automatic remediation is additive-only for `missing`. `excess` is report/audit evidence and does not authorize automatic removal or narrowing.

## Semantic-to-technical materialization

For one effective Access Policy Rule:

```text
GovernedInteractionSubject
    InteractionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef

ACC InteractionContractRevision
    -> source/destination ComponentRef
    -> complete immutable trafficAlternatives

AD source/destination ApplicationDeployment + endpoint Component
    -> all current applicable ComponentPlacement(ResourceRef)

RC each ResourceRef
    -> current AddressSpace [0..1] = HostAddress | Prefix

supported technical pairs
    -> NEP FirewallCandidate[] / accessListNames[]
    -> TargetRequiredPolicy[] grouped by ComparisonScope
```

Every applicable placement is part of completeness. A complete empty placement set is distinct from unavailable or unresolved placement truth.

The current materialization edge submits only `HostAddress -> HostAddress` pairs to NEP. A `Prefix` remains valid RC truth but makes that materialization unresolved; it is not expanded into host addresses merely to continue processing.

Current comparison scope:

```text
ComparisonScope = firewallId + accessListName
```

Missing candidate targets or missing policy locators leave affected materialization unresolved rather than producing an empty required policy.

## Configured-policy interpretation

Provider ordering, deny/default behavior, objects/groups, aliases and native syntax are interpreted by the Provider Policy Interpreter before APR comparison.

APR receives a `ConfiguredEffectivePolicySnapshot` with explicit comparison scope, completeness, unsupported-semantics information, freshness and provenance. TAE may record source-qualified evidence but does not choose the configured snapshot that APR treats as current and complete.

## APR outcomes

APR compares one complete `TargetRequiredPolicy` with one complete configured snapshot for the same ComparisonScope.

```text
Realized <=> missing is empty AND excess is empty
Drift    <=> missing is non-empty OR excess is non-empty
```

Mismatched, incomplete, unknown or unsupported inputs are `Uncomparable`, not `Drift` or `Realized`.

## Remediation boundary

```text
missing != empty
    -> APR may produce VerifiedChangeIntent(ENSURE-PERMIT)

excess
    -> report/audit only
    -> no automatic REMOVE/NARROW/REPLACE

Realized or Uncomparable
    -> no mutation intent
```

An additive intent covers selected missing permit space and does not narrow already configured access. If excess also exists, additive remediation may satisfy required permits while excess remains. `Realized` still requires a new observation and comparison.

## Ownership

- AP owns current semantic authorization.
- ACC owns immutable InteractionContractRevision traffic meaning.
- AD owns ApplicationDeployment and ComponentPlacement truth.
- RC owns Resource AddressSpace.
- NEP owns enforcement candidate/policy-locator relevance.
- Required Policy Materialization is derived composition producing complete `TargetRequiredPolicy` or unresolved.
- Provider Policy Interpreter owns provider-native interpretation into configured effective policy.
- APR owns comparison, semantic delta and verified source-neutral change intent.
- Provider Policy Renderer owns provider-native rendering of verified intent.
- NEO owns controlled mutation lifecycle and outcome.

No additional Bounded Context is implied for these composition steps.
