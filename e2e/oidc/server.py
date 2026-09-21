from __future__ import annotations

from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import ipaddress
import json
import os
from pathlib import Path
import ssl
from urllib.parse import parse_qs, urlparse

import jwt
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

ISSUER = os.environ.get("NAPMS_TEST_OIDC_ISSUER", "https://oidc:8443").rstrip("/")
AUDIENCE = os.environ.get("NAPMS_TEST_OIDC_AUDIENCE", "napms-e2e")
KEY_ID = "napms-e2e-key-1"
MATERIAL = Path("/material")
MATERIAL.mkdir(parents=True, exist_ok=True)

TLS_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
SIGNING_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "napms-e2e-oidc")])
now = datetime.now(timezone.utc)
certificate = (
    x509.CertificateBuilder()
    .subject_name(name)
    .issuer_name(name)
    .public_key(TLS_KEY.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(now - timedelta(minutes=5))
    .not_valid_after(now + timedelta(days=2))
    .add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("oidc"),
            x509.DNSName("localhost"),
            x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
        ]),
        critical=False,
    )
    .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
    .sign(TLS_KEY, hashes.SHA256())
)
TLS_KEY_PATH = Path("/tmp/napms-e2e-oidc-tls.key")
TLS_KEY_PATH.write_bytes(
    TLS_KEY.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
)
(MATERIAL / "tls.crt").write_bytes(certificate.public_bytes(serialization.Encoding.PEM))
PUBLIC_JWK = jwt.algorithms.RSAAlgorithm.to_jwk(SIGNING_KEY.public_key(), as_dict=True)
PUBLIC_JWK.update({"kid": KEY_ID, "use": "sig", "alg": "RS256"})
ALL_PERMISSIONS = [
    "resource.read", "resource.write", "application.read", "application.write",
    "deployment.read", "deployment.write", "business.read", "business.write",
    "access.decide", "access.manage", "policy.read",
]


def issue(profile: str) -> str:
    permissions = [] if profile == "restricted" else ALL_PERMISSIONS
    authority = [] if profile == "restricted" else [
        {"action": "access.request", "scope": "*"},
        {"action": "policy.export", "scope": "*"},
    ]
    expiry = (
        datetime.now(timezone.utc) - timedelta(minutes=1)
        if profile == "expired"
        else datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    return jwt.encode(
        {
            "iss": ISSUER,
            "aud": AUDIENCE,
            "sub": "subject:e2e",
            "exp": expiry,
            "permissions": permissions,
            "authority": authority,
        },
        SIGNING_KEY,
        algorithm="RS256",
        headers={"kid": KEY_ID},
    )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/.well-known/openid-configuration":
            self._json({"issuer": ISSUER, "jwks_uri": f"{ISSUER}/jwks"})
            return
        if parsed.path == "/jwks":
            self._json({"keys": [PUBLIC_JWK]})
            return
        if parsed.path == "/health":
            self._json({"status": "ok"})
            return
        if parsed.path == "/token":
            profile = parse_qs(parsed.query).get("profile", ["full"])[0]
            if profile not in {"full", "restricted", "expired"}:
                self.send_error(400)
                return
            self._json({"access_token": issue(profile), "token_type": "Bearer"})
            return
        self.send_error(404)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _json(self, payload: dict) -> None:
        body = json.dumps(payload, separators=(",", ":")).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


server = ThreadingHTTPServer(("0.0.0.0", 8443), Handler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(MATERIAL / "tls.crt", TLS_KEY_PATH)
server.socket = context.wrap_socket(server.socket, server_side=True)
server.serve_forever()
