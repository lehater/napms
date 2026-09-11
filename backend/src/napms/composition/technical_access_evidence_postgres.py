from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

import psycopg

from napms.composition.config import ApplicationConfig
from napms.technical_access_evidence.adapters.postgres import (
    PostgresTechnicalAccessEvidenceRepository,
)
from napms.technical_access_evidence.application.read import (
    GetTechnicalAccessEvidenceSet,
)
from napms.technical_access_evidence.application.record import (
    RecordTechnicalAccessEvidenceSet,
)


@dataclass(slots=True)
class TechnicalAccessEvidencePostgresScope:
    technical_access_evidence: PostgresTechnicalAccessEvidenceRepository
    record_technical_access_evidence: RecordTechnicalAccessEvidenceSet
    get_technical_access_evidence: GetTechnicalAccessEvidenceSet


@contextmanager
def open_technical_access_evidence_scope(
    config: ApplicationConfig,
) -> Iterator[TechnicalAccessEvidencePostgresScope]:
    with psycopg.connect(config.postgres.dsn) as connection:
        repository = PostgresTechnicalAccessEvidenceRepository(connection)
        yield TechnicalAccessEvidencePostgresScope(
            technical_access_evidence=repository,
            record_technical_access_evidence=RecordTechnicalAccessEvidenceSet(
                evidence_sets=repository
            ),
            get_technical_access_evidence=GetTechnicalAccessEvidenceSet(
                evidence_sets=repository
            ),
        )
