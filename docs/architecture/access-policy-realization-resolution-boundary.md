# Access Policy Realization resolution boundary — I18

Status: `accepted I18 WP0 architecture contract`.

Date: 2026-09-09.

## Purpose

Define the first module/dependency boundary for Technical-to-Domain Access Resolution while preserving RC/ACC/TAE ownership and keeping I19/I20 semantics out of I18.

## Target module

```text
src/napms/access_policy_realization/
    domain/
        model.py
        algebra.py
    application/
        ports.py
        resolve.py
    adapters/
        catalogues.py
        technical_access_evidence.py
```

No APR persistence package/schema is required in I18.

## Dependency direction

```text
APR Domain
    ^
    |
APR Application + APR-owned ports
    ^
    |
outer APR adapters / composition
    |
    +--> TAE read/domain projection
    +--> Application Catalogue application/repository boundary
    +--> Resource Catalogue application/repository boundary
```

Rules:
- APR Domain imports no peer bounded context, framework, DB, transport or configuration type;
- APR Application imports only APR Domain + APR-owned protocols;
- outer adapters may depend on peer application/domain contracts necessary to translate authoritative facts;
- TAE/RC/ACC never import APR to make the consumer work;
- no peer-owned SQL/table is read directly by APR.

## APR application input

`ResolveTechnicalAccess` receives:
- APR-owned Technical Access Predicate;
- explicit offset-aware `asOf`;
- opaque input provenance.

It obtains an APR-owned `DomainKnowledgeSnapshot` from its consuming port and passes source-neutral candidate regions to Domain algebra.

## Domain knowledge port

Minimum shape:

```text
load_for(predicate, asOf)
    -> DomainKnowledgeSnapshot
         candidates[]
         knowledgeGaps[]
         completeForPredicate
```

Each candidate region contains:
- Domain Interaction identity;
- exact source/destination technical address constraints;
- exact IP protocol number;
- source/destination port constraints;
- ACC provenance references;
- source/destination RC provenance references.

The port is predicate-aware so unrelated unsupported catalogue facts need not poison a result.

## Catalogue adapter

The first concrete adapter may compose current RC + ACC repositories/application semantics.

High-level sequence:

```text
ACC DCS revisions
  -> effective source/destination bindings at asOf
  -> RC effective realizations for bound Resources
  -> prove address disjointness where possible
  -> for address-relevant candidates decode/translate DCS transport
  -> APR-owned Domain Interaction candidate regions
```

Semantics:
- no effective binding: no effective technical realization candidate;
- effective binding + unresolved Resource realization: explicit predicate-relevant gap unless known facts prove disjointness;
- invalid/non-unique binding state: explicit gap;
- unsupported transport is a gap only after address relevance cannot be excluded;
- candidate iteration order has no semantic effect.

The initial concrete transport translator may support only protocol tokens whose exact IP protocol number mapping is explicitly implemented. Unsupported tokens fail closed; no string equality between TAE numbers and ACC tokens exists in APR Domain.

## TAE adapter

The TAE adapter maps one existing Technical Access Entry plus source-qualified evidence references into APR input values.

It may preserve:
- Evidence Set ID;
- Evidence Entry ID;
- source/capture reference;
- evidence action as provenance metadata.

It does not:
- choose latest/current evidence;
- convert RecordedAt into asOf;
- write Domain Access Resolution back into TAE;
- infer authorization.

## Algebra boundary

Domain algebra is pure and deterministic.

For the first slice:
- exact IP protocol number is required for complete resolution;
- address/port ranges are canonicalized;
- intersection/containment/difference are exact;
- NotApplicable is distinct from numeric ports;
- Protocol Any returns Unknown without guessed expansion.

The domain result carries exact overlap/remainder witnesses and ambiguity facts.

## Runtime/persistence boundary

I18 requires no:
- PostgreSQL migration/table;
- APR repository/UoW;
- HTTP route;
- Web page;
- Authority Management action;
- background job.

A later consumer may expose resolution through its own accepted workflow.

## Cross-context limits

I18 does not consume Access Policy or NEP to determine correspondence.

```text
TAE + RC + ACC
    -> APR Technical-to-Domain Resolution

AP + NEP + TAE
    -> later APR realization/reconciliation stages
```

This keeps the first capability usable by both proposal and reconciliation consumers without preselecting a later workflow.

## Failure semantics

- invalid APR input invariant -> explicit domain/application error;
- upstream predicate-relevant uncertainty -> successful `Unknown` Domain Access Resolution with knowledge-gap evidence;
- adapter corruption/contract violation that cannot be represented truthfully -> fail closed, never partial success reported as complete;
- no-match with complete knowledge -> `Unresolved`, not `Unknown`.

## Validation

Required executable proof:
- APR Domain/Application architecture import boundary;
- correspondence/remainder algebra examples;
- ambiguity winner prohibition;
- predicate-relevant Unknown behavior;
- TAE adapter direction;
- RC/ACC integration without cross-context SQL;
- no Access Policy/Decision mutation side effect.
