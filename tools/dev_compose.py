import argparse
import base64
import hashlib
import http.cookiejar
import json
import os
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.request


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return "$".join(
        (
            "scrypt-v1",
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        )
    )


def compose(*args: str, env=None, check: bool = True):
    return subprocess.run(
        ["docker", "compose", *args],
        env=env,
        check=check,
    )


def wait_ready(base_url: str) -> None:
    last_error = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(
                f"{base_url}/health/ready",
                timeout=2,
            ) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"NAPMS public readiness did not become healthy: {last_error}")


def authenticated_smoke(
    *,
    base_url: str,
    login: str,
    password: str,
) -> None:
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )

    request = urllib.request.Request(
        f"{base_url}/api/v1/session",
        method="POST",
        data=json.dumps(
            {"login": login, "password": password}
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(request, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError("local login smoke failed")

    with opener.open(f"{base_url}/api/v1/session", timeout=5) as response:
        payload = json.load(response)
        if payload["actor"]["login"] != login:
            raise RuntimeError("authenticated session actor mismatch")

    with opener.open(
        f"{base_url}/api/v1/access-rule-proposals/scopes",
        timeout=5,
    ) as response:
        payload = json.load(response)
        scopes = {item["scope"] for item in payload["scopes"]}
        if "local-demo" not in scopes:
            raise RuntimeError("local demo authority seed is unavailable")


def up(*, print_credentials: bool = True) -> None:
    login = os.environ.get("NAPMS_LOCAL_AUTH_LOGIN", "local-admin")
    actor_id = os.environ.get("NAPMS_LOCAL_AUTH_ACTOR_ID", login)
    password = secrets.token_urlsafe(15)
    password_hash = hash_password(password)
    port = os.environ.get("NAPMS_WEB_PORT", "8080")
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env.update(
        {
            "NAPMS_LOCAL_AUTH_LOGIN": login,
            "NAPMS_LOCAL_AUTH_ACTOR_ID": actor_id,
            "NAPMS_LOCAL_AUTH_PASSWORD_HASH": password_hash,
        }
    )

    try:
        compose("up", "--build", "--detach", "--remove-orphans", env=env)
        wait_ready(base_url)
        authenticated_smoke(
            base_url=base_url,
            login=login,
            password=password,
        )
    except Exception:
        compose("ps", env=env, check=False)
        raise

    print(f"NAPMS ready: {base_url}")
    if print_credentials:
        print(f"Login: {login}")
        print(f"Password: {password}")
        print("Password was generated for this run and was not written to disk.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("up",))
    parser.add_argument(
        "--no-print-credentials",
        action="store_true",
        help="run authenticated smoke without printing generated credentials",
    )
    args = parser.parse_args()

    if args.action == "up":
        up(print_credentials=not args.no_print_credentials)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, urllib.error.URLError) as exc:
        print(f"NAPMS local startup failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
