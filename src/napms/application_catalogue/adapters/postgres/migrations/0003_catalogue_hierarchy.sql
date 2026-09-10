CREATE TABLE IF NOT EXISTS napms_application_catalogue.applications (
    application_id uuid PRIMARY KEY,
    display_name text NOT NULL,
    provenance_reference text NOT NULL,
    lifecycle_state text NOT NULL DEFAULT 'Active',
    retirement_provenance_reference text NULL,
    version integer NOT NULL DEFAULT 1,
    CHECK (length(btrim(display_name)) > 0),
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

CREATE TABLE IF NOT EXISTS napms_application_catalogue.components (
    component_id uuid PRIMARY KEY,
    application_id uuid NOT NULL
        REFERENCES napms_application_catalogue.applications(application_id),
    display_name text NOT NULL,
    provenance_reference text NOT NULL,
    lifecycle_state text NOT NULL DEFAULT 'Active',
    retirement_provenance_reference text NULL,
    version integer NOT NULL DEFAULT 1,
    CHECK (length(btrim(display_name)) > 0),
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

-- Stable repository-defined identity for the conservative legacy parent.
-- It is inserted only when legacy deployments actually exist.
INSERT INTO napms_application_catalogue.applications (
    application_id,
    display_name,
    provenance_reference,
    lifecycle_state,
    version
)
SELECT
    '506918c2-afff-018a-d9e2-900b43852c1e'::uuid,
    'Imported catalogue',
    'migration:i27:application-catalogue-hierarchy',
    'Active',
    1
WHERE EXISTS (
    SELECT 1 FROM napms_application_catalogue.component_deployments
)
ON CONFLICT (application_id) DO NOTHING;

-- One deterministic compatibility Component per pre-I27 deployment. Equal display
-- names are deliberately not grouped because display metadata is not identity evidence.
INSERT INTO napms_application_catalogue.components (
    component_id,
    application_id,
    display_name,
    provenance_reference,
    lifecycle_state,
    version
)
SELECT
    (
        substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 1, 8) || '-' ||
        substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 9, 4) || '-' ||
        substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 13, 4) || '-' ||
        substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 17, 4) || '-' ||
        substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 21, 12)
    )::uuid,
    '506918c2-afff-018a-d9e2-900b43852c1e'::uuid,
    COALESCE(NULLIF(btrim(d.display_name), ''), d.component_deployment_id::text),
    'migration:i27:compat-component:' || d.component_deployment_id::text,
    'Active',
    1
FROM napms_application_catalogue.component_deployments AS d
ON CONFLICT (component_id) DO NOTHING;

ALTER TABLE napms_application_catalogue.component_deployments
ADD COLUMN IF NOT EXISTS component_id uuid NULL;

UPDATE napms_application_catalogue.component_deployments AS d
SET component_id = (
    substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 1, 8) || '-' ||
    substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 9, 4) || '-' ||
    substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 13, 4) || '-' ||
    substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 17, 4) || '-' ||
    substr(md5('napms:i27:compat-component:' || d.component_deployment_id::text), 21, 12)
)::uuid
WHERE d.component_id IS NULL;

ALTER TABLE napms_application_catalogue.component_deployments
ADD COLUMN IF NOT EXISTS lifecycle_state text NOT NULL DEFAULT 'Active';

ALTER TABLE napms_application_catalogue.component_deployments
ADD COLUMN IF NOT EXISTS retirement_provenance_reference text NULL;

ALTER TABLE napms_application_catalogue.component_deployments
ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1;

ALTER TABLE napms_application_catalogue.component_deployments
ALTER COLUMN component_id SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'fk_acc_component_deployment_component'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.component_deployments
        ADD CONSTRAINT fk_acc_component_deployment_component
        FOREIGN KEY (component_id)
        REFERENCES napms_application_catalogue.components(component_id);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ck_acc_component_deployment_lifecycle'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.component_deployments
        ADD CONSTRAINT ck_acc_component_deployment_lifecycle
        CHECK (lifecycle_state IN ('Active', 'Retired'));
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ck_acc_component_deployment_version'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.component_deployments
        ADD CONSTRAINT ck_acc_component_deployment_version
        CHECK (version >= 1);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ck_acc_component_deployment_retirement_provenance'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.component_deployments
        ADD CONSTRAINT ck_acc_component_deployment_retirement_provenance
        CHECK (
            (lifecycle_state = 'Active' AND retirement_provenance_reference IS NULL)
            OR
            (lifecycle_state = 'Retired'
             AND retirement_provenance_reference IS NOT NULL
             AND length(btrim(retirement_provenance_reference)) > 0)
        );
    END IF;
END
$$;

CREATE INDEX IF NOT EXISTS ix_acc_components_application
ON napms_application_catalogue.components (
    application_id,
    lifecycle_state,
    display_name,
    component_id
);

CREATE INDEX IF NOT EXISTS ix_acc_deployments_component
ON napms_application_catalogue.component_deployments (
    component_id,
    lifecycle_state,
    component_deployment_id
);
