# Wave-1 Domain Message Flows — PLAN-027 WP-02

Status: `accepted architecture input — transport-neutral semantic flows`.

Date: 2026-09-08.

## Principle

Flows name semantic requests/results/queries and owners. They do not choose synchronous/asynchronous transport, API protocol, process boundaries or deployment units.

## F1 — Propose connectivity and consume decision

1. Actor requests `ComposeAccessRuleProposal(scope, sourceDeployment, destinationDeployment, dcsRef)`.
2. Authority Management answers `AuthorityCheck(propose connectivity, scope, effectiveTime) -> permitted | not permitted`.
3. Application Communication Catalogue resolves/validates exact Source Deployment + Destination Deployment + immutable DCS contract/revision and described directed interaction.
4. If authority or structural validity is absent/unknown, no valid proposal is submitted.
5. Application composition emits immutable `AccessRuleProposal(subject = exact semantic identity)`.
6. Deferred Connectivity Decision Domain returns `ConnectivityDecision(subject, Allowed | NotAllowed, opaque provenance/reasonRef where available)`.
7. Access Policy verifies decision subject matches exact proposal identity.
8. `Allowed` -> `MaterializeOrResolveRule(subject, decisionRef)`; `NotAllowed` -> no authoritative Rule.
9. Access Policy atomically/idempotently resolves one Rule ID for the semantic identity; first materialization is Active.
10. The accepted proposal authority scope becomes the materialized Rule's stable non-identity governance scope for later Rule actions.

Failure semantics: identity mismatch, unknown decision subject or failed Access Policy invariants must not materialize a Rule. Retries/concurrency must not create duplicates.

## F2 — Change Rule operational state

1. Actor requests `SetRuleOperationalState(ruleId, Active|Inactive)`; caller does not supply an authority scope.
2. Access Policy loads the authoritative Rule and obtains its stored governance scope.
3. Authority Management evaluates `SetRuleOperationalState` authority for that governance scope and effective time.
4. Denied/unknown authority produces no state/audit mutation.
5. If requested state equals current state, return explicit no accepted transition and produce no transition audit.
6. Access Policy applies only `Active -> Inactive` or `Inactive -> Active`.
7. Access Policy records attributable temporal business audit/provenance: Rule, from/to, actor, effective time, governance scope and authority provenance/reference.
8. State change and audit are committed atomically.
9. Rule ID, semantic identity, governance scope and Connectivity Decision correlation remain unchanged.

Failure semantics: absent/unknown authority, unknown Rule, same-state request, invalid domain mutation or failed persistence produces no accepted state change. A caller cannot substitute another scope for authorization.

## F3 — Produce Normalized Policy Export

1. Actor requests export for an authorized domain-policy selection and logical `asOf`.
2. Authority Management evaluates read/export authority for scope/time.
3. Access Policy determines selected effective desired Rules at `asOf`: authoritative from Allowed AND Active AND declarative effective conditions permit.
4. For every selected effective Rule, Resource Catalogue resolves source/destination technical realization valid for `asOf`.
5. Application Communication Catalogue supplies referenced DCS protocol/service/port semantics and required valid projection facts.
6. Export composition verifies temporal coherence and required provenance.
7. Rules expand to one or more normalized rows as required; Rule/decision/source correlations remain traceable.
8. Only if every selected effective Rule is truthfully projectable does the operation return `SuccessfulNormalizedPolicyExport(asOf, rows, provenance)`.

Failure semantics: missing/stale/unknown required realization or DCS fact for any selected effective Rule yields explicit non-success/degraded diagnostics. Partial diagnostic rows may be returned but are not a successful downstream-ready export.

## F4 — Technical realization changes without semantic Rule change

1. Resource Catalogue accepts a new authoritative endpoint/address realization for a Resource/Endpoint.
2. Existing Access Rule identity/decision/state are not rewritten.
3. A later F3 export resolves the realization valid for its own `asOf` and therefore may emit different technical rows for the same Rule ID.

This flow is the key guardrail separating semantic policy identity from mutable technical realization.

## F5 — Identity-defining semantic change

1. Source Deployment, Destination Deployment or decision-relevant DCS contract/revision changes.
2. Application composition must form a new proposal subject.
3. Existing Rule/Connectivity Decision are not silently rebound to the new identity.
4. New subject requires a new Connectivity Decision before Access Policy may materialize the corresponding Rule.

## Temporal/consistency implications handed to architecture

- Access Policy uniqueness/materialization requires an authoritative atomic consistency point.
- Access Policy state mutation + audit require one authoritative transactional write boundary.
- Successful export requires a credible logical-as-of strategy across Access Policy + Resource Catalogue + Application Communication Catalogue facts; it does not require those facts to share one physical database.
- Provenance must cross every semantic boundary used in export.
- Authority checks are action-scoped inputs, not static UI role assumptions.
- Rule action authorization uses the Rule's authoritative governance scope rather than caller-supplied scope.
- Connectivity Decision is a semantic dependency whose implementation/transport is intentionally unresolved.

## WP-02 result

Critical propose/decide/materialize, state-management and export flows are explicit through commands/results/queries, authority, temporal semantics and failure behavior without choosing transport or deployment topology.
