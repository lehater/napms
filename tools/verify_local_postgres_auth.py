import os
import subprocess
import sys


def psql_with_password(password: str) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    return subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "-e",
            "PGPASSWORD",
            "postgres",
            "psql",
            "-h",
            "127.0.0.1",
            "-U",
            "napms",
            "-d",
            "napms",
            "-c",
            "SELECT 1",
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def main() -> int:
    password = os.environ.get("NAPMS_POSTGRES_PASSWORD")
    if not password:
        print(
            "NAPMS_POSTGRES_PASSWORD is required for local PostgreSQL verification",
            file=sys.stderr,
        )
        return 2

    accepted = psql_with_password(password)
    if accepted.returncode != 0:
        print(
            "local PostgreSQL rejected the configured password",
            file=sys.stderr,
        )
        return 1

    rejected = psql_with_password("napms-deliberately-wrong-password")
    if rejected.returncode == 0:
        print(
            "local PostgreSQL accepted an invalid password; the volume may still use legacy trust authentication. "
            "Back up required data and recreate or migrate the local PostgreSQL volume before continuing.",
            file=sys.stderr,
        )
        return 1

    print("Local PostgreSQL password authentication verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
