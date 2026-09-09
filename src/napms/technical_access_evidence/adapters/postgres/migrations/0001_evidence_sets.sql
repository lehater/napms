CREATE SCHEMA IF NOT EXISTS napms_technical_access_evidence;

CREATE TABLE IF NOT EXISTS napms_technical_access_evidence.evidence_sets (
    evidence_set_id uuid PRIMARY KEY,
    kind text NOT NULL,
    source_namespace text NOT NULL,
    source_reference text NOT NULL,
    source_scope_reference text NOT NULL,
    source_capture_reference text NOT NULL,
    evidence_time_kind text NOT NULL,
    evidence_time_at timestamptz NULL,
    evidence_time_start timestamptz NULL,
    evidence_time_end timestamptz NULL,
    recorded_at timestamptz NOT NULL,
    entries jsonb NOT NULL DEFAULT '[]'::jsonb,

    CONSTRAINT ck_tae_kind
        CHECK (kind IN ('Configured', 'TrafficDerived', 'Imported')),
    CONSTRAINT ck_tae_source_namespace_nonempty
        CHECK (length(btrim(source_namespace)) > 0),
    CONSTRAINT ck_tae_source_reference_nonempty
        CHECK (length(btrim(source_reference)) > 0),
    CONSTRAINT ck_tae_source_scope_nonempty
        CHECK (length(btrim(source_scope_reference)) > 0),
    CONSTRAINT ck_tae_capture_reference_nonempty
        CHECK (length(btrim(source_capture_reference)) > 0),
    CONSTRAINT ck_tae_evidence_time_kind
        CHECK (evidence_time_kind IN ('Unknown', 'Instant', 'Window')),
    CONSTRAINT ck_tae_evidence_time_shape
        CHECK (
            (
                evidence_time_kind = 'Unknown'
                AND evidence_time_at IS NULL
                AND evidence_time_start IS NULL
                AND evidence_time_end IS NULL
            )
            OR (
                evidence_time_kind = 'Instant'
                AND evidence_time_at IS NOT NULL
                AND evidence_time_start IS NULL
                AND evidence_time_end IS NULL
            )
            OR (
                evidence_time_kind = 'Window'
                AND evidence_time_at IS NULL
                AND evidence_time_start IS NOT NULL
                AND evidence_time_end IS NOT NULL
                AND evidence_time_start < evidence_time_end
            )
        ),
    CONSTRAINT ck_tae_entries_array
        CHECK (jsonb_typeof(entries) = 'array'),
    CONSTRAINT uq_tae_source_capture
        UNIQUE (
            source_namespace,
            source_reference,
            source_capture_reference
        )
);

CREATE INDEX IF NOT EXISTS ix_tae_source_scope_recorded
ON napms_technical_access_evidence.evidence_sets (
    source_namespace,
    source_reference,
    source_scope_reference,
    recorded_at DESC,
    evidence_set_id
);

CREATE INDEX IF NOT EXISTS ix_tae_kind_recorded
ON napms_technical_access_evidence.evidence_sets (
    kind,
    recorded_at DESC,
    evidence_set_id
);

CREATE OR REPLACE FUNCTION napms_technical_access_evidence.reject_evidence_mutation()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'Technical Access Evidence records are immutable'
        USING ERRCODE = '55000';
END;
$$;

DROP TRIGGER IF EXISTS trg_tae_evidence_set_immutable
ON napms_technical_access_evidence.evidence_sets;

CREATE TRIGGER trg_tae_evidence_set_immutable
BEFORE UPDATE OR DELETE
ON napms_technical_access_evidence.evidence_sets
FOR EACH ROW
EXECUTE FUNCTION napms_technical_access_evidence.reject_evidence_mutation();
