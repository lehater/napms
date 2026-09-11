CREATE SCHEMA IF NOT EXISTS napms_application_catalogue;

CREATE TABLE IF NOT EXISTS napms_application_catalogue.component_deployments (
    component_deployment_id uuid PRIMARY KEY,
    provenance_reference text NOT NULL,
    CHECK (length(provenance_reference) > 0)
);

CREATE TABLE IF NOT EXISTS napms_application_catalogue.dcs_revisions (
    revision_id uuid PRIMARY KEY,
    source_component_deployment_id uuid NOT NULL
        REFERENCES napms_application_catalogue.component_deployments(component_deployment_id),
    destination_component_deployment_id uuid NOT NULL
        REFERENCES napms_application_catalogue.component_deployments(component_deployment_id),
    projection_payload bytea NOT NULL,
    provenance_reference text NOT NULL,
    CHECK (octet_length(projection_payload) > 0),
    CHECK (length(provenance_reference) > 0)
);

CREATE TABLE IF NOT EXISTS napms_application_catalogue.deployment_resource_bindings (
    reference_id text PRIMARY KEY,
    component_deployment_id uuid NOT NULL
        REFERENCES napms_application_catalogue.component_deployments(component_deployment_id),
    resource_reference text NOT NULL,
    valid_from timestamptz NOT NULL,
    valid_to timestamptz NULL,
    provenance_reference text NOT NULL,
    CHECK (length(reference_id) > 0),
    CHECK (length(resource_reference) > 0),
    CHECK (length(provenance_reference) > 0),
    CHECK (valid_from < valid_to OR valid_to IS NULL)
);

CREATE INDEX IF NOT EXISTS ix_acc_binding_effective_lookup
ON napms_application_catalogue.deployment_resource_bindings (
    component_deployment_id,
    valid_from,
    valid_to,
    resource_reference
);
