import argparse
import os
from pathlib import Path
import secrets
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
POSTGRES_IMAGE = "postgres:16-alpine"


def compose_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("NAPMS_POSTGRES_PASSWORD", "local-operator-placeholder")
    return env


def compose(*args: str, env=None, stdin=None, stdout=None) -> None:
    subprocess.run(
        ["docker", "compose", *args],
        cwd=ROOT,
        env=env or compose_env(),
        stdin=stdin,
        stdout=stdout,
        check=True,
    )


def validate_backup(path: Path) -> None:
    path = path.resolve()
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"backup is missing or empty: {path}")

    subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{path.parent}:/backup:ro",
            POSTGRES_IMAGE,
            "pg_restore",
            "--list",
            f"/backup/{path.name}",
        ],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )


def backup(path: Path) -> None:
    path = path.resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    if temporary.exists():
        temporary.unlink()

    try:
        with temporary.open("wb") as output:
            compose(
                "exec",
                "-T",
                "postgres",
                "pg_dump",
                "-U",
                "napms",
                "-d",
                "napms",
                "--format=custom",
                "--no-owner",
                "--no-acl",
                stdout=output,
            )
        validate_backup(temporary)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()

    print(f"Local PostgreSQL backup written: {path}")


def restore_clean(path: Path, *, confirm_reset: bool, print_credentials: bool) -> None:
    path = path.resolve()
    validate_backup(path)
    if not confirm_reset:
        raise RuntimeError(
            "restore replaces the local PostgreSQL volume; rerun with --confirm-reset after verifying the backup path"
        )

    env = os.environ.copy()
    env["NAPMS_POSTGRES_PASSWORD"] = secrets.token_urlsafe(24)

    compose("down", "--volumes", "--remove-orphans", env=env)
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "prepare_local_postgres.py")],
        cwd=ROOT,
        env=env,
        check=True,
    )

    with path.open("rb") as archive:
        compose(
            "exec",
            "-T",
            "postgres",
            "pg_restore",
            "-U",
            "napms",
            "-d",
            "napms",
            "--no-owner",
            "--no-acl",
            "--exit-on-error",
            env=env,
            stdin=archive,
        )

    start_command = [
        sys.executable,
        str(ROOT / "tools" / "local_start.py"),
        "up",
    ]
    if not print_credentials:
        start_command.append("--no-print-credentials")
    subprocess.run(start_command, cwd=ROOT, env=env, check=True)
    subprocess.run(
        [sys.executable, str(ROOT / "tools" / "verify_local_postgres_auth.py")],
        cwd=ROOT,
        env=env,
        check=True,
    )
    print(f"Local PostgreSQL backup restored: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)

    backup_parser = subparsers.add_parser("backup")
    backup_parser.add_argument("path", type=Path)

    restore_parser = subparsers.add_parser("restore-clean")
    restore_parser.add_argument("path", type=Path)
    restore_parser.add_argument("--confirm-reset", action="store_true")
    restore_parser.add_argument("--no-print-credentials", action="store_true")

    args = parser.parse_args()
    if args.action == "backup":
        backup(args.path)
    else:
        restore_clean(
            args.path,
            confirm_reset=args.confirm_reset,
            print_credentials=not args.no_print_credentials,
        )


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"NAPMS local PostgreSQL backup operation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
