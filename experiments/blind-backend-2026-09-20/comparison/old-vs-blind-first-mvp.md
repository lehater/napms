# Post-freeze comparison — old canonical NAPMS vs blind reconstruction

Status: COMPLETE FOR FIRST-MVP BACKEND COMPARISON
Frozen blind snapshot: `ac6c2e1c17b50a62abd3320c4e4cb6cbbaf129ba`
Old comparison baseline: `napms/main` after blind freeze
Rule: comparison findings MUST NOT mutate the frozen reconstruction.

## Classification legend

- NEW_BETTER_SUPPORTED — blind reconstruction is better supported by admitted/source-level evidence.
- OLD_BETTER_SUPPORTED — old design is better supported by source evidence.
- VALID_DESIGN_FREEDOM — both are plausible realizations under available source input.
- HARNESS_MISSED_CONCERN — source/input or engineering concern was available but blind process failed to carry it into closure.
- OLD_UNJUSTIFIED_DECISION — old design introduced a material restriction/semantic decision not supported by source input.
- INPUT_CONTAMINATION — old derived design influenced the blind reconstruction before freeze.
- INSUFFICIENT_SOURCE_INPUT — neither design can be preferred because required source truth genuinely does not exist.

## Findings

### CMP-001 — cross-Application Interaction
Classification: NEW_BETTER_SUPPORTED / OLD_UNJUSTIFIED_DECISION
Priority: P1

Source Wave-1 acceptance explicitly says no blanket same-Application invariant: validity follows the described directed communication contract and valid Component references.

Old:
- Interaction is constrained to Components in one ApplicationDefinition;
- OpenAPI route is application-nested;
- test intent explicitly rejects cross-Application Interaction.

Blind:
- Components remain Application-owned;
- Interaction may reference source/destination Components from different Applications;
- validity follows explicit Component refs and communication semantics.

Conclusion: old restriction contradicts admitted original product source.

### CMP-002 — several independently meaningful Interactions for same Component pair
Classification: NEW_BETTER_SUPPORTED / OLD_UNJUSTIFIED_DECISION
Priority: P1

Stakeholder evidence says the same Component pair may have several distinct Interactions when communication reasons are independently meaningful.

Old:
- at most one Interaction per directed Component pair.

Blind:
- Interaction identity is independent from pair uniqueness;
- separately applicable/authorized traffic meaning stays separate.

Conclusion: blind reconstruction preserves source granularity; old uniqueness constraint loses independent meaning.

### CMP-003 — Access Rule existence before permission
Classification: NEW_BETTER_SUPPORTED / OLD_UNJUSTIFIED_DECISION
Priority: P1

Wave-1 source says a proposal is not an authoritative Rule before Allowed and NotAllowed creates no Rule.

Old:
- submit RuleChange creates/reuses PolicyRule and returns policyRuleId while state is Pending;
- Rejected RuleChange can therefore leave a PolicyRule identity that existed before permission.

Blind:
- AccessRequest exists independently;
- DENIED creates no PolicyRule;
- PolicyRule is created/resolved only on ALLOWED decision.

Conclusion: blind lifecycle matches source more directly.

### CMP-004 — current-access semantic identity and traffic revision
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Wave-1 source states semantic identity includes source deployment + destination deployment + immutable decision-relevant communication revision; identity-defining semantic change requires another decision/rule subject.

Old:
- one non-Retired PolicyRule per deployment pair;
- revision is mutable effective state of that Rule;
- Accepted later RuleChange advances effectiveRevisionRef.

Blind:
- AccessSubject includes source deployment + destination deployment + exact immutable InteractionRevision;
- identity-defining revision change creates another subject requiring another permission decision.

Conclusion: old model conflates a stable pair container with source-defined authoritative Rule identity.

### CMP-005 — repeated allowed materialization / multiple permission evidence
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Source requires repeated handling of the same allowed semantic access to converge on one authoritative current access.

Old:
- pair-level PolicyRule + RuleChange history partially converges, but its identity excludes revision and the model does not cleanly represent multiple independent allowed requests for one exact semantic subject as authorization evidence.

Blind:
- one PolicyRule per AccessSubject;
- repeated/separate ALLOWED requests converge on that Rule;
- AuthorizationEvidence is append-only and preserves every request/decision provenance item.

Conclusion: blind design closes the source behavior without changing semantic identity.

### CMP-006 — Active/Inactive operational state
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Wave-1 source explicitly requires Active <-> Inactive without a new permission decision.

Old:
- lifecycle is effectively Active/Retired plus withdrawal;
- no reversible Inactive state;
- withdrawal clears current effectiveness but is not the accepted reversible suspension semantic.

Blind:
- ACTIVE <-> INACTIVE is first-class and auditable without new permission.

Conclusion: old first-MVP design omitted accepted product behavior.

### CMP-007 — declarative effective condition
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Source requires supported declarative operational/effective conditions and acceptance examples include time-dependent effectiveness without toggling stored state.

Old:
- no effective-window/schedule semantics in Access Policy or export.

Blind:
- minimal non-speculative absolute [effectiveFrom,effectiveUntil) window;
- recurring DSL deferred with explicit reopening condition.

Conclusion: blind design satisfies the source with the smallest sufficient semantic commitment.

### CMP-008 — participant-attributed Connectivity Need
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Stakeholder source says Need is from a dependent participant/component perspective and source/destination participants can contribute independently.

Old:
- ConnectivityNeed references Interaction only;
- no participant attribution.

Blind:
- Need includes participantComponentRef constrained to one Interaction endpoint;
- source and destination Needs remain independently attributable.

Conclusion: blind design retains source-required business causality.

### CMP-009 — additional Need justification for already-authorized access
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Source says current authorized access may acquire additional Need justification without duplicate Rule.

Old:
- each RuleChange has one connectivity_need_ref;
- current PolicyRule has one effective revision/decision provenance and no explicit multi-Need association model.

Blind:
- Rule has append-only Need justification associations independent of authorization evidence;
- additional current Need does not duplicate Rule.

Conclusion: blind model is materially closer to source behavior.

### CMP-010 — no-current-Need reconciliation
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Source says loss of all current known Needs must remain distinguishable but must not automatically revoke access.

Old:
- historical RuleChange Need is retained, but current export/Rule contract has no explicit NO_CURRENT_BUSINESS_JUSTIFICATION condition.

Blind:
- currentness of associated Needs is resolved at materialization/read time;
- zero current Need is explicit reconciliation state and does not alter permission/ACTIVE state.

Conclusion: blind reconstruction closes an observable source requirement the old design leaves implicit.

### CMP-011 — Resource logical endpoint/presence
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Stakeholder source explicitly distinguishes logical Resource endpoint/presence identity from current address, allows Resource/endpoint before address, and allows several endpoints where they remain one access-management unit.

Old:
- Resource directly owns zero-or-one current AddressSpace;
- no independently stable endpoint/presence identity.

Blind:
- Resource owns stable Endpoint children;
- each endpoint may have zero/one current HostAddress/Prefix;
- address changes preserve Endpoint and Resource identity;
- materialization considers current endpoint realizations.

Conclusion: blind model preserves source-level logical presence semantics that old target compressed away.

### CMP-012 — Resource responsibility shape
Classification: NEW_BETTER_SUPPORTED with minor VALID_DESIGN_FREEDOM in representation
Priority: P2

Source says minimum Site + Owner group + Administrator group, with Owner/Admin distinct and not security authority.

Old:
- generic ResourceScopeAffiliation;
- extensible ResponsibilityRole;
- ResponsiblePartyRef permits person or team;
- overlapping roles allowed.

Blind:
- explicit reusable Site;
- Owner/Admin are organizational groups;
- at most one current group per each accepted role;
- responsibility is not authorization.

Conclusion: blind contract is closer to admitted source. Temporal representation remains design freedom.

### CMP-013 — deployment retirement lifecycle
Classification: VALID_DESIGN_FREEDOM / possible OLD_UNJUSTIFIED_DECISION outside selected MVP
Priority: P3

Old adds Active -> Retired ComponentDeployment lifecycle.
Blind selected MVP supports immutable deployment identity and creates another Deployment for materially different placement, but deliberately does not define retirement/delete.

No admitted source requires a deployment-retirement operation for the selected MVP. Old behavior is plausible future design but not required to close current implementation.

### CMP-014 — scoped/time authorization
Classification: OLD_BETTER_SUPPORTED + HARNESS_MISSED_CONCERN
Priority: P1

The original Wave-1 source explicitly requires:
- effective request authority for the relevant scope/time;
- required read/export authority for export selection;
- provenance from requesting actor + effective authority scope/time.

Old:
- Authority Management owns Actor/Action/Scope/Time effective authority;
- protected use cases call Admit(actor, action, scope).

Blind:
- defines exact operation permissions but makes them instance-wide because the sanitized Source Corpus omitted scope/time authority semantics.

Conclusion: old design is better supported here. This is not INSUFFICIENT_SOURCE_INPUT: the original source was available and was over-sanitized. The blind process therefore produced a false semantic closure for this concern.

### CMP-015 — authentication mechanism
Classification: VALID_DESIGN_FREEDOM
Priority: P3

Old uses local username/password + server-side HTTP-only session.
Blind uses external OIDC/JWT bearer identity.

No admitted product source requires either mechanism. Both can satisfy authenticated identity/admission if authorization semantics are correct. The blind choice is more operationally elaborate but remains engineering freedom; the material defect is scope/time authorization, not OIDC itself.

### CMP-016 — HTTP/JSON + OpenAPI
Classification: VALID_DESIGN_FREEDOM
Priority: P3

Old had an explicit stakeholder-approved engineering decision for HTTP/JSON/OpenAPI.
That decision was correctly excluded from blind Source Corpus because it was prior derived/representation design.
Blind independently selected HTTP/JSON and an explicit API contract.

Same outcome does not indicate contamination.

### CMP-017 — JSON result vs table/CSV
Classification: VALID_DESIGN_FREEDOM for backend blind scope
Priority: P3

Original Wave-1 source states CSV/XLSX/other serialization is an interface choice, not domain meaning.
Old first-MVP target fixes table + downloadable CSV.
Blind backend contract returns normalized JSON materialization and excludes frontend design.

Because frontend was intentionally excluded and source did not mandate CSV, this is not a blind defect.

### CMP-018 — policy subset selection
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Original Wave-1 source explicitly permits an authorized domain-policy subset.

Old:
- GET policy-export materializes all current effective rules; no explicit Rule subset contract.

Blind:
- ALL or explicit unique non-empty PolicyRule subset;
- selection uses domain policy identity;
- non-effective selected Rules remain explainable but do not require technical realization.

Conclusion: blind design implements accepted subset semantics omitted by old first-MVP contract.

### CMP-019 — non-effective selected Rule semantics
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Source acceptance says selected Inactive/out-of-condition Rules contribute no rows and missing realization for them must not fail the export.

Old lacks Active/Inactive/effective conditions and therefore cannot represent this behavior.
Blind explicitly separates all-selected provenance completeness from effective-only technical realization completeness.

### CMP-020 — export provenance completeness
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Source requires end-to-end business/request/decision/rule/state/property/source-fact/export provenance.

Old export row exposes Rule/revision/deployment/resource IDs, while generic provenance exists elsewhere. It does not make the exported result self-contained for request actor, authority, permission decision and all business justifications.

Blind:
- one self-contained MaterializedRuleProvenance per selected Rule;
- all AuthorizationEvidence and Need justification/currentness;
- decision actor/time;
- technical source-fact actor/time;
- policy.export caller can explain result without policy.read.

Conclusion: blind design materially strengthens source-required explainability.

### CMP-021 — materialization logical time/snapshot
Classification: NEW_BETTER_SUPPORTED in implementation closure; semantic goal shared
Priority: P1

Both require one logical export time and complete-or-unresolved behavior.

Old:
- states a complete read composition but does not close physical snapshot/evaluation-time implementation semantics.

Blind:
- one PostgreSQL read-only REPEATABLE READ snapshot;
- first statement returns transaction_timestamp() and that exact value is evaluationAt;
- preflight and emit share it.

Conclusion: old semantic direction is correct; blind design better satisfies the experiment criterion that coding must not choose consistency/time semantics.

### CMP-022 — idempotency/concurrency/optimistic locking
Classification: NEW_BETTER_SUPPORTED for implementation closure
Priority: P1

Old HTTP design maps a generic 409 conflict but does not define Idempotency-Key scope, replay ordering, exact response replay, concurrent identical-request resolution, aggregate version ownership or If-Match semantics.

Blind closes:
- target-scoped idempotency fingerprint;
- exact persisted original response replay;
- no invented TTL;
- replay-before-NEW-If-Match;
- concurrent in-progress resolution;
- per-aggregate ETag/If-Match ownership.

These are not necessarily product requirements, but leaving them open would force the implementation consumer to make material interface/data/concurrency decisions.

### CMP-023 — persistence ownership/topology
Classification: mostly VALID_DESIGN_FREEDOM; blind closure is more explicit
Priority: P2

Both independently converge on:
- one PostgreSQL database;
- modular-monolith owner schemas;
- no peer direct mutation/cross-owner DB ownership;
- local ACID transactions.

Differences such as JSONB versus normalized traffic-clause rows are physical design choices when accepted semantics are preserved. Blind additionally closes idempotency persistence, snapshot isolation, migration checksums/locking and richer provenance relations.

### CMP-024 — migration execution semantics
Classification: NEW_BETTER_SUPPORTED for implementation closure
Priority: P1

Old says module-owned migrations are applied as backend deployment concern but leaves runner/startup/concurrency/checksum semantics open.

Blind defines:
- separate `napms migrate` and `napms serve`;
- serve never applies DDL;
- ordered immutable id/checksum set;
- exclusive PostgreSQL advisory migration lock;
- transactional apply/rollback and exact schema verification.

This directly removes material implementation choices.

### CMP-025 — operability
Classification: NEW_BETTER_SUPPORTED
Priority: P1

Old observability has three useful requirements: outcome distinction, correlation, startup-vs-DB failure.
Blind retains those and additionally closes:
- structured event classes;
- redaction;
- health/live vs ready semantics;
- typed immutable configuration and unknown-key failure;
- dependency/request/DB timeouts;
- no automatic mutation retry;
- cancellation/shutdown;
- materialization response-commit boundary;
- OIDC readiness/cache lifecycle.

For an IMPLEMENTATION consumer the blind contract is substantially more complete.

### CMP-026 — threat/security analysis
Classification: mixed: NEW_BETTER_SUPPORTED for control closure; OLD_BETTER_SUPPORTED for scoped authorization
Priority: P1

Old threat model correctly preserves Authority Management as authorization owner but its local-session architecture leaves several trust/runtime details to implementation and scopes some production edge protections as deferred.

Blind performs a deeper explicit threat/control closure (JWT algorithms, kid, issuer/audience/time, JWKS lifecycle, forwarded identity distrust, redaction, dependency failure distinction), but misses source-required authorization scope/time.

Conclusion: neither entire security design dominates; scoped entitlement is an old/source advantage, while implementation-level trust/protection closure is stronger in blind design.

### CMP-027 — numeric quality targets
Classification: HARNESS_MISSED_CONCERN
Priority: P2

On 2026-09-19, explicit external product input answered that numeric latency, throughput, availability and scale targets are NOT_REQUIRED for the first MVP.

Old canonical requirements preserve that answer.
Blind Source Corpus did not admit it and classified these targets as DEFERRED_NONBLOCKING/unknown.

This did not block implementation, but it is still a source-corpus completeness failure: accepted source truth existed and was lost.

### CMP-028 — test/verification closure
Classification: NEW_BETTER_SUPPORTED for coding-agent handoff
Priority: P1

Old test intent has useful end-to-end/domain cases but omits many implementation-significant oracles: exact replay, optimistic concurrency, snapshot race, migration concurrency/checksum, OIDC key lifecycle, response streaming commit boundary, pagination/body bounds and provenance self-containment.

Blind Verification + Test Design closes those explicitly before coding.

### CMP-029 — broader future-domain contexts
Classification: VALID_DESIGN_FREEDOM / out-of-scope
Priority: P3

Old whole-domain strategic model contains Technical Access Evidence, Evidence Access Recognition, Network Enforcement Placement, Access Policy Realization and Network Environment Operations.
Blind selected backend reconstruction intentionally stops at current policy export because those areas are explicit first-MVP non-goals.

Their absence from the blind MVP closure is not a Harness miss.

### CMP-030 — contamination
Classification: INPUT_CONTAMINATION = NOT OBSERVED
Priority: none

No prior NAPMS derived design was deliberately opened before the final replacement freeze.
The recorded search-snippet contamination incident exposed fragments while locating candidate source files, but all such semantics were excluded unless independently admitted from source provenance.
Post-freeze comparison has not been used to mutate frozen artifacts.

## Aggregate comparison

### New reconstruction materially better supported/closed
- cross-Application and multi-Interaction semantics;
- permission-before-Rule lifecycle;
- source-defined semantic access identity;
- repeated allowed convergence + multi-authorization provenance;
- Active/Inactive and absolute effectiveness;
- participant-attributed and multi-Need justification;
- no-current-Need reconciliation;
- logical Resource endpoints;
- policy subset/non-effective selection semantics;
- self-contained export provenance;
- concurrency/idempotency/snapshot/migration/operability/test closure.

### Old design materially better supported
- actor/action/scope/time effective authorization, because that source requirement was lost during blind corpus sanitization.

### Valid design freedoms
- local session vs OIDC bearer;
- HTTP/OpenAPI choice;
- CSV/table vs JSON backend representation;
- many physical table/JSONB/index representation details;
- deployment retirement as a possible future lifecycle choice.

## Experiment-level conclusion from comparison

The blind reconstruction is not a clean unconditional success.

It demonstrates that current Harness topology + agent procedure can reconstruct a large, coherent backend design and in many areas correct unjustified decisions in the prior target design. However, the experiment also demonstrates a P1 failure in source classification: available accepted product semantics for authorization scope/time were omitted, allowing a semantically incomplete authorization model to pass the Coding-Agent Challenge and be frozen.

Therefore the final Harness claim must distinguish:
1. engineering-closure generation capability — strongly demonstrated;
2. source-corpus preservation/classification reliability — not yet sufficient for unconditional blind reconstruction;
3. structural COMPLETE — necessary but insufficient;
4. semantic consumer challenge — useful but insufficient when the source corpus itself has already lost a material requirement.
