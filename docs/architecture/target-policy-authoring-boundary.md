# Target policy authoring and compatibility boundary

Status: `S3 target boundary candidate aligned to formal RuleChange decisions 2026-09-16`.

## Purpose

Define how the revalidated target domain is introduced beside the current implemented runtime without reinterpreting legacy identities or embedding customer-specific approval workflow into the MVP architecture.

This document complements `first-mvp-policy-lifecycle-export.md` and focuses on owner package/persistence migration for policy creation.

## Required target owners for policy creation

```text
ACC Application / Component / Interaction / revision
RC Resource / AddressSpace
AD ComponentDeployment
BC BusinessProcess / ConnectivityNeed
AM optional protected-action authority
        |
        v
AP PolicyRule / RuleChange / formal decision
```

ACC, RC and AM have implemented capabilities that can be adapted through published application contracts. Target AD and target BC do not currently have authoritative runtime packages and must be introduced rather than inferred from incompatible legacy owners.

## Business Connectivity implementation boundary

### Why legacy `connectivity_requirements` is not the target owner

Current `contexts/connectivity_requirements` identifies a requirement using concrete compatibility ComponentDeployment identities, DCS revision and governance scope. Target `ConnectivityNeed` intentionally does **not** use concrete deployment or exact revision identity and may outlive them.

Legacy ConnectivityRequirement rows therefore cannot be treated as target ConnectivityNeed rows or target BC persistence. No automatic identity cast/migration is accepted.

### Target package

Introduce:

```text
contexts/business_connectivity/
  domain/
  application/
  infrastructure/
    persistence/postgres/
  presentation/http/
```

Minimum first-policy-authoring capabilities:

```text
CreateBusinessProcess
Get/ListBusinessProcesses
CreateConnectivityNeed
Get/ListConnectivityNeeds
SetNeedCurrentness / retire-equivalent operation only if required by accepted UI flow
ResolveCurrentConnectivityNeed
```

The implementation must not recreate a general BPM/workflow engine.

### Target persistence

BC persistence is separate from legacy ConnectivityRequirement persistence. It stores stable Process/Need identities, stable ACC `InteractionRef`, business basis/provenance and currentness/lifecycle required by accepted semantics.

No cross-context SQL foreign keys to ACC or authority tables.

## Application Deployment implementation boundary

Introduce target `contexts/application_deployment/` as defined by `first-mvp-policy-lifecycle-export.md`.

Do not use ACC `ApplicationDeployment`, `DeploymentInteraction`, compatibility ComponentDeployment or deployment Resource-set/binding rows as authoritative target ComponentDeployment persistence.

Target AD records are explicitly created from an accepted ACC `ComponentRef` and RC `ResourceRef`.

## Access Policy side-by-side migration inside one BC

### Preserve current implemented AccessRule model

The implemented `contexts/access_policy/domain/model.py` and existing application paths remain as-built dependencies of current workspaces, normalized-policy export and compatibility tests.

Do not replace that model in-place in the first target implementation commit.

### Introduce target PolicyRule model beside it

Within the same semantic context package, add target code-level models/modules, for example:

```text
contexts/access_policy/
  domain/
    model.py                    # current as-built AccessRule compatibility model
    policy_rule.py              # target PolicyRule / RuleChange model
  application/
    ...legacy current files...
    submit_rule_change.py
    decide_rule_change.py
    withdraw_policy_rule.py
    read_policy_rules.py
  infrastructure/
    persistence/postgres/
      ...legacy repositories...
      target_policy_rules.py
```

Exact filenames may vary in S4, but target and compatibility models must remain mechanically distinguishable until migration is complete.

### Separate target persistence

Target PolicyRule/RuleChange persistence uses new tables or an equally explicit namespace that cannot be mistaken for legacy AccessRule storage.

Target repository uniqueness/concurrency applies only to target records:

```text
one non-Retired target PolicyRule
per (source target ComponentDeploymentRef,
     destination target ComponentDeploymentRef)
```

The repository also enforces at most one Pending RuleChange per Active target PolicyRule for the MVP.

### No dual writes

A target Rule mutation writes target AP persistence only. It does not create/update a legacy AccessRule or ConnectivityDecision merely to keep old screens populated.

Legacy mutations remain on the compatibility path until an explicit migration/cutover is accepted.

## Formal decision architecture

The target AP application surface needs only one decision use case for the MVP:

```text
DecideRuleChange(ruleChangeId, Accepted | Rejected)
```

The authenticated actor/time are server-owned. Decision provenance may include an external workflow/ticket reference when supplied by a trusted integration contract.

The AP domain does not expose separate source/destination decision commands, approval-basis APIs, approval quorum endpoints or Responsibility Scope-derived approval routing.

Authority Management may protect `SubmitRuleChange`, `DecideRuleChange` and `WithdrawPolicyRule` at the application boundary when configured. The authority adapter returns action admission; it does not become a multi-party approval engine.

## ACC target communication compatibility

Current ACC implementation contains as-built compatibility models and target-era content predating the revalidation.

Target implementation must expose an ACC-owned application contract aligned with:

```text
Application
Component
Interaction
InteractionContractRevision
```

Target AP/AD/BC code must not import ACC compatibility `ApplicationDeployment`, `DeploymentInteraction`, compatibility `ComponentDeployment` or private DCS models.

Where current authored Interaction traffic can be exposed as exact immutable target revision semantics, an ACC-owned adapter may bridge current persistence only when identity/history mapping is exact. Otherwise target submission fails closed rather than manufacturing a revision.

## Resource Catalogue and Authority Management

RC and AM remain independent semantic owners.

Target AD/AP/workflows may reuse implemented RC/AM capabilities only through owner contracts. No target migration copies Resource, AddressSpace, ResponsibilityScope or role/membership truth into target AP tables.

RC ResourceScopeAffiliation is **not** a required input to baseline `DecideRuleChange`; it remains available for other product capabilities and future customer-specific governance extensions.

## Target policy creation composition

Target HTTP/application composition remains synchronous for the local MVP:

```text
1. user selects current ConnectivityNeed
2. user selects source/destination target ComponentDeployment
3. user selects exact ACC revision compatible with endpoint Components
4. AP resolves Need/revision/deployments
5. AP validates submission action authority when configured
6. AP creates/reuses target PolicyRule and creates one Pending RuleChange
7. an authorized actor/integration records Accepted or Rejected
8. Accepted atomically sets effectiveRevisionRef to the RuleChange revision
9. Rejected preserves the previous effectiveRevisionRef unchanged
```

No asynchronous broker/saga is required. No approval-basis snapshot or source/destination decision rows are required by the MVP architecture.

An external customer workflow may perform any richer approval procedure and then call the same formal decision use case. NAPMS stores the final decision/provenance, not the external workflow internals.

## Withdrawal

`WithdrawPolicyRule` clears current effectiveness and stores formal withdrawal actor/time/provenance in the AP aggregate transaction.

Withdrawal is not retirement. A later reauthorization requires a new RuleChange and a new Accepted formal decision.

## Web coexistence

Current legacy policy/application screens remain available as as-built behavior until deliberately migrated.

Target UI features use target APIs and display target concepts explicitly:

```text
Business Process / Connectivity Need
Component Deployment
Policy Rule / Rule Change
Pending / Accepted / Rejected
Vendor-Neutral Policy Export
```

The target UI must not present baseline source/destination approval steps that no longer exist in domain semantics. A future customer-specific workflow integration can add its own presentation without changing the core RuleChange state model.

## Migration/cutover rules

A later migration from legacy records to target records requires a separate accepted plan when exact mapping can be proven.

For every migrated object the migration must establish, without guessing:

- target ComponentDeployment identity for each endpoint;
- one Resource per target deployment;
- target ACC Interaction/immutable revision identity;
- target Business Connectivity Need/business basis where required;
- target PolicyRule sameness and current effective revision;
- explainable historical provenance.

If any mapping is one-to-many, many-to-one, absent or ambiguous, automatic migration is not lossless and the affected record remains legacy until explicit migration behavior is accepted.

## Architecture invariants

- target BC/AD/AP identities are never aliases for legacy Requirement/ACC compatibility IDs merely because field shapes look similar;
- target AP and legacy AccessRule may coexist physically, but only one model owns each record's semantics;
- no target mutation dual-writes legacy semantic state;
- peer owner data crosses through application contracts/ports, never direct table joins in mutation logic;
- baseline target RuleChange decision is one `Accepted | Rejected` outcome, not a hidden bilateral workflow;
- Resource Scope Affiliation is not a mandatory AP decision dependency;
- policy export target path reads target effective PolicyRules only; legacy normalized-policy reads legacy AccessRules only;
- as-built reconstruction docs remain valid until corresponding compatibility runtime is removed.
