from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any

import psycopg


class IdempotencyConflict(Exception):
    pass


@dataclass(frozen=True)
class PersistedHttpResponse:
    status_code: int
    body: dict[str, object]
    location: str | None
    etag: str | None


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
                SELECT request_fingerprint, status_code, response_body, location, etag
                FROM napms_technical.idempotency
                WHERE principal = %s AND method = %s AND route = %s
                  AND target = %s AND idempotency_key = %s
                """,
                (principal, method, route, target, key),
            ).fetchone()
        if row is None:
            return None
        if row[0] != fingerprint:
            raise IdempotencyConflict(key)
        return PersistedHttpResponse(
            status_code=row[1],
            body=row[2],
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
        with psycopg.connect(self._dsn) as connection:
            row = connection.execute(
                """
                INSERT INTO napms_technical.idempotency (
                    principal, method, route, target, idempotency_key,
                    request_fingerprint, status_code, response_body, location, etag
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                ON CONFLICT (principal, method, route, target, idempotency_key)
                DO NOTHING
                RETURNING status_code
                """,
                (
                    principal,
                    method,
                    route,
                    target,
                    key,
                    fingerprint,
                    response.status_code,
                    json.dumps(response.body, sort_keys=True),
                    response.location,
                    response.etag,
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
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()
    return hashlib.sha256(encoded).hexdigest()
