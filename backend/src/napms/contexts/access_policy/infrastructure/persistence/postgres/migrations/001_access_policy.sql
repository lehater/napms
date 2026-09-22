CREATE SCHEMA IF NOT EXISTS access_policy;

CREATE TABLE IF NOT EXISTS access_policy.access_request (
    request_ref uuid PRIMARY KEY,
    source_deployment_ref uuid NOT NULL,
    destination_deployment_ref uuid NOT NULL,
    interaction_revision_ref uuid NOT NULL,
    initial_need_ref uuid NOT NULL,
    validated_business_process_version bigint NOT NULL,
    submitter_subject text NOT NULL,
    submitted_at timestamptz NOT NULL,
    decision_result text NULL,
    external_decision_ref text NULL,
    decided_by_subject text NULL,
    decided_at timestamptz NULL,
    version bigint NOT NULL,
    CONSTRAINT ck_request_decision
        CHECK (decision_result IS NULL OR decision_result IN ('ALLOWED', 'DENIED'))
);

CREATE TABLE IF NOT EXISTS access_policy.access_request_authority_evidence (
    evidence_ref uuid PRIMARY KEY,
    request_ref uuid NOT NULL REFERENCES access_policy.access_request(request_ref) ON DELETE RESTRICT,
    scope_ref text NOT NULL,
    action text NOT NULL,
    grant_effective_from timestamptz NULL,
    grant_effective_until timestamptz NULL,
    evaluated_at timestamptz NOT NULL,
    CONSTRAINT ck_request_authority_action CHECK (action = 'access.request')
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_request_authority_scope
    ON access_policy.access_request_authority_evidence(request_ref, scope_ref, action);

CREATE TABLE IF NOT EXISTS access_policy.policy_rule (
    rule_ref uuid PRIMARY KEY,
    source_deployment_ref uuid NOT NULL,
    destination_deployment_ref uuid NOT NULL,
    interaction_revision_ref uuid NOT NULL,
    effect_state text NOT NULL,
    effective_from timestamptz NULL,
    effective_until timestamptz NULL,
    version bigint NOT NULL,
    created_at timestamptz NOT NULL,
    CONSTRAINT ck_rule_effect_state CHECK (effect_state IN ('ACTIVE', 'INACTIVE'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_policy_rule_access_subject
    ON access_policy.policy_rule(
        source_deployment_ref,
        destination_deployment_ref,
        interaction_revision_ref
    );

CREATE TABLE IF NOT EXISTS access_policy.policy_rule_authorization_evidence (
    evidence_ref uuid PRIMARY KEY,
    rule_ref uuid NOT NULL REFERENCES access_policy.policy_rule(rule_ref) ON DELETE RESTRICT,
    access_request_ref uuid NOT NULL REFERENCES access_policy.access_request(request_ref) ON DELETE RESTRICT,
    external_decision_ref text NULL,
    decided_by_subject text NOT NULL,
    decided_at timestamptz NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_authorization_request
    ON access_policy.policy_rule_authorization_evidence(access_request_ref);

CREATE TABLE IF NOT EXISTS access_policy.policy_rule_justification (
    association_ref uuid PRIMARY KEY,
    rule_ref uuid NOT NULL REFERENCES access_policy.policy_rule(rule_ref) ON DELETE RESTRICT,
    need_ref uuid NOT NULL,
    attached_at timestamptz NOT NULL,
    attached_by_subject text NOT NULL,
    source_access_request_ref uuid NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_rule_need_justification
    ON access_policy.policy_rule_justification(rule_ref, need_ref);

CREATE TABLE IF NOT EXISTS access_policy.policy_rule_operational_history (
    history_ref uuid PRIMARY KEY,
    rule_ref uuid NOT NULL REFERENCES access_policy.policy_rule(rule_ref) ON DELETE RESTRICT,
    rule_version bigint NOT NULL,
    effect_state text NOT NULL,
    effective_from timestamptz NULL,
    effective_until timestamptz NULL,
    changed_by_subject text NOT NULL,
    changed_at timestamptz NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_rule_operational_version
    ON access_policy.policy_rule_operational_history(rule_ref, rule_version);
