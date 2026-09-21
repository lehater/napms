from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from uuid import uuid4

import psycopg


class IdempotencyConflict(Exception):
    pass


@dataclass(frozen=True)
class PersistedHttpResponse:
    status_code: int
    body: dict[str, object]
    location: str | None = None
    etag: str | None = None


class PostgresIdempotencyStore:
    def __init__(self, *, dsn: str) -> None:
        self._dsn = dsn

    def lookup(
        self,
        *,
        principal: str,
        method: str,
        route: str,
        target: str,
        key: str,
        payload: dict[str, object],
    ) -> PersistedHttpResponse | None:
        fingerprint = _fingerprint(payload)
        with psycopg.connect(self._dsn) as connection:
            row = connection.execute(
                """
                SELECT request_fingerprint, response_status,
                       response_body_json_bytes, location, response_etag
                FROM application_edge.idempotency_record
                WHERE principal_subject = %s AND http_method = %s
                  AND route_template = %s AND target_key = %s
                  AND idempotency_key = %s
                """,
                (principal, method, route, target, key),
            ).fetchone()
        if row is None:
            return None
        if row[0] != fingerprint:
            raise IdempotencyConflict(key)
        return PersistedHttpResponse(
            status_code=row[1],
            body=json.loads(bytes(row[2]).decode()),
            location=row[3],
            etag=row[4],
        )

    def record(
        self,
        *,
        principal: str,
        method: str,
        route: str,
        target: str,
        key: str,
        payload: dict[str, object],
        response: PersistedHttpResponse,
    ) -> PersistedHttpResponse:
        fingerprint = _fingerprint(payload)
        body = json.dumps(
            response.body, sort_keys=True, separators=(",", ":")
        ).encode()
        with psycopg.connect(self._dsn) as connection:
            row = connection.execute(
                """
                INSERT INTO application_edge.idempotency_record (
                    record_ref, principal_subject, http_method, route_template,
                    target_key, idempotency_key, request_fingerprint,
                    response_status, response_body_json_bytes, location,
                    response_etag, committed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (
                    principal_subject, http_method, route_template,
                    target_key, idempotency_key
                ) DO NOTHING
                RETURNING record_ref
                """,
                (
                    uuid4(),
                    principal,
                    method,
                    route,
                    target,
                    key,
                    fingerprint,
                    response.status_code,
                    body,
                    response.location,
                    response.etag,
                    datetime.now(timezone.utc),
                ),
            ).fetchone()
            if row is not None:
                return response
        replay = self.lookup(
            principal=principal,
            method=method,
            route=route,
            target=target,
            key=key,
            payload=payload,
        )
        assert replay is not None
        return replay


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), default=str
    ).encode()
    return hashlib.sha256(encoded).hexdigest()
