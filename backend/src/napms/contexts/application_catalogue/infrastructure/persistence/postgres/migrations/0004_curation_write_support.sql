ALTER TABLE napms_application_catalogue.deployment_resource_bindings
ADD COLUMN IF NOT EXISTS end_provenance_reference text NULL;

ALTER TABLE napms_application_catalogue.deployment_resource_bindings
ADD COLUMN IF NOT EXISTS version integer NOT NULL DEFAULT 1;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ck_acc_binding_version'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.deployment_resource_bindings
        ADD CONSTRAINT ck_acc_binding_version
        CHECK (version >= 1);
    END IF;

    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'ck_acc_binding_end_provenance'
          AND connamespace = 'napms_application_catalogue'::regnamespace
    ) THEN
        ALTER TABLE napms_application_catalogue.deployment_resource_bindings
        ADD CONSTRAINT ck_acc_binding_end_provenance
        CHECK (
            end_provenance_reference IS NULL
            OR (
                valid_to IS NOT NULL
                AND length(btrim(end_provenance_reference)) > 0
            )
        );
    END IF;
END
$$;

CREATE TABLE IF NOT EXISTS napms_application_catalogue.curation_command_receipts (
    actor_id text NOT NULL,
    idempotency_key text NOT NULL,
    command_kind text NOT NULL,
    request_fingerprint text NOT NULL,
    result_uuid uuid NULL,
    result_reference text NULL,
    result_version integer NOT NULL,
    PRIMARY KEY (actor_id, idempotency_key),
    CHECK (length(btrim(actor_id)) > 0),
    CHECK (length(btrim(idempotency_key)) > 0),
    CHECK (length(btrim(command_kind)) > 0),
    CHECK (length(btrim(request_fingerprint)) > 0),
    CHECK (result_version >= 1),
    CHECK (
        (result_uuid IS NOT NULL AND result_reference IS NULL)
        OR
        (result_uuid IS NULL
         AND result_reference IS NOT NULL
         AND length(btrim(result_reference)) > 0)
    )
);
