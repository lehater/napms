CREATE SCHEMA IF NOT EXISTS napms_technical;

CREATE TABLE IF NOT EXISTS napms_technical.idempotency (
    principal text NOT NULL,
    method text NOT NULL,
    route text NOT NULL,
    target text NOT NULL,
    idempotency_key text NOT NULL,
    request_fingerprint text NOT NULL,
    status_code integer NOT NULL,
    response_body jsonb NOT NULL,
    location text NULL,
    etag text NULL,
    created_at timestamptz NOT NULL DEFAULT transaction_timestamp(),
    PRIMARY KEY (principal, method, route, target, idempotency_key)
);
