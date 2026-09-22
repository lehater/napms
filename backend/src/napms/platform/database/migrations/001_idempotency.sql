CREATE SCHEMA IF NOT EXISTS application_edge;

CREATE TABLE IF NOT EXISTS application_edge.idempotency_record (
    record_ref uuid NOT NULL PRIMARY KEY,
    principal_subject text NOT NULL,
    http_method text NOT NULL,
    route_template text NOT NULL,
    target_key text NOT NULL,
    idempotency_key text NOT NULL,
    request_fingerprint text NOT NULL,
    response_status integer NOT NULL,
    response_body_json_bytes bytea NOT NULL,
    location text NULL,
    response_etag text NULL,
    committed_at timestamptz NOT NULL,
    CONSTRAINT uq_idempotency_scope UNIQUE (
        principal_subject, http_method, route_template, target_key, idempotency_key
    )
);
