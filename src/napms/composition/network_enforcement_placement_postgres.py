from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

import psycopg

from napms.composition.config import ApplicationConfig
from napms.network_enforcement_placement.adapters.postgres import (
    PostgresPlacementKnowledgeRepository,
)
from napms.network_enforcement_placement.application.record import (
    RecordPlacementKnowledge,
)
from napms.network_enforcement_placement.application.select import (
    SelectEnforcement,
)


@dataclass(slots=True)
class NetworkEnforcementPlacementPostgresScope:
    placement_knowledge: PostgresPlacementKnowledgeRepository
    record_placement_knowledge: RecordPlacementKnowledge
    select_enforcement: SelectEnforcement


@contextmanager
def open_network_enforcement_placement_scope(
    config: ApplicationConfig,
) -> Iterator[NetworkEnforcementPlacementPostgresScope]:
    with psycopg.connect(config.postgres.dsn) as connection:
        repository = PostgresPlacementKnowledgeRepository(connection)
        yield NetworkEnforcementPlacementPostgresScope(
            placement_knowledge=repository,
            record_placement_knowledge=RecordPlacementKnowledge(
                captures=repository
            ),
            select_enforcement=SelectEnforcement(
                placement_knowledge=repository
            ),
        )
