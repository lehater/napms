CREATE SCHEMA IF NOT EXISTS napms_network_enforcement_placement;

CREATE TABLE IF NOT EXISTS napms_network_enforcement_placement.knowledge_captures (
    capture_id uuid PRIMARY KEY,
    source_namespace text NOT NULL,
    source_reference text NOT NULL,
    source_capture_reference text NOT NULL,
    source_ip text NOT NULL,
    destination_ip text NOT NULL,
    valid_from timestamptz NOT NULL,
    valid_until timestamptz NULL,
    recorded_at timestamptz NOT NULL,
    payload jsonb NOT NULL,

    CONSTRAINT ck_nep_source_namespace_nonempty
        CHECK (length(btrim(source_namespace)) > 0),
    CONSTRAINT ck_nep_source_reference_nonempty
        CHECK (length(btrim(source_reference)) > 0),
    CONSTRAINT ck_nep_capture_reference_nonempty
        CHECK (length(btrim(source_capture_reference)) > 0),
    CONSTRAINT ck_nep_source_ip_nonempty
        CHECK (length(btrim(source_ip)) > 0),
    CONSTRAINT ck_nep_destination_ip_nonempty
        CHECK (length(btrim(destination_ip)) > 0),
    CONSTRAINT ck_nep_validity
        CHECK (
            valid_until IS NULL
            OR valid_from < valid_until
        ),
    CONSTRAINT ck_nep_payload_object
        CHECK (jsonb_typeof(payload) = 'object'),
    CONSTRAINT uq_nep_source_capture
        UNIQUE (
            source_namespace,
            source_reference,
            source_capture_reference
        )
);

CREATE INDEX IF NOT EXISTS ix_nep_relation_validity
ON napms_network_enforcement_placement.knowledge_captures (
    source_ip,
    destination_ip,
    valid_from,
    valid_until,
    capture_id
);

CREATE OR REPLACE FUNCTION napms_network_enforcement_placement.reject_capture_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'Network Enforcement Placement knowledge captures are immutable'
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_nep_capture_immutable
ON napms_network_enforcement_placement.knowledge_captures;

CREATE TRIGGER trg_nep_capture_immutable
BEFORE UPDATE OR DELETE
ON napms_network_enforcement_placement.knowledge_captures
FOR EACH ROW
EXECUTE FUNCTION napms_network_enforcement_placement.reject_capture_mutation();
