CREATE SCHEMA IF NOT EXISTS napms_resource_catalogue;

CREATE TABLE IF NOT EXISTS napms_resource_catalogue.resources (
    resource_reference text PRIMARY KEY,
    provenance_reference text NOT NULL,
    CHECK (length(resource_reference) > 0),
    CHECK (length(provenance_reference) > 0)
);

CREATE TABLE IF NOT EXISTS napms_resource_catalogue.resource_realization_versions (
    fact_reference text PRIMARY KEY,
    resource_reference text NOT NULL
        REFERENCES napms_resource_catalogue.resources(resource_reference),
    valid_from timestamptz NOT NULL,
    valid_to timestamptz NULL,
    provenance_reference text NOT NULL,
    CHECK (length(fact_reference) > 0),
    CHECK (length(provenance_reference) > 0),
    CHECK (valid_from < valid_to OR valid_to IS NULL)
);

CREATE TABLE IF NOT EXISTS napms_resource_catalogue.resource_endpoints (
    fact_reference text NOT NULL
        REFERENCES napms_resource_catalogue.resource_realization_versions(fact_reference)
        ON DELETE CASCADE,
    endpoint_reference text NOT NULL,
    technical_address text NOT NULL,
    PRIMARY KEY (fact_reference, endpoint_reference, technical_address),
    CHECK (length(endpoint_reference) > 0),
    CHECK (length(technical_address) > 0)
);

CREATE INDEX IF NOT EXISTS ix_resource_realization_effective_lookup
ON napms_resource_catalogue.resource_realization_versions (
    resource_reference,
    valid_from,
    valid_to
);
