CREATE SCHEMA IF NOT EXISTS application_communication_catalogue;

CREATE TABLE IF NOT EXISTS application_communication_catalogue.application (
    application_ref uuid PRIMARY KEY,
    name text NOT NULL,
    version bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS application_communication_catalogue.component (
    component_ref uuid PRIMARY KEY,
    application_ref uuid NOT NULL
        REFERENCES application_communication_catalogue.application(application_ref)
        ON DELETE RESTRICT,
    name text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS application_communication_catalogue.interaction (
    interaction_ref uuid PRIMARY KEY,
    source_component_ref uuid NOT NULL
        REFERENCES application_communication_catalogue.component(component_ref)
        ON DELETE RESTRICT,
    destination_component_ref uuid NOT NULL
        REFERENCES application_communication_catalogue.component(component_ref)
        ON DELETE RESTRICT,
    purpose text NULL,
    version bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_interaction_pair
    ON application_communication_catalogue.interaction(
        source_component_ref,
        destination_component_ref
    );

CREATE TABLE IF NOT EXISTS application_communication_catalogue.interaction_revision (
    revision_ref uuid PRIMARY KEY,
    interaction_ref uuid NOT NULL
        REFERENCES application_communication_catalogue.interaction(interaction_ref)
        ON DELETE RESTRICT,
    revision_no bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    created_by_subject text NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_interaction_revision_no
    ON application_communication_catalogue.interaction_revision(interaction_ref, revision_no);

CREATE TABLE IF NOT EXISTS application_communication_catalogue.interaction_traffic_clause (
    clause_ref uuid PRIMARY KEY,
    revision_ref uuid NOT NULL
        REFERENCES application_communication_catalogue.interaction_revision(revision_ref)
        ON DELETE RESTRICT,
    clause_ordinal integer NOT NULL,
    ip_protocol integer NOT NULL,
    CONSTRAINT ck_ip_protocol CHECK (ip_protocol BETWEEN 0 AND 255)
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_revision_clause_ordinal
    ON application_communication_catalogue.interaction_traffic_clause(
        revision_ref,
        clause_ordinal
    );

CREATE TABLE IF NOT EXISTS application_communication_catalogue.interaction_port_range (
    range_ref uuid PRIMARY KEY,
    clause_ref uuid NOT NULL
        REFERENCES application_communication_catalogue.interaction_traffic_clause(clause_ref)
        ON DELETE RESTRICT,
    direction text NOT NULL,
    range_ordinal integer NOT NULL,
    port_from integer NOT NULL,
    port_to integer NOT NULL,
    CONSTRAINT ck_port_direction CHECK (direction IN ('SOURCE', 'DESTINATION')),
    CONSTRAINT ck_port_bounds CHECK (
        port_from BETWEEN 0 AND 65535
        AND port_to BETWEEN port_from AND 65535
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_clause_direction_range
    ON application_communication_catalogue.interaction_port_range(
        clause_ref,
        direction,
        range_ordinal
    );
