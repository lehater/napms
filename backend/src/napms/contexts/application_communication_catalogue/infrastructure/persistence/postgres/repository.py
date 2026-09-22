from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import psycopg

from napms.contexts.application_communication_catalogue.application.ports import (
    CatalogueVersionConflict,
    ResolvedInteractionRevision,
)
from napms.contexts.application_communication_catalogue.domain.model import (
    Application,
    Component,
    Interaction,
    InteractionRevision,
    PortRange,
    TrafficClause,
)


class PostgresApplicationCommunicationCatalogue:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, value: Application | Interaction) -> None:
        if isinstance(value, Application):
            self._add_application(value)
        else:
            self._add_interaction(value)

    def get(self, ref: UUID) -> Application | Interaction | None:
        application = self.get_application(ref)
        if application is not None:
            return application
        return self.get_interaction(ref)

    def save(
        self,
        value: Application | Interaction,
        *,
        expected_version: int,
    ) -> None:
        if isinstance(value, Application):
            self.save_application(value, expected_version=expected_version)
        else:
            self.save_interaction(value, expected_version=expected_version)

    def list_applications(self) -> tuple[Application, ...]:
        with psycopg.connect(self._dsn) as connection:
            rows = connection.execute(
                """SELECT application_ref FROM application_communication_catalogue.application ORDER BY name, application_ref"""
            ).fetchall()
        return tuple(value for (ref,) in rows if (value := self.get_application(ref)) is not None)

    def get_application(self, application_ref: UUID) -> Application | None:
        with psycopg.connect(self._dsn) as connection:
            row = connection.execute(
                """
                SELECT application_ref, name, version
                FROM application_communication_catalogue.application
                WHERE application_ref = %s
                """,
                (application_ref,),
            ).fetchone()
            if row is None:
                return None
            component_rows = connection.execute(
                """
                SELECT component_ref, name
                FROM application_communication_catalogue.component
                WHERE application_ref = %s
                ORDER BY created_at, component_ref
                """,
                (application_ref,),
            ).fetchall()
            return Application(
                application_ref=row[0],
                name=row[1],
                version=row[2],
                components=tuple(
                    Component(component_ref=component_ref, name=name)
                    for component_ref, name in component_rows
                ),
            )

    def save_application(self, value: Application, *, expected_version: int) -> None:
        with psycopg.connect(self._dsn) as connection:
            updated = connection.execute(
                """
                UPDATE application_communication_catalogue.application
                SET version = %s
                WHERE application_ref = %s AND version = %s
                """,
                (value.version, value.application_ref, expected_version),
            )
            if updated.rowcount != 1:
                raise CatalogueVersionConflict(str(value.application_ref))
            for component in value.components:
                connection.execute(
                    """
                    INSERT INTO application_communication_catalogue.component
                        (component_ref, application_ref, name)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (component_ref) DO NOTHING
                    """,
                    (component.component_ref, value.application_ref, component.name),
                )

    def get_interaction(self, interaction_ref: UUID) -> Interaction | None:
        with psycopg.connect(self._dsn) as connection:
            row = connection.execute(
                """
                SELECT interaction_ref, source_component_ref, destination_component_ref,
                       purpose, version
                FROM application_communication_catalogue.interaction
                WHERE interaction_ref = %s
                """,
                (interaction_ref,),
            ).fetchone()
            if row is None:
                return None
            revision_rows = connection.execute(
                """
                SELECT revision_ref, revision_no, created_by_subject
                FROM application_communication_catalogue.interaction_revision
                WHERE interaction_ref = %s
                ORDER BY revision_no
                """,
                (interaction_ref,),
            ).fetchall()
            revisions = tuple(
                InteractionRevision(
                    revision_ref=revision_ref,
                    revision_no=revision_no,
                    traffic_clauses=self._load_clauses(connection, revision_ref),
                    created_by_subject=created_by_subject,
                )
                for revision_ref, revision_no, created_by_subject in revision_rows
            )
            return Interaction(
                interaction_ref=row[0],
                source_component_ref=row[1],
                destination_component_ref=row[2],
                purpose=row[3],
                version=row[4],
                revisions=revisions,
            )

    def list_interactions_for_components(
        self, component_refs: tuple[UUID, ...]
    ) -> tuple[Interaction, ...]:
        if not component_refs:
            return ()
        with psycopg.connect(self._dsn) as connection:
            rows = connection.execute(
                """
                SELECT interaction_ref
                FROM application_communication_catalogue.interaction
                WHERE source_component_ref = ANY(%s)
                   OR destination_component_ref = ANY(%s)
                ORDER BY interaction_ref
                """,
                (list(component_refs), list(component_refs)),
            ).fetchall()
        return tuple(value for (ref,) in rows if (value := self.get_interaction(ref)) is not None)

    def save_interaction(self, value: Interaction, *, expected_version: int) -> None:
        with psycopg.connect(self._dsn) as connection:
            updated = connection.execute(
                """
                UPDATE application_communication_catalogue.interaction
                SET version = %s
                WHERE interaction_ref = %s AND version = %s
                """,
                (value.version, value.interaction_ref, expected_version),
            )
            if updated.rowcount != 1:
                raise CatalogueVersionConflict(str(value.interaction_ref))
            for revision in value.revisions:
                connection.execute(
                    """
                    INSERT INTO application_communication_catalogue.interaction_revision
                        (revision_ref, interaction_ref, revision_no, created_by_subject)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (revision_ref) DO NOTHING
                    """,
                    (
                        revision.revision_ref,
                        value.interaction_ref,
                        revision.revision_no,
                        revision.created_by_subject,
                    ),
                )
                self._persist_clauses(connection, revision)

    def resolve(self, component_ref: UUID) -> Component | None:
        with psycopg.connect(self._dsn) as connection:
            row = connection.execute(
                """
                SELECT component_ref, name
                FROM application_communication_catalogue.component
                WHERE component_ref = %s
                """,
                (component_ref,),
            ).fetchone()
            return None if row is None else Component(component_ref=row[0], name=row[1])

    def resolve_revision(self, revision_ref: UUID) -> ResolvedInteractionRevision | None:
        with psycopg.connect(self._dsn) as connection:
            return self.resolve_revision_in(connection, revision_ref)

    @classmethod
    def resolve_revision_in(
        cls,
        connection: psycopg.Connection[Any],
        revision_ref: UUID,
    ) -> ResolvedInteractionRevision | None:
        row = connection.execute(
            """
                SELECT revision_ref, interaction_ref, revision_no, created_by_subject
                FROM application_communication_catalogue.interaction_revision
                WHERE revision_ref = %s
                """,
            (revision_ref,),
        ).fetchone()
        if row is None:
            return None
        return ResolvedInteractionRevision(
            interaction_ref=row[1],
            revision=InteractionRevision(
                revision_ref=row[0],
                revision_no=row[2],
                traffic_clauses=cls._load_clauses(connection, row[0]),
                created_by_subject=row[3],
            ),
        )

    @staticmethod
    def resolve_interaction_in(
        connection: psycopg.Connection[Any],
        interaction_ref: UUID,
    ) -> Interaction | None:
        row = connection.execute(
            """
            SELECT interaction_ref, source_component_ref, destination_component_ref,
                   purpose, version
            FROM application_communication_catalogue.interaction
            WHERE interaction_ref = %s
            """,
            (interaction_ref,),
        ).fetchone()
        if row is None:
            return None
        return Interaction(
            interaction_ref=row[0],
            source_component_ref=row[1],
            destination_component_ref=row[2],
            purpose=row[3],
            version=row[4],
        )

    def _add_application(self, value: Application) -> None:
        with psycopg.connect(self._dsn) as connection:
            connection.execute(
                """
                INSERT INTO application_communication_catalogue.application
                    (application_ref, name, version)
                VALUES (%s, %s, %s)
                """,
                (value.application_ref, value.name, value.version),
            )

    def _add_interaction(self, value: Interaction) -> None:
        with psycopg.connect(self._dsn) as connection:
            connection.execute(
                """
                INSERT INTO application_communication_catalogue.interaction
                    (interaction_ref, source_component_ref, destination_component_ref,
                     purpose, version)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    value.interaction_ref,
                    value.source_component_ref,
                    value.destination_component_ref,
                    value.purpose,
                    value.version,
                ),
            )

    @staticmethod
    def _load_clauses(
        connection: psycopg.Connection[Any],
        revision_ref: UUID,
    ) -> tuple[TrafficClause, ...]:
        clause_rows = connection.execute(
            """
            SELECT clause_ref, ip_protocol
            FROM application_communication_catalogue.interaction_traffic_clause
            WHERE revision_ref = %s
            ORDER BY clause_ordinal
            """,
            (revision_ref,),
        ).fetchall()
        clauses: list[TrafficClause] = []
        for clause_ref, ip_protocol in clause_rows:
            range_rows = connection.execute(
                """
                SELECT direction, port_from, port_to
                FROM application_communication_catalogue.interaction_port_range
                WHERE clause_ref = %s
                ORDER BY direction, range_ordinal
                """,
                (clause_ref,),
            ).fetchall()
            source_ports = tuple(
                PortRange(start=port_from, end=port_to)
                for direction, port_from, port_to in range_rows
                if direction == "SOURCE"
            )
            destination_ports = tuple(
                PortRange(start=port_from, end=port_to)
                for direction, port_from, port_to in range_rows
                if direction == "DESTINATION"
            )
            clauses.append(
                TrafficClause(
                    ip_protocol=ip_protocol,
                    source_ports=source_ports,
                    destination_ports=destination_ports,
                )
            )
        return tuple(clauses)

    @staticmethod
    def _persist_clauses(
        connection: psycopg.Connection[Any],
        revision: InteractionRevision,
    ) -> None:
        for clause_ordinal, clause in enumerate(revision.traffic_clauses):
            clause_ref = uuid4()
            connection.execute(
                """
                INSERT INTO application_communication_catalogue.interaction_traffic_clause
                    (clause_ref, revision_ref, clause_ordinal, ip_protocol)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (revision_ref, clause_ordinal) DO NOTHING
                """,
                (
                    clause_ref,
                    revision.revision_ref,
                    clause_ordinal,
                    clause.ip_protocol,
                ),
            )
            existing = connection.execute(
                """
                SELECT clause_ref
                FROM application_communication_catalogue.interaction_traffic_clause
                WHERE revision_ref = %s AND clause_ordinal = %s
                """,
                (revision.revision_ref, clause_ordinal),
            ).fetchone()
            assert existing is not None
            persisted_clause_ref = existing[0]
            for direction, ranges in (
                ("SOURCE", clause.source_ports),
                ("DESTINATION", clause.destination_ports),
            ):
                for range_ordinal, port_range in enumerate(ranges):
                    connection.execute(
                        """
                        INSERT INTO application_communication_catalogue.interaction_port_range
                            (range_ref, clause_ref, direction, range_ordinal,
                             port_from, port_to)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (clause_ref, direction, range_ordinal) DO NOTHING
                        """,
                        (
                            uuid4(),
                            persisted_clause_ref,
                            direction,
                            range_ordinal,
                            port_range.start,
                            port_range.end,
                        ),
                    )
