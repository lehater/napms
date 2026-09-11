CREATE TABLE IF NOT EXISTS napms_resource_catalogue.resource_scope_affiliations (
    affiliation_reference text PRIMARY KEY,
    resource_reference text NOT NULL
        REFERENCES napms_resource_catalogue.resources(resource_reference),
    responsibility_scope text NOT NULL,
    valid_from timestamptz NOT NULL,
    valid_to timestamptz NULL,
    provenance_reference text NOT NULL,
    CHECK (length(affiliation_reference) > 0),
    CHECK (length(responsibility_scope) > 0),
    CHECK (length(provenance_reference) > 0),
    CHECK (valid_from < valid_to OR valid_to IS NULL)
);

CREATE INDEX IF NOT EXISTS ix_resource_scope_affiliation_effective_lookup
ON napms_resource_catalogue.resource_scope_affiliations (
    responsibility_scope,
    resource_reference,
    valid_from,
    valid_to
);
