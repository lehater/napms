from uuid import UUID

from psycopg import Connection, Error as PsycopgError
from psycopg.errors import UniqueViolation
from psycopg.types.json import Jsonb

from napms.technical_access_evidence.application.ports import (
    EvidenceCaptureConflict,
    EvidenceCommitOutcomeUnknown,
    EvidencePersistenceError,
    EvidenceSetFilters,
)
from napms.technical_access_evidence.domain.model import (
    AddressConstraint,
    AddressConstraintKind,
    AddressRange,
    EvidenceAction,
    EvidenceInvariantError,
    EvidenceKind,
    EvidenceSourceReference,
    EvidenceTime,
    EvidenceTimeKind,
    PortConstraint,
    PortConstraintKind,
    PortRange,
    ProtocolSelector,
    ProtocolSelectorKind,
    SourceCaptureReference,
    SourceScopeReference,
    TechnicalAccessEntry,
    TechnicalAccessEntryPayload,
    TechnicalAccessEvidenceSet,
    TechnicalAccessPredicate,
)


_COLUMNS = """
    evidence_set_id,
    kind,
    source_namespace,
    source_reference,
    source_scope_reference,
    source_capture_reference,
    evidence_time_kind,
    evidence_time_at,
    evidence_time_start,
    evidence_time_end,
    recorded_at,
    entries
"""


class PostgresTechnicalAccessEvidenceRepository:
    """Operation-scoped append-only PostgreSQL repository/UoW."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get_by_id(
        self,
        evidence_set_id: UUID,
    ) -> TechnicalAccessEvidenceSet | None:
        try:
            row = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_technical_access_evidence.evidence_sets
                WHERE evidence_set_id = %s
                """,
                (evidence_set_id,),
            ).fetchone()
            return self._hydrate(row) if row is not None else None
        except EvidencePersistenceError:
            raise
        except (PsycopgError, ValueError, TypeError, KeyError, EvidenceInvariantError) as exc:
            raise EvidencePersistenceError() from exc

    def find_by_capture(
        self,
        *,
        source: EvidenceSourceReference,
        source_capture_reference: SourceCaptureReference,
    ) -> TechnicalAccessEvidenceSet | None:
        try:
            row = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_technical_access_evidence.evidence_sets
                WHERE source_namespace = %s
                  AND source_reference = %s
                  AND source_capture_reference = %s
                """,
                (
                    source.namespace,
                    source.reference,
                    source_capture_reference.value,
                ),
            ).fetchone()
            return self._hydrate(row) if row is not None else None
        except EvidencePersistenceError:
            raise
        except (PsycopgError, ValueError, TypeError, KeyError, EvidenceInvariantError) as exc:
            raise EvidencePersistenceError() from exc

    def list(
        self,
        *,
        filters: EvidenceSetFilters,
        offset: int,
        limit: int,
    ) -> tuple[TechnicalAccessEvidenceSet, ...]:
        if offset < 0:
            raise ValueError("offset must be >= 0")
        if limit < 1:
            raise ValueError("limit must be >= 1")

        clauses = []
        params = []
        if filters.source is not None:
            clauses.extend(
                (
                    "source_namespace = %s",
                    "source_reference = %s",
                )
            )
            params.extend(
                (
                    filters.source.namespace,
                    filters.source.reference,
                )
            )
        if filters.source_scope is not None:
            clauses.append("source_scope_reference = %s")
            params.append(filters.source_scope.value)
        if filters.kind is not None:
            clauses.append("kind = %s")
            params.append(filters.kind.value)
        if filters.recorded_from is not None:
            clauses.append("recorded_at >= %s")
            params.append(filters.recorded_from)
        if filters.recorded_until is not None:
            clauses.append("recorded_at < %s")
            params.append(filters.recorded_until)

        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.extend((offset, limit))
        try:
            rows = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_technical_access_evidence.evidence_sets
                {where}
                ORDER BY recorded_at DESC, evidence_set_id
                OFFSET %s
                LIMIT %s
                """,
                tuple(params),
            ).fetchall()
            return tuple(self._hydrate(row) for row in rows)
        except EvidencePersistenceError:
            raise
        except (PsycopgError, ValueError, TypeError, KeyError, EvidenceInvariantError) as exc:
            raise EvidencePersistenceError() from exc

    def add(self, evidence_set: TechnicalAccessEvidenceSet) -> None:
        try:
            self._connection.execute(
                """
                INSERT INTO napms_technical_access_evidence.evidence_sets (
                    evidence_set_id,
                    kind,
                    source_namespace,
                    source_reference,
                    source_scope_reference,
                    source_capture_reference,
                    evidence_time_kind,
                    evidence_time_at,
                    evidence_time_start,
                    evidence_time_end,
                    recorded_at,
                    entries
                )
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s
                )
                """,
                (
                    evidence_set.evidence_set_id,
                    evidence_set.kind.value,
                    evidence_set.source.namespace,
                    evidence_set.source.reference,
                    evidence_set.source_scope.value,
                    evidence_set.source_capture_reference.value,
                    evidence_set.evidence_time.kind.value,
                    evidence_set.evidence_time.at,
                    evidence_set.evidence_time.start,
                    evidence_set.evidence_time.end,
                    evidence_set.recorded_at,
                    Jsonb(
                        [
                            self._serialize_entry(entry)
                            for entry in evidence_set.entries
                        ]
                    ),
                ),
            )
        except UniqueViolation as exc:
            self._connection.rollback()
            if exc.diag.constraint_name == "uq_tae_source_capture":
                raise EvidenceCaptureConflict() from exc
            raise EvidencePersistenceError() from exc
        except EvidencePersistenceError:
            raise
        except PsycopgError as exc:
            self._connection.rollback()
            raise EvidencePersistenceError() from exc

    def commit(self) -> None:
        try:
            self._connection.commit()
        except PsycopgError as exc:
            raise EvidenceCommitOutcomeUnknown() from exc

    @staticmethod
    def _serialize_address(constraint: AddressConstraint) -> dict:
        return {
            "kind": constraint.kind.value,
            "ranges": [
                {
                    "first": value.first,
                    "last": value.last,
                }
                for value in constraint.ranges
            ],
        }

    @staticmethod
    def _serialize_ports(constraint: PortConstraint) -> dict:
        return {
            "kind": constraint.kind.value,
            "ranges": [
                {
                    "first": value.first,
                    "last": value.last,
                }
                for value in constraint.ranges
            ],
        }

    @classmethod
    def _serialize_entry(cls, entry: TechnicalAccessEntry) -> dict:
        payload = entry.payload
        return {
            "evidence_entry_id": str(entry.evidence_entry_id),
            "predicate": {
                "source_addresses": cls._serialize_address(
                    payload.predicate.source_addresses
                ),
                "destination_addresses": cls._serialize_address(
                    payload.predicate.destination_addresses
                ),
                "protocol": {
                    "kind": payload.predicate.protocol.kind.value,
                    "number": payload.predicate.protocol.number,
                },
                "source_ports": cls._serialize_ports(
                    payload.predicate.source_ports
                ),
                "destination_ports": cls._serialize_ports(
                    payload.predicate.destination_ports
                ),
            },
            "action": payload.action.value if payload.action is not None else None,
            "source_entry_reference": payload.source_entry_reference,
            "source_position": payload.source_position,
        }

    @staticmethod
    def _hydrate_evidence_time(row: tuple) -> EvidenceTime:
        kind = EvidenceTimeKind(row[6])
        if kind is EvidenceTimeKind.UNKNOWN:
            return EvidenceTime.unknown()
        if kind is EvidenceTimeKind.INSTANT:
            return EvidenceTime.instant(row[7])
        return EvidenceTime.window(row[8], row[9])

    @staticmethod
    def _hydrate_address(value: dict) -> AddressConstraint:
        kind = AddressConstraintKind(value["kind"])
        if kind is AddressConstraintKind.ANY:
            if value.get("ranges"):
                raise EvidencePersistenceError(
                    "persisted Any address constraint cannot carry ranges"
                )
            return AddressConstraint.any()
        return AddressConstraint.ranged(
            *(
                AddressRange(item["first"], item["last"])
                for item in value["ranges"]
            )
        )

    @staticmethod
    def _hydrate_ports(value: dict) -> PortConstraint:
        kind = PortConstraintKind(value["kind"])
        if kind is PortConstraintKind.ANY:
            if value.get("ranges"):
                raise EvidencePersistenceError(
                    "persisted Any port constraint cannot carry ranges"
                )
            return PortConstraint.any()
        if kind is PortConstraintKind.NOT_APPLICABLE:
            if value.get("ranges"):
                raise EvidencePersistenceError(
                    "persisted NotApplicable port constraint cannot carry ranges"
                )
            return PortConstraint.not_applicable()
        return PortConstraint.ranged(
            *(
                PortRange(item["first"], item["last"])
                for item in value["ranges"]
            )
        )

    @staticmethod
    def _hydrate_protocol(value: dict) -> ProtocolSelector:
        kind = ProtocolSelectorKind(value["kind"])
        if kind is ProtocolSelectorKind.ANY:
            if value.get("number") is not None:
                raise EvidencePersistenceError(
                    "persisted Any protocol cannot carry a number"
                )
            return ProtocolSelector.any()
        return ProtocolSelector.ip_protocol(value["number"])

    @classmethod
    def _hydrate_entry(cls, value: dict) -> TechnicalAccessEntry:
        predicate = value["predicate"]
        action = value.get("action")
        return TechnicalAccessEntry(
            evidence_entry_id=UUID(value["evidence_entry_id"]),
            payload=TechnicalAccessEntryPayload(
                predicate=TechnicalAccessPredicate(
                    source_addresses=cls._hydrate_address(
                        predicate["source_addresses"]
                    ),
                    destination_addresses=cls._hydrate_address(
                        predicate["destination_addresses"]
                    ),
                    protocol=cls._hydrate_protocol(
                        predicate["protocol"]
                    ),
                    source_ports=cls._hydrate_ports(
                        predicate["source_ports"]
                    ),
                    destination_ports=cls._hydrate_ports(
                        predicate["destination_ports"]
                    ),
                ),
                action=EvidenceAction(action) if action is not None else None,
                source_entry_reference=value.get("source_entry_reference"),
                source_position=value.get("source_position"),
            ),
        )

    @classmethod
    def _hydrate(cls, row: tuple) -> TechnicalAccessEvidenceSet:
        entries = row[11]
        if not isinstance(entries, list):
            raise EvidencePersistenceError(
                "persisted TAE entries must be a JSON array"
            )
        return TechnicalAccessEvidenceSet(
            evidence_set_id=row[0],
            kind=EvidenceKind(row[1]),
            source=EvidenceSourceReference(
                namespace=row[2],
                reference=row[3],
            ),
            source_scope=SourceScopeReference(row[4]),
            source_capture_reference=SourceCaptureReference(row[5]),
            evidence_time=cls._hydrate_evidence_time(row),
            recorded_at=row[10],
            entries=tuple(cls._hydrate_entry(item) for item in entries),
        )
