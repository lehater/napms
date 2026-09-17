# Catalogue curation M7 pilot — S2 inventory

Status: CANDIDATE / non-canonical / S2 classification complete for selected Resource Catalogue sources.

## Capsule result

Scope: `catalogue-curation-pilot`  
Stage: `S2`  
Task: classify the selected Resource Catalogue domain sources into v2 S2 artifacts and trace the S1 pilot requirements they realize, without changing canonical `docs/`.

Direct context used:

- `docs-v2/spec/lifecycle.md`
- `docs-v2/spec/artifacts.md`
- `docs-v2/spec/agent-execution.md`
- `docs-v2/pilot/catalogue-curation/s1-inventory.md`
- `docs/domain/resource-catalogue/tactical-model.md`
- `docs/domain/resource-catalogue/target-realization-model.md`

Context expansions: none.

## Classification rule

S2 owns domain semantics: stable identities, value objects, domain facts, invariants, state/lifecycle semantics, published semantic projections and bounded-context relationships. Persistence/versioning mechanics, HTTP contracts and implementation details remain downstream. Observable behavior remains S1-owned and is referenced through traceability rather than redefined.

The two legacy domain documents overlap substantially. The pilot therefore MERGEs their current semantic truth into one candidate `domain-model` record instead of preserving both documents as co-owners. Narrative terminology needed to interpret the model becomes `domain-glossary`; requirement relationships become `requirement-domain-trace`.

## Candidate domain-model record

Candidate artifact: `domain-model`  
Owning stage: `S2`  
Bounded context: `Resource Catalogue`

### Identities and value objects

```text
Resource
    ResourceId
    displayName?
    lifecycle: Active | Retired

AddressSpace = HostAddress | Prefix

ResourceAddressFact
    ResourceAddressFactId
    ResourceRef
    AddressSpace
    [validFrom, validUntil)
    provenanceReference
    endProvenanceReference?

ResourceScopeAffiliation
    AffiliationId
    ResourceRef
    ResponsibilityScopeRef
    [validFrom, validUntil)
    provenanceReference
    endProvenanceReference?

ResourceResponsibility
    ResourceRef
    ResponsiblePartyRef
    partyKind: Person | Team
    role: ServiceOwner | TechnicalOwner | OperationsContact | BusinessOwner
    displayName
    contactPoint?
    [validFrom, validUntil)
    provenanceReference
    endProvenanceReference?
```

### Published semantic projection

```text
CurrentResourceRealization(ResourceRef, logicalTime)
    resourceRef
    addressSpace? : HostAddress | Prefix
    asOf
    resolution/completeness
    provenance/freshness reference
```

`CurrentResourceRealization` is derived from RC-owned truth and is not a second owner of Resource identity or address history.

### Current invariants

1. `ResourceId` is stable across rename, address realization, deployment reference, scope affiliation and responsibility changes.
2. Resource lifecycle for the current scope is `Active -> Retired`; retirement preserves historical identity and facts.
3. At one logical time a Resource has at most one effective `ResourceAddressFact` / `AddressSpace`.
4. A resolved `AddressSpace` is exactly one `HostAddress` or one `Prefix`; a Prefix is not expanded into host identities.
5. Absence of effective AddressSpace is valid unresolved realization and is not equivalent to an empty access requirement.
6. Address history remains explainable through temporal validity and provenance; replacing an address ends the previous effective fact and establishes another fact for the same Resource.
7. For the same Resource + Responsibility Scope + logical time, at most one equivalent Resource Scope Affiliation is effective.
8. Resource Scope Affiliation, Resource Responsibility and actor authorization are separate meanings.
9. Cross-context consumers use opaque `ResourceRef` plus published RC projections, not RC-private fact identities.
10. AddressSpace change alone does not change `ComponentDeployment` or downstream policy semantic identity.
11. Address-to-Resource correlation may resolve to zero/one/many Resources; ambiguous or missing correlation remains unresolved and does not create policy truth.

### Domain operations retained at semantic level

```text
CreateResource
SetResourceAddressSpace
ReplaceResourceAddressSpace
```

These names express domain meaning only. Exact command/API names, transaction boundaries, optimistic-lock fields, database representation and migration mechanics are downstream concerns.

### Explicitly deferred semantics

Several simultaneous addresses/prefixes per Resource, endpoint/interface/VIP/listener identity, management/data-plane separation, deployment-specific exposure, NAT calculation, richer Resource lifecycle/restoration and explicit address clearing remain outside the current domain model until an accepted use case requires them.

## Candidate domain-glossary record

| Term | S2 meaning |
|---|---|
| Resource | Stable RC-owned identity of an access-relevant resource. |
| ResourceRef | Opaque cross-context reference to Resource identity; not a storage key or private realization identity. |
| AddressSpace | Value object containing exactly one HostAddress or Prefix when resolved. |
| ResourceAddressFact | Temporal authoritative fact that one Resource has one AddressSpace for a validity interval, with provenance. |
| CurrentResourceRealization | Derived published semantic projection resolving ResourceRef at a logical time to optional AddressSpace plus completeness/provenance information. |
| ResourceScopeAffiliation | Temporal RC fact associating a Resource with a Responsibility Scope; it does not grant actor authority. |
| ResourceResponsibility | Temporal RC fact describing responsible person/team and role/contact data; it neither establishes scope membership nor grants actor authority. |
| unresolved realization | Valid state in which no effective AddressSpace resolves for a Resource at the requested logical time. |

## Requirement-domain traceability

Traceability references the candidate S1 IDs; it does not transfer requirement ownership into the bounded context.

| S1 candidate | S2 realization/constraint | Trace status |
|---|---|---|
| `REQ-CAT-RC-001` | `Resource` / stable `ResourceId`; creation establishes identity. | DIRECT |
| `REQ-CAT-RC-002` | `ResourceAddressFact`, temporal validity/provenance, stable Resource identity, replace semantics. | DIRECT |
| `REQ-CAT-RC-003` | `ResourceScopeAffiliation` temporal fact and uniqueness invariant. | DIRECT |
| `REQ-CAT-RC-004` | `ResourceResponsibility` temporal fact with party kind/role/contact semantics. | DIRECT |
| `REQ-CAT-RC-006` | Optional `CurrentResourceRealization.addressSpace?`; absence is explicit unresolved state. | DIRECT |
| `REQ-CAT-ACC-002` | RC side owns only referenced `Resource` identity; deployment/binding semantics remain outside RC. | PARTIAL / CROSS-CONTEXT |
| `REQ-CAT-AUTH-003` | RC explicitly separates affiliation/responsibility from actor authority. | DIRECT BOUNDARY |
| `REQ-CAT-VAL-001` | RC covers temporal/address/affiliation invariants; binding and DCS validation belong to their owning contexts. | PARTIAL / CROSS-CONTEXT |
| `QREQ-CAT-003` | Stable Resource identity plus temporal fact/provenance history supports preservation of referenced history. | DIRECT FOR RC |
| `ACC-CAT-006` | Address replacement changes temporal realization, not Resource identity. | DIRECT |
| `ACC-CAT-007` | Responsibility semantics explicitly do not grant authority. | DIRECT BOUNDARY |
| `ACC-CAT-008` | `Active -> Retired` preserves Resource identity/facts; downstream readability remains subject to other owners. | PARTIAL / CROSS-CONTEXT |

S1 records for application hierarchy, DCS authoring, generic mutation authorization, UI behavior and concurrency are intentionally not forced into the Resource Catalogue model. They require Application Communication Catalogue, Authority Management or downstream architecture/application ownership.

## Mixed/downstream material routed out of S2

The source documents contain downstream statements that are useful evidence but are not S2 canonical domain truth:

- exact persistence/versioning mechanism, ORM/schema and migration mechanics -> S3/S4/Implementation as applicable;
- exact command/API names and transport contracts -> S3;
- optimistic-lock/ETag fields and transaction shape -> S3/S4;
- policy materialization orchestration details beyond RC's published projection -> consuming bounded context/architecture;
- implementation statement that `tactical-model.md` "implements" another document -> replaced here by a single semantic candidate owner plus traceability.

No executable code or persistence model was loaded to define missing domain semantics.

## G2 candidate check

For the selected Resource Catalogue portion of catalogue curation:

- stable domain identity: explicit;
- current value objects/facts/projections: explicit;
- invariants and temporal semantics: explicit;
- bounded-context ownership boundaries: explicit;
- requirement-to-domain traceability: explicit without moving requirements into S2;
- duplicate semantic ownership between the two legacy domain documents: removed in the candidate classification through MERGE;
- downstream implementation/persistence leakage: identified and routed out;
- unresolved semantic ambiguity blocking this selected RC slice: none.

Result: `PASS` for this S2 classification task. This is pilot evidence only; it does not replace canonical `docs/`, grant canonical G2 for unrelated catalogue contexts, or authorize implementation.

## Handoff

Next task only: classify the selected Resource Catalogue architecture boundary and HTTP contract into S3 candidate artifacts, using this S2 candidate model as accepted pilot input. The S3 capsule must not broaden into Application Communication Catalogue or implementation work.