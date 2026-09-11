CREATE SCHEMA IF NOT EXISTS napms_access_policy;

CREATE TABLE IF NOT EXISTS napms_access_policy.access_rules (
    rule_id uuid PRIMARY KEY,
    source_component_deployment_id uuid NOT NULL,
    destination_component_deployment_id uuid NOT NULL,
    dcs_contract_revision_id uuid NOT NULL,
    operational_state text NOT NULL
        CHECK (operational_state IN ('Active', 'Inactive')),
    decision_result text NOT NULL
        CHECK (decision_result = 'Allowed'),
    decision_id text NULL,
    proposal_actor_id text NOT NULL,
    proposal_authority_scope text NOT NULL,
    proposal_effective_time timestamptz NOT NULL,
    authority_reference text NOT NULL,
    catalogue_reference text NOT NULL,
    CONSTRAINT uq_access_rules_semantic_identity UNIQUE (
        source_component_deployment_id,
        destination_component_deployment_id,
        dcs_contract_revision_id
    )
);
