ALTER TABLE napms_resource_catalogue.resources
ADD COLUMN IF NOT EXISTS display_name text NULL;

ALTER TABLE napms_resource_catalogue.resources
ADD COLUMN IF NOT EXISTS lifecycle_state text NOT NULL DEFAULT 'Active';

ALTER TABLE napms_resource_catalogue.resources
ADD COLUMN IF NOT EXISTS retirement_provenance_reference text NULL;

ALTER TABLE napms_resource_catalogue.resources
ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1;

ALTER TABLE napms_resource_catalogue.resource_realization_versions
ADD COLUMN IF NOT EXISTS end_provenance_reference text NULL;

ALTER TABLE napms_resource_catalogue.resource_realization_versions
ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1;

ALTER TABLE napms_resource_catalogue.resource_scope_affiliations
ADD COLUMN IF NOT EXISTS end_provenance_reference text NULL;

ALTER TABLE napms_resource_catalogue.resource_scope_affiliations
ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1;

CREATE TABLE IF NOT EXISTS napms_resource_catalogue.resource_responsibilities (
    assignment_reference text PRIMARY KEY,
    resource_reference text NOT NULL
        REFERENCES napms_resource_catalogue.resources(resource_reference),
    party_reference text NOT NULL,
    party_kind text NOT NULL,
    role text NOT NULL,
    display_name text NOT NULL,
    contact text NULL,
    valid_from timestamptz NOT NULL,
    valid_to timestamptz NULL,
    provenance_reference text NOT NULL,
    end_provenance_reference text NULL,
    version integer NOT NULL DEFAULT 1,
    CHECK (length(btrim(assignment_reference)) > 0),
    CHECK (length(btrim(party_reference)) > 0),
    CHECK (party_kind IN ('Person', 'Team')),
    CHECK (role IN ('ServiceOwner', 'TechnicalOwner', 'OperationsContact', 'BusinessOwner')),
    CHECK (length(btrim(display_name)) > 0),
    CHECK (contact IS NULL OR length(btrim(contact)) > 0),
    CHECK (length(btrim(provenance_reference)) > 0),
    CHECK (valid_from < valid_to OR valid_to IS NULL),
    CHECK (version >= 1),
    CHECK (
        end_provenance_reference IS NULL
        OR (
            valid_to IS NOT NULL
            AND length(btrim(end_provenance_reference)) > 0
        )
    )
);

CREATE INDEX IF NOT EXISTS ix_resource_responsibility_effective_lookup
ON napms_resource_catalogue.resource_responsibilities (
    resource_reference,
    valid_from,
    valid_to,
    role,
    party_reference
);

CREATE TABLE IF NOT EXISTS napms_resource_catalogue.curation_command_receipts (
    actor_id text NOT NULL,
    idempotency_key text NOT NULL,
    command_kind text NOT NULL,
    request_fingerprint text NOT NULL,
    result_reference text NOT NULL,
    result_version integer NOT NULL,
    PRIMARY KEY (actor_id, idempotency_key),
    CHECK (length(btrim(actor_id)) > 0),
    CHECK (length(btrim(idempotency_key)) > 0),
    CHECK (length(btrim(command_kind)) > 0),
    CHECK (length(btrim(request_fingerprint)) > 0),
    CHECK (length(btrim(result_reference)) > 0),
    CHECK (result_version >= 1)
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_rc_resource_display_name'
          AND connamespace = 'napms_resource_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_resource_catalogue.resources
        ADD CONSTRAINT ck_rc_resource_display_name
        CHECK (display_name IS NULL OR length(btrim(display_name)) > 0);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_rc_resource_lifecycle'
          AND connamespace = 'napms_resource_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_resource_catalogue.resources
        ADD CONSTRAINT ck_rc_resource_lifecycle
        CHECK (lifecycle_state IN ('Active', 'Retired'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_rc_resource_retirement_provenance'
          AND connamespace = 'napms_resource_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_resource_catalogue.resources
        ADD CONSTRAINT ck_rc_resource_retirement_provenance
        CHECK (
            (lifecycle_state = 'Active' AND retirement_provenance_reference IS NULL)
            OR
            (lifecycle_state = 'Retired'
             AND retirement_provenance_reference IS NOT NULL
             AND length(btrim(retirement_provenance_reference)) > 0)
        );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_rc_resource_version'
          AND connamespace = 'napms_resource_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_resource_catalogue.resources
        ADD CONSTRAINT ck_rc_resource_version CHECK (version >= 1);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_rc_realization_end_provenance'
          AND connamespace = 'napms_resource_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_resource_catalogue.resource_realization_versions
        ADD CONSTRAINT ck_rc_realization_end_provenance
        CHECK (
            end_provenance_reference IS NULL
            OR (valid_to IS NOT NULL AND length(btrim(end_provenance_reference)) > 0)
        );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_rc_realization_version'
          AND connamespace = 'napms_resource_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_resource_catalogue.resource_realization_versions
        ADD CONSTRAINT ck_rc_realization_version CHECK (version >= 1);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_rc_affiliation_end_provenance'
          AND connamespace = 'napms_resource_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_resource_catalogue.resource_scope_affiliations
        ADD CONSTRAINT ck_rc_affiliation_end_provenance
        CHECK (
            end_provenance_reference IS NULL
            OR (valid_to IS NOT NULL AND length(btrim(end_provenance_reference)) > 0)
        );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_rc_affiliation_version'
          AND connamespace = 'napms_resource_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_resource_catalogue.resource_scope_affiliations
        ADD CONSTRAINT ck_rc_affiliation_version CHECK (version >= 1);
    END IF;
END
$$;
