CREATE SCHEMA IF NOT EXISTS napms_authority;

CREATE TABLE IF NOT EXISTS napms_authority.authority_assignments (
    reference_id text PRIMARY KEY,
    actor_id text NOT NULL,
    action text NOT NULL,
    scope text NOT NULL,
    valid_from timestamptz NOT NULL,
    valid_to timestamptz NULL,
    provenance_reference text NOT NULL,
    CHECK (valid_from < valid_to OR valid_to IS NULL)
);

CREATE INDEX IF NOT EXISTS ix_authority_assignment_lookup
ON napms_authority.authority_assignments (
    actor_id,
    action,
    scope,
    valid_from,
    valid_to
);
