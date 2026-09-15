# Target policy authoring and compatibility boundary

Status: `S3 accepted target boundary candidate 2026-09-16`.

## Purpose

Define how the revalidated target domain is introduced beside the current implemented runtime without reinterpreting legacy identities.

This document complements `first-mvp-policy-lifecycle-export.md` and focuses on owner package/persistence migration for the policy-creation path.

## Required target owners for policy creation

The first product goal is not only export: a user must be able to establish the semantic inputs required to create an effective target PolicyRule.

The target authoring dependency chain is:

```text
ACC Application / Component / Interaction / revision
RC Resource / AddressSpace / scope affiliation
AD ComponentDeployment
BC BusinessProcess / ConnectivityNeed
AM authority
        |
        v
AP PolicyRule / RuleChange / approvals
```

ACC, RC and AM have implemented capabilities that can be adapted through published application contracts. Target AD and target BC do not currently have authoritative runtime packages. They must be introduced rather than inferred from incompatible legacy owners.

## Business Connectivity implementation boundary

### Why legacy `connectivity_requirements` is not the target owner

Current `contexts/connectivity_requirements` identifies a requirement using concrete compatibility ComponentDeployment identities, DCS revision and governance scope. Target `ConnectivityNeed` intentionally does **not** use concrete deployment or exact revision identity and may outlive them.

Therefore legacy ConnectivityRequirement rows cannot be treated as target ConnectivityNeed rows or target BC persistence.

No automatic identity cast/migration is accepted.

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
ResolveCurrentConnectivityNeed   # AP-owned adapter consumes this contract
```

The target implementation only needs the semantic subset already accepted by Business Connectivity G1/Tactical DDD; it must not recreate BPM/workflow-engine behavior.

### Target persistence

BC persistence is separate from legacy ConnectivityRequirement persistence. It stores stable Process/Need identities, stable ACC `InteractionRef`, business basis/provenance and currentness/lifecycle information required by the accepted model.

No cross-context SQL foreign keys to ACC or organization/authority tables.

## Application Deployment implementation boundary

Introduce target `contexts/application_deployment/` exactly as defined by `first-mvp-policy-lifecycle-export.md`.

Do not use:

- ACC `ApplicationDeployment` rows;
- ACC `DeploymentInteraction` rows;
- ACC compatibility ComponentDeployment rows;
- deployment Resource-set/binding rows

as authoritative target ComponentDeployment persistence.

Those objects may remain as-built compatibility input for old APIs only.

Target AD records are created explicitly from an accepted ACC `ComponentRef` and RC `ResourceRef`.

## Access Policy side-by-side migration inside one BC

### Preserve current implemented AccessRule model

The implemented `contexts/access_policy/domain/model.py` and existing application paths are as-built dependencies of current AccessRule workspaces, normalized-policy export and compatibility tests.

Do not replace that model in-place in the first target implementation commit.

### Introduce target PolicyRule model beside it

Inside the same semantic context package, add a target model with distinct code-level names/modules, for example:

```text
contexts/access_policy/
  domain/
    model.py                    # current as-built AccessRule compatibility model
    policy_rule.py              # target PolicyRule / RuleChange model
  application/
    ...legacy current files...
    submit_rule_change.py       # target
    decide_rule_change.py       # target
    withdraw_policy_rule.py     # target
    read_policy_rules.py        # target
  infrastructure/
    persistence/postgres/
      ...legacy repositories...
      target_policy_rules.py    # target repository/schema mapping
```

Exact filenames may vary in S4, but target and compatibility models must remain mechanically distinguishable until migration is complete.

### Separate target persistence

Target PolicyRule/RuleChange persistence must use new tables or an equally explicit namespace that cannot be mistaken for the legacy AccessRule schema.

Target repository uniqueness/concurrency applies only to target records:

```text
one non-Retired target PolicyRule
per (source target ComponentDeploymentRef,
     destination target ComponentDeploymentRef)
```

Legacy rows retain their existing semantic identity and behavior.

### No dual writes

A target Rule mutation writes target AP persistence only. It does not also create/update a legacy AccessRule/ConnectivityDecision row merely to keep old screens populated.

A legacy mutation remains on the compatibility path until an explicit migration/cutover is accepted.

Dual writing two different semantic models would create unclear authority and partial-failure behavior and is therefore prohibited for the first target slice.

## ACC target communication compatibility

Current ACC implementation contains both as-built compatibility models and a `target_model.py` whose `ApplicationDeployment`/`DeploymentInteraction` content predates the 2026-09-16 revalidation.

Target implementation must align ACC's **published application contract** with the accepted ACC domain:

```text
Application
Component
Interaction
InteractionContractRevision
```

The target AP/AD/BC code must not import ACC `target_model.ApplicationDeployment`, `DeploymentInteraction`, compatibility `ComponentDeployment` or DCS private models.

Where current authored Interaction traffic must be exposed as immutable target revision semantics, implement an ACC-owned application projection/adapter that publishes the accepted revision contract. It may internally bridge current persistence only when the mapping is exact and preserves immutable revision identity/history.

If exact revision history cannot be reconstructed for a current authored object, target policy submission fails closed for that object rather than manufacturing a target revision.

## Resource Catalogue and Authority Management

RC and AM remain semantic owners and are consumed through application/integration adapters.

Target AD/AP/workflows may reuse implemented RC/AM persistence only through their owner contracts. No target migration copies Resource, AddressSpace, ResponsibilityScope or role/membership truth into target tables.

## Target policy creation composition

Target HTTP/application composition is synchronous for the local MVP:

```text
1. user selects current ConnectivityNeed
2. user selects source/destination target ComponentDeployment
3. user selects exact ACC revision compatible with endpoint Components
4. AP resolves Need/revision/deployments
5. AP resolves both Resource scope affiliations
6. AP validates submission authority
7. AP creates/reuses target PolicyRule and creates one Pending RuleChange
8. source/destination authorized actors record decisions
9. second applicable approval activates the RuleChange and sets effectiveRevisionRef atomically
```

No asynchronous broker/saga is required. External peer reads happen before the AP aggregate transaction; exact decision basis/provenance is stored with the RuleChange.

## Web coexistence

Current legacy policy/application screens remain available as as-built behavior until deliberately migrated.

Target UI routes/features must use target APIs and display target concepts explicitly:

```text
Business Process / Connectivity Need
Component Deployment
Policy Rule / Rule Change
Vendor-Neutral Policy Export
```

They must not display legacy compatibility ComponentDeployment IDs as target deployment identities.

The exact navigation merge with existing Applications/Policy screens is S4/UI engineering as long as semantic concepts are not conflated.

## Migration/cutover rules

A later migration from legacy records to target records requires a separate accepted plan when exact mapping can be proven.

For every migrated object the migration must establish, without guessing:

- target ComponentDeployment identity for each endpoint;
- one Resource per target deployment;
- target ACC Interaction/immutable revision identity;
- target Business Connectivity Need/business basis where required;
- target PolicyRule sameness and current effective revision;
- explainable historical provenance.

If any required mapping is one-to-many, many-to-one, absent or ambiguous, automatic migration is not lossless and the affected record remains legacy until user-assisted/explicit migration behavior is accepted.

## Architecture invariants

- target BC/AD/AP identities are never aliases for legacy Requirement/ACC compatibility IDs merely because field shapes look similar;
- target AP and legacy AccessRule may coexist physically, but only one model owns each record's semantics;
- no target mutation dual-writes legacy semantic state;
- peer owner data crosses through application contracts/ports, never direct table joins in mutation logic;
- policy export target path reads target effective PolicyRules only; legacy normalized-policy reads legacy AccessRules only;
- as-built reconstruction docs remain valid until the corresponding compatibility runtime is actually removed.
