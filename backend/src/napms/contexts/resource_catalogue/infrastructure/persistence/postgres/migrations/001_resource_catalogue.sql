CREATE SCHEMA IF NOT EXISTS resource_catalogue;

CREATE TABLE IF NOT EXISTS resource_catalogue.resource (
    resource_ref uuid PRIMARY KEY,
    display_name text NOT NULL,
    authority_scope_ref text NOT NULL,
    version bigint NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS resource_catalogue.site (
    site_ref uuid PRIMARY KEY,
    name text NOT NULL,
    description text NULL
);

CREATE TABLE IF NOT EXISTS resource_catalogue.responsibility_group (
    group_ref uuid PRIMARY KEY,
    display_name text NOT NULL,
    external_reference text NULL
);

CREATE TABLE IF NOT EXISTS resource_catalogue.resource_site_history (
    history_ref uuid PRIMARY KEY,
    resource_ref uuid NOT NULL REFERENCES resource_catalogue.resource(resource_ref) ON DELETE RESTRICT,
    site_ref uuid NULL REFERENCES resource_catalogue.site(site_ref) ON DELETE RESTRICT,
    effective_from timestamptz NOT NULL,
    effective_to timestamptz NULL,
    changed_by_subject text NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_resource_current_site
    ON resource_catalogue.resource_site_history(resource_ref)
    WHERE effective_to IS NULL;

CREATE TABLE IF NOT EXISTS resource_catalogue.resource_endpoint (
    endpoint_ref uuid PRIMARY KEY,
    resource_ref uuid NOT NULL REFERENCES resource_catalogue.resource(resource_ref) ON DELETE RESTRICT,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS resource_catalogue.resource_endpoint_address_history (
    address_fact_ref uuid PRIMARY KEY,
    endpoint_ref uuid NOT NULL REFERENCES resource_catalogue.resource_endpoint(endpoint_ref) ON DELETE RESTRICT,
    address_kind text NOT NULL,
    address_value text NOT NULL,
    effective_from timestamptz NOT NULL,
    effective_to timestamptz NULL,
    changed_by_subject text NOT NULL,
    CONSTRAINT ck_endpoint_address_kind CHECK (address_kind IN ('HOST', 'PREFIX'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_endpoint_current_address
    ON resource_catalogue.resource_endpoint_address_history(endpoint_ref)
    WHERE effective_to IS NULL;

CREATE TABLE IF NOT EXISTS resource_catalogue.resource_responsibility_history (
    assignment_ref uuid PRIMARY KEY,
    resource_ref uuid NOT NULL REFERENCES resource_catalogue.resource(resource_ref) ON DELETE RESTRICT,
    role text NOT NULL,
    group_ref uuid NOT NULL REFERENCES resource_catalogue.responsibility_group(group_ref) ON DELETE RESTRICT,
    effective_from timestamptz NOT NULL,
    effective_to timestamptz NULL,
    changed_by_subject text NOT NULL,
    CONSTRAINT ck_resource_responsibility_role CHECK (role IN ('OWNER', 'ADMINISTRATOR'))
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_resource_current_responsibility
    ON resource_catalogue.resource_responsibility_history(resource_ref, role)
    WHERE effective_to IS NULL;
