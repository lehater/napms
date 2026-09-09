import os
import re
import subprocess
import sys
import time


_SAFE_PASSWORD = re.compile(r"^[A-Za-z0-9_-]+$")


def compose(*args: str, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["docker", "compose", *args],
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=check,
    )


def wait_postgres_ready() -> None:
    for _ in range(60):
        result = compose(
            "exec",
            "-T",
            "postgres",
            "pg_isready",
            "-U",
            "napms",
            "-d",
            "napms",
            check=False,
        )
        if result.returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("local PostgreSQL did not become ready")


def main() -> int:
    password = os.environ.get("NAPMS_POSTGRES_PASSWORD", "")
    if not password:
        print("NAPMS_POSTGRES_PASSWORD is required", file=sys.stderr)
        return 2
    if not _SAFE_PASSWORD.fullmatch(password):
        print(
            "NAPMS_POSTGRES_PASSWORD must contain only URL-safe alphanumeric, '-' or '_' characters for the supported local helper path",
            file=sys.stderr,
        )
        return 2

    compose("up", "--detach", "postgres")
    wait_postgres_ready()

    sql = f"ALTER ROLE napms PASSWORD '{password}'"
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
            "-c",
            sql,
        ],
        env=os.environ.copy(),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        print(
            "could not rotate the local napms PostgreSQL role password through the container-local database socket",
            file=sys.stderr,
        )
        return 1

    print("Local PostgreSQL credential prepared")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"NAPMS local PostgreSQL preparation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
