# Catalogue curation M7 pilot — S1 inventory

Status: CANDIDATE / non-canonical / S1 classification complete for selected sources.

## Capsule result

Scope: `catalogue-curation-pilot`  
Stage: `S1`  
Task: classify the three selected accepted catalogue-curation requirement sources into v2 S1 artifact records without changing canonical `docs/`.

Direct context used:

- `docs-v2/spec/lifecycle.md`
- `docs-v2/spec/artifacts.md`
- `docs-v2/spec/agent-execution.md`
- `docs/requirements/catalogue-curation.md`
- `docs/requirements/catalogue-curation-acceptance-examples.md`
- `docs/requirements/catalogue-curation-security.md`

Context expansions: none.

## Classification rule

S1 records observable product behavior, measurable quality requirements and acceptance intent. Existing prose that states product problem/evidence, S2 domain ownership/aggregate decisions, S3 HTTP/UI realization choices, S4 implementation readiness, or externally imposed/non-negotiable S0 constraints is not copied into S1 merely because it currently lives in `docs/requirements/**`.

The selected sources contain mixed-stage material. This inventory splits by semantic owner rather than preserving legacy file boundaries.

## Candidate functional-requirement records

Stable pilot IDs below are candidate semantic IDs for traceability during the pilot; they do not replace current canonical identifiers before cutover.

| Candidate ID | Observable behavior | Source | Disposition |
|---|---|---|---|
| `REQ-CAT-RC-001` | An admitted user can create/register an access-relevant Resource identity with required provenance and inspect its details. | `catalogue-curation.md` Resource curation workflow | SPLIT |
| `REQ-CAT-RC-002` | An admitted user can add, end and replace time-qualified Resource endpoint/realization facts while historical facts remain distinguishable. | `catalogue-curation.md` Resource curation/history | SPLIT |
| `REQ-CAT-RC-003` | An admitted user can add, end and replace Resource Scope Affiliations without changing Resource identity. | `catalogue-curation.md` Resource curation workflow | SPLIT |
| `REQ-CAT-RC-004` | An admitted user can maintain Resource Responsibility/contact assignments for supported references and roles. | `catalogue-curation.md` Resource curation workflow | SPLIT |
| `REQ-CAT-RC-005` | The Resources workspace provides server-backed paging, supported search/filtering, scope-focused filtering, explicit missing-fact indication and navigation to admitted mutations. | `catalogue-curation.md` Resource list | SPLIT |
| `REQ-CAT-RC-006` | Missing effective affiliation or realization does not hide or fabricate a Resource; missing relations are represented explicitly. | `catalogue-curation.md` Resource list | SPLIT |
| `REQ-CAT-ACC-001` | An admitted user can create and maintain Application, Component and Component Deployment catalogue structure through supported workflows. | `catalogue-curation.md` Application catalogue curation | SPLIT |
| `REQ-CAT-ACC-002` | A user can bind/unbind or effectively replace Component Deployment to Resource bindings using backend-discovered Resource identities. | `catalogue-curation.md` Applications workspace / Deployment Resource Binding | SPLIT |
| `REQ-CAT-DCS-001` | A user can author a new immutable directed communication specification revision through supported semantic fields rather than raw internal identifiers or encoded payloads. | `catalogue-curation.md` Applications workspace / DCS authoring | SPLIT |
| `REQ-CAT-DCS-002` | Editing an immutable DCS revision creates a new revision/identity rather than rewriting a revision already referenced by downstream truth. | `catalogue-curation.md` DCS authoring | SPLIT |
| `REQ-CAT-AUTH-001` | Every catalogue mutation is admitted by Authority Management using authenticated actor identity and the owning use case's server-selected catalogue action/scope. | `catalogue-curation-security.md` Observable behavior | SPLIT |
| `REQ-CAT-AUTH-002` | Client-supplied actor, catalogue authority scope or action time is not trusted for mutation authorization. | `catalogue-curation-security.md` Observable behavior | SPLIT |
| `REQ-CAT-AUTH-003` | Resource affiliation, responsibility/contact role, catalogue/read visibility and unrelated policy actions do not by themselves grant catalogue curation authority. | `catalogue-curation-security.md` Separation of concerns | SPLIT |
| `REQ-CAT-AUTH-004` | Catalogue curation authority does not grant protected Connectivity/Checker/proposal/decision/Access Rule actions. | `catalogue-curation-security.md` Separation of concerns | SPLIT |
| `REQ-CAT-AUTH-005` | Direct HTTP mutation is rejected when authority is absent even if presentation state hides or disables the action. | `catalogue-curation-security.md` Read workspace | SPLIT |
| `REQ-CAT-AUTH-006` | Authorization denial is distinguishable from domain/structural validation, optimistic concurrency, idempotency and persistence/transport failures without leaking protected authority/provenance detail. | `catalogue-curation-security.md` Error behavior | SPLIT |
| `REQ-CAT-VAL-001` | Catalogue mutations reject invalid required references/provenance, invalid temporal intervals, prohibited overlaps, missing binding targets and invalid DCS semantics explicitly. | `catalogue-curation.md` Validation and consistency | SPLIT |
| `REQ-CAT-UX-001` | Supported authoring uses backend discovery for cross-context references rather than requiring arbitrary internal stable-ID combinations. | `catalogue-curation.md` Deployment binding / HTTP boundary / Mutation UX | MERGE |
| `REQ-CAT-UX-002` | Mutation workflows distinguish version/relation-ending operations from scalar edits, prevent accidental duplicate submission, surface relevant validation errors and distinguish authorization/domain/transport failures. | `catalogue-curation.md` Mutation UX | MERGE |

## Candidate quality-requirement records

Only claims that express a cross-cutting quality expectation rather than a concrete product action are classified here.

| Candidate ID | Quality expectation | Source | Disposition |
|---|---|---|---|
| `QREQ-CAT-001` | Catalogue mutation authorization fails closed when the required Authority Management assignment is absent or ambiguous under accepted authority semantics. | `catalogue-curation-security.md` Scope integrity | SPLIT |
| `QREQ-CAT-002` | Mutation processing must not silently overwrite a concurrent accepted change; stale submissions produce an explicit conflict. | acceptance Example J plus `catalogue-curation.md` validation/error intent | MERGE |
| `QREQ-CAT-003` | Historical identities/facts referenced by downstream business truth are preserved rather than silently rewritten or hard-deleted by ordinary curation. | `catalogue-curation.md` history/non-goals plus acceptance examples | MERGE |

Idempotency is not promoted to a standalone quality requirement yet: the canonical requirement explicitly leaves behavior conditional on a natural command identity/idempotency contract, so the exact rule remains dependent on later owner decisions.

## Candidate acceptance-scenario records

| Candidate ID | Scenario intent | Source example | Disposition |
|---|---|---|---|
| `ACC-CAT-001` | Authorized curator onboards an Application/Component/Deployment and a Resource with endpoint/scope affiliation, then binds deployment to Resource without authoring internal IDs. | A | TRANSFORM |
| `ACC-CAT-002` | Curator defines supported directed communication semantics and backend persists a validated immutable DCS revision. | B | TRANSFORM |
| `ACC-CAT-003` | Rename changes display metadata without changing stable deployment identity or downstream semantic references. | C | MOVE |
| `ACC-CAT-004` | Moving a deployment to another Component uses replacement structural identity rather than hidden parent reassignment. | D | MOVE |
| `ACC-CAT-005` | Retirement proceeds leaves-upward and preserves historical references. | E | MOVE |
| `ACC-CAT-006` | Changing a Resource address creates/replaces temporal realization while preserving Resource identity and historical resolution. | F | MOVE |
| `ACC-CAT-007` | Operational responsibility alone does not grant mutation or policy authority. | G | MOVE |
| `ACC-CAT-008` | Resource retirement prevents new active selection while preserving readable historical bindings/realizations/policy references under existing read authorization. | I | MOVE |
| `ACC-CAT-009` | Concurrent stale mutation receives explicit conflict instead of silently overwriting the accepted change. | J | MOVE |

Example H is excluded from this first Resource Catalogue curation happy-path pilot because it specifies compatibility migration of legacy Application/Component structure rather than the selected fresh-catalogue workflow.

## Material routed out of S1

The classification found mixed-stage content that must not become duplicate S1 truth:

- product-problem narrative about seed-only catalogue maintenance -> S0 problem/evidence candidate if/when B1 migrates that upstream truth;
- statements assigning Resource Catalogue, Application Communication Catalogue and Authority Management semantic ownership -> S2 domain truth/reference;
- exact aggregate boundaries, lifecycle identities and tactical decisions -> S2;
- conceptual HTTP route families, transport DTO ownership and task-oriented boundary shape -> S3;
- dense-list/detail presentation structure and other realization-specific UI design -> S3/UI owner once the target UI artifact policy is resolved;
- blocking implementation decisions and implementation-closure statements -> S2/S3/S4 owners as applicable;
- local PostgreSQL/session/demo realization statements -> architecture/deployment or test/demo evidence, not S1 unless a separately accepted product constraint establishes them as externally imposed/non-negotiable S0 truth.

No claim in the three selected sources was promoted to a new S0 `constraint` solely from its wording. The pilot does not infer an externally imposed/non-negotiable constraint from downstream solution choices.

## G1 candidate check

For the selected Resource Catalogue curation slice:

- observable functional behavior: present;
- applicable quality expectations: present;
- acceptance intent: present;
- solution/domain leakage: identified and routed out rather than copied;
- bounded-context grouping: not used as S1 ownership; candidate IDs are grouped by observable capability only;
- upstream constraint redefinition: none;
- missing information that would require inference from code/domain/architecture: none for this classification task.

Result: `PASS` for the S1 classification task itself. This is pilot evidence, not a canonical G1 decision for product truth and not implementation authorization.

## Handoff

Next task only: classify the selected Resource Catalogue S2 sources (`tactical-model.md` and the S2 portions of `target-realization-model.md`) against `domain-model`, `domain-glossary` and requirement-domain traceability. Do not execute S3 or implementation work in that capsule.