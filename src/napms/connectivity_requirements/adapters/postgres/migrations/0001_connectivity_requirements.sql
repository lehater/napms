CREATE SCHEMA IF NOT EXISTS napms_connectivity_requirements;

CREATE TABLE IF NOT EXISTS napms_connectivity_requirements.connectivity_requirements (
    requirement_id uuid PRIMARY KEY,
    governance_scope text NOT NULL,
    dependent_component_deployment_id uuid NOT NULL,
    source_component_deployment_id uuid NOT NULL,
    destination_component_deployment_id uuid NOT NULL,
    dcs_contract_revision_id uuid NOT NULL,
    applicability_kind text NOT NULL,
    applicability_start timestamptz NULL,
    applicability_end timestamptz NULL,
    justification text NOT NULL,
    lifecycle_state text NOT NULL,
    declaration_actor_id text NOT NULL,
    declaration_effective_time timestamptz NOT NULL,
    declaration_authority_reference text NOT NULL,
    declaration_catalogue_reference text NULL,
    version bigint NOT NULL,

    CONSTRAINT ck_connectivity_requirement_scope_nonempty
        CHECK (length(btrim(governance_scope)) > 0),
    CONSTRAINT ck_connectivity_requirement_dependent_participates
        CHECK (
            dependent_component_deployment_id = source_component_deployment_id
            OR dependent_component_deployment_id = destination_component_deployment_id
        ),
    CONSTRAINT ck_connectivity_requirement_applicability
        CHECK (
            (
                applicability_kind = 'Ongoing'
                AND applicability_start IS NULL
                AND applicability_end IS NULL
            )
            OR
            (
                applicability_kind = 'AbsoluteWindow'
                AND applicability_start IS NOT NULL
                AND applicability_end IS NOT NULL
                AND applicability_start < applicability_end
            )
        ),
    CONSTRAINT ck_connectivity_requirement_justification_nonempty
        CHECK (length(btrim(justification)) > 0),
    CONSTRAINT ck_connectivity_requirement_lifecycle
        CHECK (lifecycle_state IN ('Active', 'Retired')),
    CONSTRAINT ck_connectivity_requirement_actor_nonempty
        CHECK (length(btrim(declaration_actor_id)) > 0),
    CONSTRAINT ck_connectivity_requirement_authority_nonempty
        CHECK (length(btrim(declaration_authority_reference)) > 0),
    CONSTRAINT ck_connectivity_requirement_version
        CHECK (version >= 1)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_connectivity_requirements_active_semantic
ON napms_connectivity_requirements.connectivity_requirements (
    governance_scope,
    dependent_component_deployment_id,
    source_component_deployment_id,
    destination_component_deployment_id,
    dcs_contract_revision_id
)
WHERE lifecycle_state = 'Active';

CREATE INDEX IF NOT EXISTS ix_connectivity_requirements_scope_id
ON napms_connectivity_requirements.connectivity_requirements (
    governance_scope,
    requirement_id
);

CREATE TABLE IF NOT EXISTS napms_connectivity_requirements.applicability_changes (
    requirement_id uuid NOT NULL
        REFERENCES napms_connectivity_requirements.connectivity_requirements(requirement_id),
    sequence_no integer NOT NULL,
    previous_kind text NOT NULL,
    previous_start timestamptz NULL,
    previous_end timestamptz NULL,
    new_kind text NOT NULL,
    new_start timestamptz NULL,
    new_end timestamptz NULL,
    actor_id text NOT NULL,
    effective_time timestamptz NOT NULL,
    governance_scope text NOT NULL,
    authority_reference text NOT NULL,
    PRIMARY KEY (requirement_id, sequence_no),
    CONSTRAINT ck_requirement_applicability_change_previous
        CHECK (
            (
                previous_kind = 'Ongoing'
                AND previous_start IS NULL
                AND previous_end IS NULL
            )
            OR
            (
                previous_kind = 'AbsoluteWindow'
                AND previous_start IS NOT NULL
                AND previous_end IS NOT NULL
                AND previous_start < previous_end
            )
        ),
    CONSTRAINT ck_requirement_applicability_change_new
        CHECK (
            (
                new_kind = 'Ongoing'
                AND new_start IS NULL
                AND new_end IS NULL
            )
            OR
            (
                new_kind = 'AbsoluteWindow'
                AND new_start IS NOT NULL
                AND new_end IS NOT NULL
                AND new_start < new_end
            )
        ),
    CONSTRAINT ck_requirement_applicability_change_actor
        CHECK (length(btrim(actor_id)) > 0),
    CONSTRAINT ck_requirement_applicability_change_scope
        CHECK (length(btrim(governance_scope)) > 0),
    CONSTRAINT ck_requirement_applicability_change_authority
        CHECK (length(btrim(authority_reference)) > 0)
);

CREATE TABLE IF NOT EXISTS napms_connectivity_requirements.justification_changes (
    requirement_id uuid NOT NULL
        REFERENCES napms_connectivity_requirements.connectivity_requirements(requirement_id),
    sequence_no integer NOT NULL,
    previous_justification text NOT NULL,
    new_justification text NOT NULL,
    actor_id text NOT NULL,
    effective_time timestamptz NOT NULL,
    governance_scope text NOT NULL,
    authority_reference text NOT NULL,
    PRIMARY KEY (requirement_id, sequence_no),
    CONSTRAINT ck_requirement_justification_change_previous
        CHECK (length(btrim(previous_justification)) > 0),
    CONSTRAINT ck_requirement_justification_change_new
        CHECK (length(btrim(new_justification)) > 0),
    CONSTRAINT ck_requirement_justification_change_actor
        CHECK (length(btrim(actor_id)) > 0),
    CONSTRAINT ck_requirement_justification_change_scope
        CHECK (length(btrim(governance_scope)) > 0),
    CONSTRAINT ck_requirement_justification_change_authority
        CHECK (length(btrim(authority_reference)) > 0)
);

CREATE TABLE IF NOT EXISTS napms_connectivity_requirements.lifecycle_transitions (
    requirement_id uuid NOT NULL
        REFERENCES napms_connectivity_requirements.connectivity_requirements(requirement_id),
    sequence_no integer NOT NULL,
    from_state text NOT NULL,
    to_state text NOT NULL,
    actor_id text NOT NULL,
    effective_time timestamptz NOT NULL,
    governance_scope text NOT NULL,
    authority_reference text NOT NULL,
    PRIMARY KEY (requirement_id, sequence_no),
    CONSTRAINT ck_requirement_lifecycle_transition
        CHECK (from_state = 'Active' AND to_state = 'Retired'),
    CONSTRAINT ck_requirement_lifecycle_actor
        CHECK (length(btrim(actor_id)) > 0),
    CONSTRAINT ck_requirement_lifecycle_scope
        CHECK (length(btrim(governance_scope)) > 0),
    CONSTRAINT ck_requirement_lifecycle_authority
        CHECK (length(btrim(authority_reference)) > 0)
);
