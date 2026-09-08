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

## F2b — Change Rule EffectiveWindow

1. Actor requests `SetRuleEffectiveWindow(ruleId, window|None)`; caller does not supply an authority scope.
2. Access Policy loads the authoritative Rule and obtains its stored RuleGovernanceScope.
3. Authority Management evaluates `SetRuleEffectiveWindow` authority for that scope/effective time.
4. Denied/unknown/missing authority produces no property/audit mutation.
5. Same window value produces explicit no accepted change and no property-change audit.
6. Access Policy applies the new optional EffectiveWindow while preserving RuleId, semantic identity, governance scope, operational state and Connectivity Decision correlation.
7. Access Policy records old/new window, actor, effective time, governance scope and authority provenance/reference.
8. Property change and audit commit atomically.

Failure semantics: absent/unknown authority, unknown Rule, same value, invalid EffectiveWindow or failed persistence produces no accepted property change.

## F3 — Select effective desired policy and produce Normalized Policy Export

1. Actor requests `SelectEffectiveDesiredPolicy(scope, asOf)`, where scope is one RuleGovernanceScope.
2. Authority Management evaluates `ReadEffectiveDesiredPolicy` authority for that scope/asOf.
3. Denied/unknown/missing authority produces no selected policy data.
4. Access Policy selects authoritative Rules whose stored RuleGovernanceScope equals the authorized scope.
5. Access Policy keeps only Rules that are Active and whose optional EffectiveWindow permits effect at `asOf` using `start <= asOf < end`.
6. The resulting effective desired-policy selection is handed to later export composition.
7. For every selected effective Rule, Application Communication Catalogue resolves the exact RuleSemanticIdentity at `asOf`, returning source/destination ComponentDeployment -> one-or-more stable Resource references plus complete immutable DCS projection-semantics payload and binding/DCS provenance.
8. Export composition verifies exact subject/DCS correlation and required ACC provenance/validity evidence.
9. For every returned Resource reference, Resource Catalogue resolves one-or-more endpoint/address realizations proven valid for `asOf`, with stable fact/version/effective-validity evidence and source provenance.
10. Export composition assembles an immutable logical Export Snapshot only if every selected effective Rule has complete coherent ACC + RC facts.
11. I6 locally decodes each captured immutable DCS projection payload into one-or-more source-neutral `DcsTrafficAlternative` values: canonical protocol token, explicit source/destination port constraints (`NotApplicable | Any | canonical inclusive PortRange set`) and optional ACC service reference.
12. I6 transforms each successful snapshot item into the deterministic product of captured source endpoint/address realizations × captured destination endpoint/address realizations × DCS traffic alternatives.
13. Every normalized row retains its single authoritative Rule/decision correlation, snapshot `asOf`/read-authority provenance and contributing ACC/RC fact/validity/provenance; independent Rules are never provenance-losing merged.
14. Only after complete normalization may the operation return a successful Normalized Policy Export.

Failure semantics: unauthorized selection returns no policy data. ACC subject/DCS mismatch, missing/invalid/unknown deployment-resource binding or DCS projection fact, or missing/stale/unknown RC realization for any selected effective Rule prevents a successful Export Snapshot. Diagnostics may retain partial captured evidence, but no successful snapshot or downstream-ready export is produced.

The first selection is one governance scope at a time. Arbitrary vendor/device/technical filters are not selection-membership authority.

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
- Access Policy state/property mutation + audit require one authoritative transactional write boundary.
- Successful export requires a credible logical-as-of strategy across Access Policy + Application Communication Catalogue deployment/resource bindings + Resource Catalogue realizations + DCS facts; it does not require those facts to share one physical database.
- Provenance must cross every semantic boundary used in export.
- Authority checks are action-scoped inputs, not static UI role assumptions.
- Rule action authorization uses the Rule's authoritative governance scope rather than caller-supplied scope.
- Effective-policy membership uses the same stored RuleGovernanceScope after read authority is established; caller filters cannot manufacture membership.
- EffectiveWindow is evaluated against the explicit logical `asOf`; no hidden wall-clock evaluation belongs in Domain/Application.
- ComponentDeployment -> Resource-reference binding is owned by Application Communication Catalogue; Resource Catalogue resolves realization only for stable Resource references.
- I5 captures complete immutable DCS projection semantics without interpreting normalization-facing protocol/service/port structure; I6 defines/uses the bounded DcsTrafficAlternative schema.
- DCS payload byte encoding/codec is a local translation concern; normalization performs no live catalogue lookup.
- Normalized row expansion is deterministic source realization × destination realization × DCS alternative and never cross-Rule merges provenance.
- Connectivity Decision is a semantic dependency whose implementation/transport is intentionally unresolved.

## WP-02 result

Critical propose/decide/materialize, state-management and export flows are explicit through commands/results/queries, authority, temporal semantics and failure behavior without choosing transport or deployment topology.
