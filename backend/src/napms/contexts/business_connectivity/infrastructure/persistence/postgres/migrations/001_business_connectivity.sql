CREATE SCHEMA IF NOT EXISTS business_connectivity;

CREATE TABLE IF NOT EXISTS business_connectivity.business_process (
    process_ref uuid PRIMARY KEY,
    name text NOT NULL,
    description text NULL,
    organization_external_reference text NULL,
    organization_display_name text NULL,
    criticality_label text NULL,
    version bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS business_connectivity.connectivity_need (
    need_ref uuid PRIMARY KEY,
    process_ref uuid NOT NULL
        REFERENCES business_connectivity.business_process(process_ref)
        ON DELETE RESTRICT,
    interaction_ref uuid NOT NULL,
    participant_component_ref uuid NOT NULL,
    business_basis text NOT NULL,
    status text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    created_by_subject text NOT NULL,
    retired_at timestamptz NULL,
    CONSTRAINT ck_need_status CHECK (status IN ('ACTIVE', 'RETIRED'))
);

CREATE INDEX IF NOT EXISTS ix_need_interaction
    ON business_connectivity.connectivity_need(interaction_ref);
