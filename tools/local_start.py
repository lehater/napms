import argparse
import json
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request


def compose(*args: str, env=None, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["docker", "compose", *args], env=env, check=check)


def wait_ready(base_url: str) -> None:
    last_error = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"{base_url}/health/ready", timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"NAPMS public readiness did not become healthy: {last_error}")


def wait_oidc(oidc_url: str) -> None:
    context = ssl._create_unverified_context()
    last_error = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(f"{oidc_url}/health", context=context, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"NAPMS test OIDC issuer did not become healthy: {last_error}")


def issue_local_token(oidc_url: str) -> str:
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(f"{oidc_url}/token?profile=full", context=context, timeout=5) as response:
        payload = json.load(response)
    return payload["access_token"]


def read_only_smoke(*, base_url: str, token: str) -> None:
    request = urllib.request.Request(
        f"{base_url}/v1/resources?page=1&pageSize=1",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError("OIDC authenticated read probe failed")
        payload = json.load(response)
        if "items" not in payload:
            raise RuntimeError("authenticated read response is malformed")


def up(*, print_credentials: bool = True) -> None:
    if not os.environ.get("NAPMS_POSTGRES_PASSWORD"):
        raise RuntimeError("NAPMS_POSTGRES_PASSWORD is required")

    port = os.environ.get("NAPMS_WEB_PORT", "8080")
    oidc_port = os.environ.get("NAPMS_OIDC_PORT", "8443")
    base_url = f"http://127.0.0.1:{port}"
    oidc_url = f"https://127.0.0.1:{oidc_port}"
    env = os.environ.copy()

    try:
        compose("up", "--build", "--detach", "oidc", env=env)
        wait_oidc(oidc_url)
        token = issue_local_token(oidc_url)
        compose("up", "--build", "--detach", "--remove-orphans", env=env)
        wait_ready(base_url)
        read_only_smoke(base_url=base_url, token=token)
    except Exception:
        compose("ps", env=env, check=False)
        raise

    print(f"NAPMS ready: {base_url}")
    if print_credentials:
        print("Authentication: OIDC-backed; startup probe used an ephemeral signed bearer token.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("up",))
    parser.add_argument("--no-print-credentials", action="store_true")
    args = parser.parse_args()
    if args.action == "up":
        up(print_credentials=not args.no_print_credentials)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, urllib.error.URLError) as exc:
        print(f"NAPMS local startup failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
