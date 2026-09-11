ALTER TABLE napms_application_catalogue.component_deployments
ADD COLUMN IF NOT EXISTS display_name text NULL;

ALTER TABLE napms_application_catalogue.dcs_revisions
ADD COLUMN IF NOT EXISTS display_name text NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ck_acc_component_deployment_display_name'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.component_deployments
        ADD CONSTRAINT ck_acc_component_deployment_display_name
        CHECK (display_name IS NULL OR length(btrim(display_name)) > 0);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ck_acc_dcs_revision_display_name'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.dcs_revisions
        ADD CONSTRAINT ck_acc_dcs_revision_display_name
        CHECK (display_name IS NULL OR length(btrim(display_name)) > 0);
    END IF;
END
$$;
