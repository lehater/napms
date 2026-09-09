CREATE SCHEMA IF NOT EXISTS napms_connectivity_decision;

CREATE TABLE IF NOT EXISTS napms_connectivity_decision.connectivity_decisions (
    decision_id uuid PRIMARY KEY,
    governance_scope text NOT NULL,
    source_component_deployment_id uuid NOT NULL,
    destination_component_deployment_id uuid NOT NULL,
    dcs_contract_revision_id uuid NOT NULL,
    outcome text NOT NULL,
    valid_from timestamptz NOT NULL,
    valid_until timestamptz NULL,
    reason_code text NOT NULL,
    reason_text text NOT NULL,
    evidence_references jsonb NOT NULL DEFAULT '[]'::jsonb,
    deciding_actor_id text NOT NULL,
    decided_at timestamptz NOT NULL,
    authority_reference text NOT NULL,
    supersedes_decision_id uuid NULL,

    CONSTRAINT ck_connectivity_decision_scope_nonempty
        CHECK (length(btrim(governance_scope)) > 0),
    CONSTRAINT ck_connectivity_decision_outcome
        CHECK (outcome IN ('Allowed', 'NotAllowed')),
    CONSTRAINT ck_connectivity_decision_validity
        CHECK (valid_until IS NULL OR valid_from < valid_until),
    CONSTRAINT ck_connectivity_decision_reason_code_nonempty
        CHECK (length(btrim(reason_code)) > 0),
    CONSTRAINT ck_connectivity_decision_reason_text_nonempty
        CHECK (length(btrim(reason_text)) > 0),
    CONSTRAINT ck_connectivity_decision_evidence_array
        CHECK (jsonb_typeof(evidence_references) = 'array'),
    CONSTRAINT ck_connectivity_decision_actor_nonempty
        CHECK (length(btrim(deciding_actor_id)) > 0),
    CONSTRAINT ck_connectivity_decision_authority_nonempty
        CHECK (length(btrim(authority_reference)) > 0),
    CONSTRAINT ck_connectivity_decision_not_self_superseding
        CHECK (
            supersedes_decision_id IS NULL
            OR supersedes_decision_id <> decision_id
        ),
    CONSTRAINT uq_connectivity_decision_identity_subject
        UNIQUE (
            decision_id,
            governance_scope,
            source_component_deployment_id,
            destination_component_deployment_id,
            dcs_contract_revision_id
        ),
    CONSTRAINT uq_connectivity_decision_single_successor
        UNIQUE (supersedes_decision_id),
    CONSTRAINT fk_connectivity_decision_supersedes_same_subject
        FOREIGN KEY (
            supersedes_decision_id,
            governance_scope,
            source_component_deployment_id,
            destination_component_deployment_id,
            dcs_contract_revision_id
        )
        REFERENCES napms_connectivity_decision.connectivity_decisions (
            decision_id,
            governance_scope,
            source_component_deployment_id,
            destination_component_deployment_id,
            dcs_contract_revision_id
        )
);

CREATE INDEX IF NOT EXISTS ix_connectivity_decision_subject_scope_validity
ON napms_connectivity_decision.connectivity_decisions (
    governance_scope,
    source_component_deployment_id,
    destination_component_deployment_id,
    dcs_contract_revision_id,
    valid_from
);

CREATE INDEX IF NOT EXISTS ix_connectivity_decision_scope_decided
ON napms_connectivity_decision.connectivity_decisions (
    governance_scope,
    decided_at DESC,
    decision_id
);

CREATE OR REPLACE FUNCTION napms_connectivity_decision.reject_decision_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'Connectivity Decision records are immutable'
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_connectivity_decision_immutable
ON napms_connectivity_decision.connectivity_decisions;

CREATE TRIGGER trg_connectivity_decision_immutable
BEFORE UPDATE OR DELETE
ON napms_connectivity_decision.connectivity_decisions
FOR EACH ROW
EXECUTE FUNCTION napms_connectivity_decision.reject_decision_mutation();
