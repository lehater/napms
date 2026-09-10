ALTER TABLE napms_application_catalogue.applications
ADD COLUMN IF NOT EXISTS description text NULL;

ALTER TABLE napms_application_catalogue.applications
ADD COLUMN IF NOT EXISTS domain text NULL;

ALTER TABLE napms_application_catalogue.applications
ADD COLUMN IF NOT EXISTS owner_reference text NULL;

ALTER TABLE napms_application_catalogue.components
ADD COLUMN IF NOT EXISTS component_type text NULL;

ALTER TABLE napms_application_catalogue.components
ADD COLUMN IF NOT EXISTS description text NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_acc_application_target_metadata'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.applications
        ADD CONSTRAINT ck_acc_application_target_metadata
        CHECK (
            (description IS NULL OR length(btrim(description)) > 0)
            AND (domain IS NULL OR length(btrim(domain)) > 0)
            AND (owner_reference IS NULL OR length(btrim(owner_reference)) > 0)
        );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint
        WHERE conname = 'ck_acc_component_target_metadata'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.components
        ADD CONSTRAINT ck_acc_component_target_metadata
        CHECK (
            (component_type IS NULL OR length(btrim(component_type)) > 0)
            AND (description IS NULL OR length(btrim(description)) > 0)
        );
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS napms_application_catalogue.interaction_definitions (
    interaction_definition_id uuid PRIMARY KEY,
    application_id uuid NOT NULL
        REFERENCES napms_application_catalogue.applications(application_id),
    source_component_id uuid NOT NULL
        REFERENCES napms_application_catalogue.components(component_id),
    destination_component_id uuid NOT NULL
        REFERENCES napms_application_catalogue.components(component_id),
    traffic_payload bytea NOT NULL,
    provenance_reference text NOT NULL,
    lifecycle_state text NOT NULL DEFAULT 'Active',
    retirement_provenance_reference text NULL,
    version integer NOT NULL DEFAULT 1,
    CHECK (octet_length(traffic_payload) > 0),
    CHECK (length(btrim(provenance_reference)) > 0),
    CHECK (lifecycle_state IN ('Active', 'Retired')),
    CHECK (version >= 1),
    CHECK (
        (lifecycle_state = 'Active' AND retirement_provenance_reference IS NULL)
        OR
        (lifecycle_state = 'Retired'
         AND retirement_provenance_reference IS NOT NULL
         AND length(btrim(retirement_provenance_reference)) > 0)
    )
);

CREATE INDEX IF NOT EXISTS ix_acc_interaction_definitions_application
ON napms_application_catalogue.interaction_definitions (
    application_id,
    lifecycle_state,
    source_component_id,
    destination_component_id,
    interaction_definition_id
);

CREATE INDEX IF NOT EXISTS ix_acc_interaction_definitions_source
ON napms_application_catalogue.interaction_definitions (
    source_component_id,
    lifecycle_state,
    interaction_definition_id
);

CREATE INDEX IF NOT EXISTS ix_acc_interaction_definitions_destination
ON napms_application_catalogue.interaction_definitions (
    destination_component_id,
    lifecycle_state,
    interaction_definition_id
);

CREATE TABLE IF NOT EXISTS napms_application_catalogue.application_deployments (
    application_deployment_id uuid PRIMARY KEY,
    application_id uuid NOT NULL
        REFERENCES napms_application_catalogue.applications(application_id),
    company_reference text NOT NULL,
    environment text NOT NULL,
    scope_reference text NOT NULL,
    provenance_reference text NOT NULL,
    lifecycle_state text NOT NULL DEFAULT 'Active',
    retirement_provenance_reference text NULL,
    version integer NOT NULL DEFAULT 1,
    CHECK (length(btrim(company_reference)) > 0),
    CHECK (length(btrim(environment)) > 0),
    CHECK (length(btrim(scope_reference)) > 0),
    CHECK (length(btrim(provenance_reference)) > 0),
    CHECK (lifecycle_state IN ('Active', 'Retired')),
    CHECK (version >= 1),
    CHECK (
        (lifecycle_state = 'Active' AND retirement_provenance_reference IS NULL)
        OR
        (lifecycle_state = 'Retired'
         AND retirement_provenance_reference IS NOT NULL
         AND length(btrim(retirement_provenance_reference)) > 0)
    )
);

CREATE INDEX IF NOT EXISTS ix_acc_application_deployments_application
ON napms_application_catalogue.application_deployments (
    application_id,
    lifecycle_state,
    company_reference,
    environment,
    scope_reference,
    application_deployment_id
);

CREATE TABLE IF NOT EXISTS napms_application_catalogue.deployment_interactions (
    deployment_interaction_id uuid PRIMARY KEY,
    application_deployment_id uuid NOT NULL
        REFERENCES napms_application_catalogue.application_deployments(application_deployment_id),
    interaction_definition_id uuid NOT NULL
        REFERENCES napms_application_catalogue.interaction_definitions(interaction_definition_id),
    provenance_reference text NOT NULL,
    lifecycle_state text NOT NULL DEFAULT 'Active',
    retirement_provenance_reference text NULL,
    version integer NOT NULL DEFAULT 1,
    CHECK (length(btrim(provenance_reference)) > 0),
    CHECK (lifecycle_state IN ('Active', 'Retired')),
    CHECK (version >= 1),
    CHECK (
        (lifecycle_state = 'Active' AND retirement_provenance_reference IS NULL)
        OR
        (lifecycle_state = 'Retired'
         AND retirement_provenance_reference IS NOT NULL
         AND length(btrim(retirement_provenance_reference)) > 0)
    )
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_acc_active_deployment_interaction_definition
ON napms_application_catalogue.deployment_interactions (
    application_deployment_id,
    interaction_definition_id
)
WHERE lifecycle_state = 'Active';

CREATE INDEX IF NOT EXISTS ix_acc_deployment_interactions_definition
ON napms_application_catalogue.deployment_interactions (
    interaction_definition_id,
    lifecycle_state,
    deployment_interaction_id
);

CREATE TABLE IF NOT EXISTS napms_application_catalogue.deployment_interaction_compatibility_sides (
    deployment_interaction_id uuid NOT NULL
        REFERENCES napms_application_catalogue.deployment_interactions(deployment_interaction_id),
    side text NOT NULL,
    component_deployment_id uuid NOT NULL UNIQUE
        REFERENCES napms_application_catalogue.component_deployments(component_deployment_id),
    PRIMARY KEY (deployment_interaction_id, side),
    CHECK (side IN ('Source', 'Destination'))
);

CREATE TABLE IF NOT EXISTS napms_application_catalogue.deployment_interaction_compatibility (
    deployment_interaction_id uuid PRIMARY KEY
        REFERENCES napms_application_catalogue.deployment_interactions(deployment_interaction_id),
    current_dcs_revision_id uuid NOT NULL
        REFERENCES napms_application_catalogue.dcs_revisions(revision_id),
    version integer NOT NULL DEFAULT 1,
    CHECK (version >= 1)
);

CREATE INDEX IF NOT EXISTS ix_acc_compatibility_current_dcs
ON napms_application_catalogue.deployment_interaction_compatibility (
    current_dcs_revision_id,
    deployment_interaction_id
);
