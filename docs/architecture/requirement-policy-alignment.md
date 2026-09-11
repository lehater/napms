# Requirement-to-Policy Alignment architecture — I14

Status: `accepted I14 WP3 architecture contract`.

Date: 2026-09-09.

## Disposition

Requirement-to-Policy Alignment is an **application composition**, not a new Bounded Context and not a persisted aggregate.

Target layout:

```text
backend/src/napms/requirement_policy_alignment/
    application/
        model.py
        ports.py
        align.py

backend/src/napms/connectivity_requirements/adapters/
    requirement_policy_alignment.py

backend/src/napms/access_policy/adapters/
    requirement_policy_alignment.py
```

There is no `domain/` package and no PostgreSQL schema for Alignment.

## Dependency direction

```text
Requirement-to-Policy Alignment Application
        ^
        |
consumer-owned ports
        ^
        |
CR adapter        AP adapter
   |                 |
   v                 v
Connectivity      Access
Requirements      Policy
```

Alignment application imports neither CR nor AP domain/application types.

CR and AP do not import each other.

## Local alignment model

### AlignmentSemanticIdentity

Local structural value:
- Source Component Deployment ID;
- Destination Component Deployment ID;
- DCS Contract Revision ID.

It is a translation shape only. Semantic ownership remains ACC/CR/AP as already accepted.

### RequirementAlignmentSnapshot

Contains only facts needed to answer currentness/coverage:
- Requirement ID;
- exact semantic identity;
- lifecycle `Active | Retired`;
- applicability `Ongoing | AbsoluteWindow`;
- Requirement Governance Scope only if needed for explanation, not matching.

It contains no mutation capability or owner shortcut.

### AlignmentStatus

```text
Covered
Uncovered
NotCurrent
Unknown
```

No `Denied` in I14.

## Requirement port

```text
AuthorizedRequirementAlignmentPort.get(
    requirementId,
    actorId,
    asOf
)
 -> Found(snapshot, readAuthorityReference)
  | NotFound
  | AuthorityDenied
  | AuthorityUnknown
  | Unavailable
```

Implementation:
- adapter delegates to existing Connectivity Requirements authorized detail semantics;
- Requirement read authority is therefore the admission gate for derived alignment status;
- no alignment result is returned when Requirement read is denied/unknown;
- mutation admissions are irrelevant and are not propagated.

## Access Policy coverage port

```text
EffectivePolicyCoveragePort.check_exact(
    semanticIdentity,
    asOf
)
 -> Covered
  | Uncovered
  | Unknown
```

Meaning:
- exact Rule semantic identity only;
- `Covered` iff the authoritative matching Rule exists and `contributes_effect_at(asOf)`;
- `Uncovered` iff authoritative AP truth is successfully established and no exact matching Rule contributes effect;
- `Unknown` on persistence/unavailable/corrupt authoritative result.

This port is **not** an Access Policy browsing/read endpoint.

Accepted I14 authority rule:
- Requirement read authority admits the derived status;
- this internal coverage check may inspect AP authoritative truth only to derive the minimal status;
- it exposes no Rule ID, Rule scope, decision/proposal provenance, Rule properties or audit.

Therefore differing Requirement/Rule governance scopes do not affect exact semantic matching.

## Optional Rule evidence

Not required for the first I14 slice.

If later added:
- use a separate optional port;
- require independent Access Policy read admission;
- failure/denial of evidence enrichment must not change an already established `Covered|Uncovered` status;
- never leak Rule identity through errors.

## Alignment use case

`AlignConnectivityRequirementToPolicy(requirementId, actorId, asOf)`

Order:
1. validate offset-aware `asOf`;
2. obtain authorized Requirement snapshot;
3. denied/unknown/not-found/unavailable maps safely without AP inspection where possible;
4. evaluate Requirement currentness at the same `asOf`;
5. if not current -> `NotCurrent` and do not require AP coverage;
6. if current -> call exact AP coverage port;
7. map coverage to `Covered | Uncovered | Unknown`;
8. return Requirement ID, semantic identity, `asOf`, status and non-sensitive explanation facts.

No mutation occurs in either source context.

## Temporal semantics

One explicit logical `asOf` governs:
- Requirement applicability;
- Access Rule effective contribution.

No runtime clock is consulted inside the application use case.

## Failure semantics

- Requirement not found -> explicit not-found outcome;
- Requirement read denied -> no Requirement/alignment data;
- Requirement read unknown -> no Requirement/alignment data;
- Requirement persistence unavailable -> unavailable;
- AP persistence unavailable/corrupt result -> Alignment `Unknown`;
- no matching/effective Rule after successful AP lookup -> `Uncovered`.

## HTTP/Web implication

I14 may add:
- one Requirement detail alignment endpoint, or enrich existing Requirement detail with an explicit-`asOf` alignment query;
- Web status in My Connectivity Needs.

The backend, not the browser, derives status.

No API exposes an unauthenticated/global "does this Rule exist?" oracle.

## Architecture guards

- no CR -> AP import;
- no AP -> CR import;
- Alignment application imports no CR/AP implementation/domain types;
- no Alignment PostgreSQL migration/repository;
- no Decision-domain import;
- no Technical Access Evidence/APR import;
- no hidden wall-clock;
- no `Denied` or orphan-policy semantics in I14.

## WP3 exit

Implementation gate opens when:
- WP1 semantic decision is accepted;
- WP2 acceptance examples are accepted;
- this application-composition boundary is accepted.
