from napms.composition.config import load_application_config
from napms.composition.postgres_migrations import apply_greenfield_migrations


def run() -> None:
    config = load_application_config()
    applied = apply_greenfield_migrations(config)
    print(f"NAPMS migrations applied: {len(applied)}")
