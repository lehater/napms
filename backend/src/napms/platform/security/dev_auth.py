from __future__ import annotations

import hmac
import json
import urllib.request
from dataclasses import dataclass
from typing import Protocol


class DevelopmentAuthUnavailable(RuntimeError):
    pass


class DevelopmentTokenIssuer(Protocol):
    def issue(self, *, login: str, password: str) -> str | None: ...


@dataclass(frozen=True)
class LocalDevelopmentTokenIssuer:
    oidc_issuer: str
    timeout_seconds: float = 5.0

    def issue(self, *, login: str, password: str) -> str | None:
        if not (
            hmac.compare_digest(login, "admin")
            and hmac.compare_digest(password, "admin")
        ):
            return None

        token_url = f"{self.oidc_issuer.rstrip('/')}/token?profile=full"
        try:
            with urllib.request.urlopen(token_url, timeout=self.timeout_seconds) as response:
                payload = json.load(response)
        except (OSError, ValueError) as exc:
            raise DevelopmentAuthUnavailable(
                "local development token issuer is unavailable"
            ) from exc

        if not isinstance(payload, dict):
            raise DevelopmentAuthUnavailable(
                "local development token response is malformed"
            )
        token = payload.get("access_token")
        if not isinstance(token, str) or not token.strip():
            raise DevelopmentAuthUnavailable(
                "local development token response has no access token"
            )
        return token
