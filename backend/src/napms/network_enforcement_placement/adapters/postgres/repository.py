from datetime import datetime
from uuid import UUID

from psycopg import Connection, Error as PsycopgError
from psycopg.errors import UniqueViolation
from psycopg.types.json import Jsonb

from napms.network_enforcement_placement.application.capture import (
    KnowledgeSourceReference,
    PersistedPlacementKnowledgeCapture,
    PlacementKnowledgeCapture,
    SourceCaptureReference,
)
from napms.network_enforcement_placement.application.ports import (
    PlacementCaptureConflict,
    PlacementCommitOutcomeUnknown,
    PlacementPersistenceError,
)
from napms.network_enforcement_placement.domain.model import (
    EffectiveWindow,
    EnforcementAttachment,
    ForwardingPath,
    KnowledgeGap,
    LogicalFirewall,
    LogicalFirewallCorrespondence,
    NoForwardingPath,
    PathAttachmentReference,
    PlacementInvariantError,
    PlacementKnowledgeSnapshot,
    Provenance,
    ProviderRealizationReference,
    TrafficRelation,
    TraversalPoint,
    require_aware,
)


_COLUMNS = """
    capture_id,
    source_namespace,
    source_reference,
    source_capture_reference,
    source_ip,
    destination_ip,
    valid_from,
    valid_until,
    recorded_at,
    payload
"""


class PostgresPlacementKnowledgeRepository:
    """Append-only relation-scoped NEP knowledge capture repository."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def find_by_capture(
        self,
        *,
        source: KnowledgeSourceReference,
        source_capture_reference: SourceCaptureReference,
    ) -> PersistedPlacementKnowledgeCapture | None:
        try:
            row = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_network_enforcement_placement.knowledge_captures
                WHERE source_namespace = %s
                  AND source_reference = %s
                  AND source_capture_reference = %s
                """,
                (source.namespace, source.reference, source_capture_reference.value),
            ).fetchone()
            return None if row is None else self._hydrate(row)
        except PlacementPersistenceError:
            raise
        except (
            PsycopgError,
            ValueError,
            TypeError,
            KeyError,
            PlacementInvariantError,
        ) as exc:
            raise PlacementPersistenceError() from exc

    def load_for(
        self,
        *,
        relation: TrafficRelation,
        as_of: datetime,
    ) -> PlacementKnowledgeSnapshot:
        require_aware(as_of)
        try:
            rows = self._connection.execute(
                f"""
                SELECT {_COLUMNS}
                FROM napms_network_enforcement_placement.knowledge_captures
                WHERE source_ip = %s
                  AND destination_ip = %s
                  AND valid_from <= %s
                  AND (valid_until IS NULL OR %s < valid_until)
                ORDER BY capture_id
                """,
                (relation.source_ip, relation.destination_ip, as_of, as_of),
            ).fetchall()
            if not rows:
                return self._unknown(
                    "NoEffectiveKnowledgeCapture",
                    (relation.source_ip, relation.destination_ip),
                )
            if len(rows) > 1:
                return self._unknown(
                    "MultipleEffectiveKnowledgeCaptures",
                    tuple(str(row[0]) for row in rows),
                )
            return self._hydrate(rows[0]).payload.knowledge
        except PlacementPersistenceError:
            raise
        except (
            PsycopgError,
            ValueError,
            TypeError,
            KeyError,
            PlacementInvariantError,
        ) as exc:
            raise PlacementPersistenceError() from exc

    def add(self, capture: PersistedPlacementKnowledgeCapture) -> None:
        value = capture.payload
        try:
            self._connection.execute(
                """
                INSERT INTO napms_network_enforcement_placement.knowledge_captures (
                    capture_id,
                    source_namespace,
                    source_reference,
                    source_capture_reference,
                    source_ip,
                    destination_ip,
                    valid_from,
                    valid_until,
                    recorded_at,
                    payload
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    capture.capture_id,
                    value.source.namespace,
                    value.source.reference,
                    value.source_capture_reference.value,
                    value.relation.source_ip,
                    value.relation.destination_ip,
                    value.validity.valid_from,
                    value.validity.valid_until,
                    capture.recorded_at,
                    Jsonb(self._snapshot_to_json(value.knowledge)),
                ),
            )
        except UniqueViolation as exc:
            self._connection.rollback()
            if exc.diag.constraint_name == "uq_nep_source_capture":
                raise PlacementCaptureConflict() from exc
            raise PlacementPersistenceError() from exc
        except PsycopgError as exc:
            self._connection.rollback()
            raise PlacementPersistenceError() from exc

    def commit(self) -> None:
        try:
            self._connection.commit()
        except PsycopgError as exc:
            raise PlacementCommitOutcomeUnknown() from exc

    @staticmethod
    def _window_to_json(value: EffectiveWindow) -> dict:
        return {
            "valid_from": value.valid_from.isoformat(),
            "valid_until": (
                None if value.valid_until is None else value.valid_until.isoformat()
            ),
        }

    @staticmethod
    def _provenance_to_json(value: Provenance) -> list[str]:
        return list(value.references)

    @staticmethod
    def _provider_to_json(value: ProviderRealizationReference) -> dict:
        return {"namespace": value.namespace, "reference": value.reference}

    @staticmethod
    def _path_ref_to_json(value: PathAttachmentReference) -> dict:
        return {"namespace": value.namespace, "reference": value.reference}

    @classmethod
    def _snapshot_to_json(cls, value: PlacementKnowledgeSnapshot) -> dict:
        path = value.path
        no_path = value.no_forwarding_path
        return {
            "path": None
            if path is None
            else {
                "path_reference": path.path_reference,
                "traversal_points": [
                    {
                        "provider_realization": cls._provider_to_json(
                            point.provider_realization
                        ),
                        "path_attachment": cls._path_ref_to_json(
                            point.path_attachment
                        ),
                        "provenance": cls._provenance_to_json(point.provenance),
                    }
                    for point in path.traversal_points
                ],
                "validity": cls._window_to_json(path.validity),
                "provenance": cls._provenance_to_json(path.provenance),
            },
            "no_forwarding_path": None
            if no_path is None
            else {
                "validity": cls._window_to_json(no_path.validity),
                "provenance": cls._provenance_to_json(no_path.provenance),
            },
            "logical_firewalls": [
                {
                    "logical_firewall_id": str(item.logical_firewall_id),
                    "validity": cls._window_to_json(item.validity),
                    "provenance": cls._provenance_to_json(item.provenance),
                }
                for item in value.logical_firewalls
            ],
            "correspondences": [
                {
                    "logical_firewall_id": str(item.logical_firewall_id),
                    "provider_realization": cls._provider_to_json(
                        item.provider_realization
                    ),
                    "validity": cls._window_to_json(item.validity),
                    "provenance": cls._provenance_to_json(item.provenance),
                }
                for item in value.correspondences
            ],
            "attachments": [
                {
                    "enforcement_attachment_id": str(
                        item.enforcement_attachment_id
                    ),
                    "logical_firewall_id": str(item.logical_firewall_id),
                    "provider_realization": cls._provider_to_json(
                        item.provider_realization
                    ),
                    "path_attachment": cls._path_ref_to_json(
                        item.path_attachment
                    ),
                    "validity": cls._window_to_json(item.validity),
                    "provenance": cls._provenance_to_json(item.provenance),
                }
                for item in value.attachments
            ],
            "complete_for_pair": value.complete_for_pair,
            "complete_for_attachments": value.complete_for_attachments,
            "knowledge_gaps": [
                {
                    "owner": item.owner,
                    "reason": item.reason,
                    "references": list(item.references),
                }
                for item in value.knowledge_gaps
            ],
        }

    @staticmethod
    def _datetime(value) -> datetime:
        if not isinstance(value, str):
            raise PlacementPersistenceError(
                "persisted datetime must be an ISO-8601 string"
            )
        return datetime.fromisoformat(value)

    @classmethod
    def _window_from_json(cls, value) -> EffectiveWindow:
        value = cls._object(value, "validity")
        return EffectiveWindow(
            cls._datetime(value["valid_from"]),
            None
            if value.get("valid_until") is None
            else cls._datetime(value["valid_until"]),
        )

    @staticmethod
    def _provenance_from_json(value) -> Provenance:
        return Provenance(tuple(PostgresPlacementKnowledgeRepository._array(
            value, "provenance"
        )))

    @staticmethod
    def _provider_from_json(value) -> ProviderRealizationReference:
        value = PostgresPlacementKnowledgeRepository._object(
            value, "provider_realization"
        )
        return ProviderRealizationReference(value["namespace"], value["reference"])

    @staticmethod
    def _path_ref_from_json(value) -> PathAttachmentReference:
        value = PostgresPlacementKnowledgeRepository._object(value, "path_attachment")
        return PathAttachmentReference(value["namespace"], value["reference"])

    @classmethod
    def _snapshot_from_json(cls, value) -> PlacementKnowledgeSnapshot:
        value = cls._object(value, "payload")
        raw_path = value.get("path")
        path = None
        if raw_path is not None:
            raw_path = cls._object(raw_path, "path")
            path = ForwardingPath(
                raw_path["path_reference"],
                tuple(
                    TraversalPoint(
                        cls._provider_from_json(point["provider_realization"]),
                        cls._path_ref_from_json(point["path_attachment"]),
                        cls._provenance_from_json(point["provenance"]),
                    )
                    for point in cls._array(
                        raw_path["traversal_points"], "traversal_points"
                    )
                ),
                cls._window_from_json(raw_path["validity"]),
                cls._provenance_from_json(raw_path["provenance"]),
            )

        raw_no_path = value.get("no_forwarding_path")
        no_path = None
        if raw_no_path is not None:
            raw_no_path = cls._object(raw_no_path, "no_forwarding_path")
            no_path = NoForwardingPath(
                cls._window_from_json(raw_no_path["validity"]),
                cls._provenance_from_json(raw_no_path["provenance"]),
            )

        return PlacementKnowledgeSnapshot(
            path=path,
            no_forwarding_path=no_path,
            logical_firewalls=tuple(
                LogicalFirewall(
                    UUID(item["logical_firewall_id"]),
                    cls._window_from_json(item["validity"]),
                    cls._provenance_from_json(item["provenance"]),
                )
                for item in cls._array(
                    value["logical_firewalls"], "logical_firewalls"
                )
            ),
            correspondences=tuple(
                LogicalFirewallCorrespondence(
                    UUID(item["logical_firewall_id"]),
                    cls._provider_from_json(item["provider_realization"]),
                    cls._window_from_json(item["validity"]),
                    cls._provenance_from_json(item["provenance"]),
                )
                for item in cls._array(
                    value["correspondences"], "correspondences"
                )
            ),
            attachments=tuple(
                EnforcementAttachment(
                    UUID(item["enforcement_attachment_id"]),
                    UUID(item["logical_firewall_id"]),
                    cls._provider_from_json(item["provider_realization"]),
                    cls._path_ref_from_json(item["path_attachment"]),
                    cls._window_from_json(item["validity"]),
                    cls._provenance_from_json(item["provenance"]),
                )
                for item in cls._array(value["attachments"], "attachments")
            ),
            complete_for_pair=cls._boolean(
                value["complete_for_pair"], "complete_for_pair"
            ),
            complete_for_attachments=cls._boolean(
                value["complete_for_attachments"], "complete_for_attachments"
            ),
            knowledge_gaps=tuple(
                KnowledgeGap(
                    item["owner"],
                    item["reason"],
                    tuple(item.get("references", ())),
                )
                for item in cls._array(
                    value.get("knowledge_gaps", []), "knowledge_gaps"
                )
            ),
        )

    @classmethod
    def _hydrate(cls, row: tuple) -> PersistedPlacementKnowledgeCapture:
        return PersistedPlacementKnowledgeCapture(
            capture_id=row[0],
            recorded_at=row[8],
            payload=PlacementKnowledgeCapture(
                source=KnowledgeSourceReference(row[1], row[2]),
                source_capture_reference=SourceCaptureReference(row[3]),
                relation=TrafficRelation(row[4], row[5]),
                validity=EffectiveWindow(row[6], row[7]),
                knowledge=cls._snapshot_from_json(row[9]),
            ),
        )

    @staticmethod
    def _object(value, name: str) -> dict:
        if not isinstance(value, dict):
            raise PlacementPersistenceError(
                f"persisted {name} must be an object"
            )
        return value

    @staticmethod
    def _array(value, name: str) -> list:
        if not isinstance(value, list):
            raise PlacementPersistenceError(
                f"persisted {name} must be an array"
            )
        return value

    @staticmethod
    def _boolean(value, name: str) -> bool:
        if not isinstance(value, bool):
            raise PlacementPersistenceError(
                f"persisted {name} must be a boolean"
            )
        return value

    @staticmethod
    def _unknown(
        reason: str,
        references: tuple[str, ...],
    ) -> PlacementKnowledgeSnapshot:
        return PlacementKnowledgeSnapshot(
            complete_for_pair=False,
            complete_for_attachments=False,
            knowledge_gaps=(
                KnowledgeGap(
                    "Network Enforcement Placement",
                    reason,
                    references,
                ),
            ),
        )
