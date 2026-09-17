# Catalogue curation M7 pilot — S3 inventory

Status: CANDIDATE / non-canonical / S3 classification complete for selected Resource Catalogue boundary and HTTP surface.

## Capsule result

Scope: `catalogue-curation-pilot`  
Stage: `S3`  
Task: classify the selected Resource Catalogue architecture boundary and HTTP contract into v2 S3 artifacts without broadening into Application Communication Catalogue or implementation.

Direct context used:

- `docs-v2/spec/lifecycle.md`
- `docs-v2/spec/artifacts.md`
- `docs-v2/spec/agent-execution.md`
- `docs-v2/pilot/catalogue-curation/s1-inventory.md`
- `docs-v2/pilot/catalogue-curation/s2-inventory.md`
- `docs/architecture/catalogue-curation-boundary.md`
- `docs/engineering/catalogue-curation-http-api-contract.md`

Context expansions: none.

## Classification rule

S3 owns architecture and externally consumable contracts needed to realize accepted S1 behavior using accepted S2 semantics. The pilot keeps the Resource Catalogue portion only. ACC endpoints and ACC transaction behavior remain referenced as excluded neighboring evidence, not copied into this slice.

The legacy architecture document mixes container/dependency boundaries, interaction flows, transaction decisions, security mechanics, migration notes and implementation consequences. The legacy HTTP document is a prose transport contract. The candidate split is therefore:

- `container-view` for structural/dependency boundary;
- `interaction-flow` for RC read/write flows;
- `http-contract` for the selected RC public HTTP surface;
- S4/migration/implementation statements routed downstream rather than retained in S3.

## Candidate container-view

```text
Web / HTTP adapter
    -> Resource Catalogue application use cases
        -> Resource Catalogue domain
        -> Authority admission port -> Authority Management adapter
        -> Resource Catalogue repository port -> PostgreSQL adapter
        -> owner-preserving read projection/composition
```

Architecture constraints for this slice:

1. Web/HTTP is an outer adapter and owns no Resource Catalogue semantic truth.
2. Resource Catalogue application/domain code owns RC mutation orchestration and invariants.
3. Authority checks are consumed through an application-owned port; RC domain does not depend on Authority Management implementation or HTTP concepts.
4. RC persistence is behind an RC-owned repository port; a Resource mutation transacts inside the RC persistence boundary.
5. Cross-context read composition may enrich presentation but cannot move semantic ownership into Web/query composition.
6. Clients do not choose trusted actor identity, catalogue authority scope or authoritative provenance.
7. No distributed ACC+RC transaction is introduced by this selected RC slice.

## Candidate interaction flows

### Resource mutation

```text
Web form
  -> authenticated RC HTTP command
  -> RC application use case
  -> server selects CurateResourceCatalogue @ resource-catalogue
  -> Authority Management admission port
  -> RC domain invariants
  -> RC repository transaction
  -> command result / owner read projection
```

Failure before admission/invariant validation produces no RC mutation. UI visibility is not authorization; direct HTTP mutation performs the same server-side admission.

### Resource workspace read

```text
Resources workspace
  -> RC workspace/read application path
  -> Resource identity + current temporal RC facts at one asOf
  -> optional owner-preserving presentation composition
  -> HTTP projection
```

`responsibilityScope` is a business-data filter over effective Resource Scope Affiliation. It is not substituted for the fixed Resource Catalogue authorization scope.

### Address replacement

```text
client selects current realization + expected version
  -> replacement command
  -> admission
  -> validate current fact/version/time
  -> end selected ResourceAddressFact
  -> create successor ResourceAddressFact
  -> commit atomically inside RC
  -> return updated projection
```

This flow realizes S2 replace semantics while keeping transaction/version representation downstream from the domain model.

## Candidate HTTP contract — Resource Catalogue subset

Canonical target form for this artifact type should be OpenAPI. This pilot inventory records the semantic operations to migrate; it does not manufacture a full OpenAPI document from prose without first checking the repository's native executable/API schema source during the later contract migration step.

### Trust and common mutation rules

For RC mutations the server owns authenticated actor identity, runtime action time, `CurateResourceCatalogue @ resource-catalogue`, generated RC identities/provenance and persisted idempotency outcome. Requests must not supply trusted actor, authority scope or provenance.

Every selected mutation requires a non-empty `Idempotency-Key`. Equivalent retry resolves the authoritative prior result; incompatible reuse maps to `409 CatalogueIdempotencyConflict`.

Versioned mutations use `expectedVersion`; stale writes map to `409 CatalogueConcurrencyConflict`.

Temporal values are offset-aware RFC 3339 and use `[validFrom, validTo)` semantics.

### Reads

| Operation | Contract intent |
|---|---|
| `GET /api/v1/catalogues/resources` | Lightweight authenticated Resource discovery for cross-entity forms; deliberately does not expose workspace diagnostics. |
| `GET /api/v1/catalogues/resource-workspace` | Paged/searchable RC workspace projection with optional `responsibilityScope`, `asOf`, `includeRetired` and current-fact diagnostics. |
| `GET /api/v1/catalogues/resources/{resourceReference}` | Resource detail plus current/effective RC-owned realization, scope-affiliation and responsibility facts at one logical `asOf`. |

### Mutations

| Operation | Contract intent |
|---|---|
| `POST /api/v1/catalogues/resources` | Create stable Resource identity; identity/provenance generated by NAPMS. |
| `POST /api/v1/catalogues/resources/{resourceReference}/realizations` | Establish first/non-overlapping authoritative Resource realization from technical address/validity input. |
| `POST /api/v1/catalogues/resource-realizations/{factReference}/replacement` | Atomically end selected current realization and create successor, preserving history/provenance and checking expected version. |
| `POST /api/v1/catalogues/resources/{resourceReference}/scope-affiliations` | Create temporal Resource Scope Affiliation; Responsibility Scope is external business correlation, not authority scope. |
| `POST /api/v1/catalogues/resource-scope-affiliations/{affiliationReference}/end` | End selected affiliation using `validTo` + `expectedVersion`; no hard delete. |
| `POST /api/v1/catalogues/resources/{resourceReference}/responsibilities` | Create temporal Resource Responsibility for accepted party kind/role; assignment grants no authority. |
| `POST /api/v1/catalogues/resource-responsibilities/{assignmentReference}/end` | End selected responsibility while preserving creation and end provenance separately. |

### Stable public error semantics for selected RC surface

| Condition | HTTP | Public code/shape |
|---|---:|---|
| unauthenticated | 401 | `AuthenticationRequired` |
| mutation denied | 403 | `CatalogueAuthorityDenied` |
| authority ambiguous/unknown | 409 | `CatalogueAuthorityUnknown` |
| subject not found | 404 | `CatalogueSubjectNotFound` |
| inactive Resource | 409 | `CatalogueResourceInactive` |
| invalid input/domain invariant | 422 | `CatalogueInputInvalid` / `CatalogueValidationError` |
| invalid temporal input | 422 | catalogue time/interval validation code |
| temporal overlap | 409 | `CatalogueOverlapConflict` |
| stale expected version | 409 | `CatalogueConcurrencyConflict` |
| incompatible idempotency-key reuse | 409 | `CatalogueIdempotencyConflict` |
| known persistence execution failure | 503 | catalogue unavailable code |
| ambiguous commit acknowledgement | 503 | `CataloguePersistenceOutcomeUnknown` |

The shared public error envelope/session/correlation conventions remain referenced from the shared HTTP contract; the pilot does not duplicate them into the RC-specific candidate.

## Traceability to accepted pilot inputs

| Upstream candidate | S3 realization |
|---|---|
| `REQ-CAT-RC-001` | create/detail Resource operations plus RC application/domain boundary |
| `REQ-CAT-RC-002` | realization create/replacement operations and atomic replacement flow |
| `REQ-CAT-RC-003` | scope-affiliation create/end operations |
| `REQ-CAT-RC-004` | responsibility create/end operations |
| `REQ-CAT-RC-005` | resource-workspace paging/search/scope filter and diagnostics projection |
| `REQ-CAT-RC-006` | detail/workspace projection preserves explicit missing current facts |
| `REQ-CAT-AUTH-001` | server-selected RC authority policy and admission port in mutation flow |
| `REQ-CAT-AUTH-002` | HTTP trust boundary forbids caller-owned actor/scope/provenance |
| `REQ-CAT-AUTH-003` | scope-affiliation/responsibility remain business data, never authority substitution |
| `REQ-CAT-AUTH-005` | every HTTP mutation re-checks authority server-side |
| `REQ-CAT-AUTH-006` | distinct public authorization/domain/concurrency/idempotency/persistence outcomes |
| `REQ-CAT-VAL-001` | HTTP/application boundary maps RC validation and overlap failures explicitly |
| `QREQ-CAT-001` | admission failure/ambiguity fails closed before mutation |
| `QREQ-CAT-002` | `expectedVersion` + explicit concurrency conflict |
| `QREQ-CAT-003` | create/end/replace operations avoid destructive history rewrite |
| `ACC-CAT-006` | replacement endpoint/flow preserves Resource identity and realization history |
| `ACC-CAT-007` | fixed authority policy remains independent of Resource Responsibility |
| `ACC-CAT-009` | stale expected version maps to explicit conflict |

S2 `Resource`, `ResourceAddressFact`, `ResourceScopeAffiliation`, `ResourceResponsibility` and `CurrentResourceRealization` remain domain-owned; the HTTP DTO/projection does not become their semantic owner.

## Routed out / excluded

- all `/applications`, `/components`, `/deployments`, DCS and deployment-resource-binding operations -> ACC neighboring slice, not this RC pilot capsule;
- schema migration/backfill mechanics -> S4 migration plan / Implementation;
- statements that implementation may proceed -> S4/G4 only, not an S3 authorization;
- PostgreSQL table/ORM details -> persistence-model/Implementation only when applicable;
- concrete Web layout/widgets -> UI architecture/design owner, not inferred here;
- exact OpenAPI schemas not present in these two prose inputs -> do not invent; verify native schema/executable source before canonical contract migration.

## G3 candidate check

For the selected Resource Catalogue curation slice:

- structural boundary and dependency direction: explicit;
- mutation/read interaction flows: explicit;
- authority/trust/transaction boundaries: explicit;
- RC public HTTP operations and error semantics: identified;
- upstream S1/S2 traceability: explicit;
- ACC neighboring surface: excluded rather than silently broadened;
- implementation/migration authorization leakage: routed downstream;
- duplicate shared HTTP convention truth: avoided by reference;
- missing exact OpenAPI schema: recorded as a contract-migration task, not filled by inference.

Result: `PASS` for S3 classification/inventory. It is pilot evidence only and is not canonical G3 or implementation authorization.

## Handoff

Next task only: perform S4 readiness classification for this documentation-migration pilot itself: identify the concrete candidate artifacts/files to materialize, validation intent, migration ledger entries and blockers. Do not implement product changes and do not treat the existing product implementation as authorization.