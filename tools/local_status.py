import json
import os
import subprocess
import sys
import urllib.error
import urllib.request


def compose_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("NAPMS_POSTGRES_PASSWORD", "local-status-placeholder")
    return env


def run_compose_ps() -> None:
    subprocess.run(
        ["docker", "compose", "ps"],
        env=compose_env(),
        check=True,
    )


def check_http(url: str, expected_status: str) -> None:
    with urllib.request.urlopen(url, timeout=3) as response:
        if response.status != 200:
            raise RuntimeError(f"{url} returned HTTP {response.status}")
        payload = json.load(response)
        if payload.get("status") != expected_status:
            raise RuntimeError(f"{url} returned unexpected status payload: {payload}")


def check_postgres() -> None:
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "postgres",
            "psql",
            "-U",
            "napms",
            "-d",
            "napms",
            "--set=ON_ERROR_STOP=1",
            "-Atc",
            "SELECT 1",
        ],
        env=compose_env(),
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        check=False,
    )
    if result.returncode != 0 or result.stdout.strip() != "1":
        raise RuntimeError("local PostgreSQL query probe failed")


def main() -> int:
    port = os.environ.get("NAPMS_WEB_PORT", "8080")
    base_url = f"http://127.0.0.1:{port}"

    run_compose_ps()
    check_http(f"{base_url}/health/live", "Live")
    check_http(f"{base_url}/health/ready", "Ready")
    check_postgres()

    print(f"NAPMS local status OK: {base_url} live, ready, PostgreSQL queryable")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        RuntimeError,
        subprocess.CalledProcessError,
        urllib.error.URLError,
        TimeoutError,
        ValueError,
    ) as exc:
        print(f"NAPMS local status failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
