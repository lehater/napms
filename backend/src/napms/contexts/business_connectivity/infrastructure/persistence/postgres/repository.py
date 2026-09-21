from __future__ import annotations

from typing import Any
from uuid import UUID

import psycopg

from napms.contexts.business_connectivity.application.ports import (
    BusinessConnectivityVersionConflict,
)
from napms.contexts.business_connectivity.domain.model import (
    BusinessProcess,
    ConnectivityNeed,
    NeedStatus,
)


class PostgresBusinessProcessRepository:
    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def add(self, process: BusinessProcess) -> None:
        with psycopg.connect(self._dsn) as connection:
            connection.execute(
                """
                INSERT INTO business_connectivity.business_process
                    (process_ref, name, description,
                     organization_external_reference, organization_display_name,
                     criticality_label, version)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    process.process_ref,
                    process.name,
                    process.description,
                    process.organization_external_reference,
                    process.organization_display_name,
                    process.criticality_label,
                    process.version,
                ),
            )

    def get_process(self, process_ref: UUID) -> BusinessProcess | None:
        with psycopg.connect(self._dsn) as connection:
            row = connection.execute(
                """
                SELECT process_ref, name, description,
                       organization_external_reference, organization_display_name,
                       criticality_label, version
                FROM business_connectivity.business_process
                WHERE process_ref = %s
                """,
                (process_ref,),
            ).fetchone()
            if row is None:
                return None
            needs = connection.execute(
                """
                SELECT need_ref, interaction_ref, participant_component_ref,
                       business_basis, status, created_by_subject, retired_at
                FROM business_connectivity.connectivity_need
                WHERE process_ref = %s
                ORDER BY created_at, need_ref
                """,
                (process_ref,),
            ).fetchall()
            return BusinessProcess(
                process_ref=row[0],
                name=row[1],
                description=row[2],
                organization_external_reference=row[3],
                organization_display_name=row[4],
                criticality_label=row[5],
                version=row[6],
                needs=tuple(
                    ConnectivityNeed(
                        need_ref=need_ref,
                        interaction_ref=interaction_ref,
                        participant_component_ref=participant_component_ref,
                        business_basis=business_basis,
                        status=NeedStatus(status),
                        created_by_subject=created_by_subject,
                        retired_at=retired_at,
                    )
                    for (
                        need_ref,
                        interaction_ref,
                        participant_component_ref,
                        business_basis,
                        status,
                        created_by_subject,
                        retired_at,
                    ) in needs
                ),
            )

    @staticmethod
    def lock_current_need_in(
        connection: psycopg.Connection[Any],
        need_ref: UUID,
    ) -> tuple[ConnectivityNeed, int] | None:
        row = connection.execute(
            """
            SELECT n.need_ref, n.interaction_ref, n.participant_component_ref,
                   n.business_basis, n.status, n.created_by_subject, n.retired_at,
                   p.version
            FROM business_connectivity.connectivity_need AS n
            JOIN business_connectivity.business_process AS p
              ON p.process_ref = n.process_ref
            WHERE n.need_ref = %s AND n.status = 'ACTIVE'
            FOR UPDATE OF n, p
            """,
            (need_ref,),
        ).fetchone()
        if row is None:
            return None
        need = ConnectivityNeed(
            need_ref=row[0],
            interaction_ref=row[1],
            participant_component_ref=row[2],
            business_basis=row[3],
            status=NeedStatus(row[4]),
            created_by_subject=row[5],
            retired_at=row[6],
        )
        return need, row[7]

    def save_process(self, process: BusinessProcess, *, expected_version: int) -> None:
        with psycopg.connect(self._dsn) as connection:
            updated = connection.execute(
                """
                UPDATE business_connectivity.business_process
                SET organization_external_reference = %s,
                    organization_display_name = %s,
                    criticality_label = %s,
                    version = %s
                WHERE process_ref = %s AND version = %s
                """,
                (
                    process.organization_external_reference,
                    process.organization_display_name,
                    process.criticality_label,
                    process.version,
                    process.process_ref,
                    expected_version,
                ),
            )
            if updated.rowcount != 1:
                raise BusinessConnectivityVersionConflict(str(process.process_ref))

            for need in process.needs:
                connection.execute(
                    """
                    INSERT INTO business_connectivity.connectivity_need
                        (need_ref, process_ref, interaction_ref,
                         participant_component_ref, business_basis, status,
                         created_by_subject, retired_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (need_ref) DO UPDATE
                    SET status = EXCLUDED.status,
                        retired_at = EXCLUDED.retired_at
                    """,
                    (
                        need.need_ref,
                        process.process_ref,
                        need.interaction_ref,
                        need.participant_component_ref,
                        need.business_basis,
                        need.status.value,
                        need.created_by_subject,
                        need.retired_at,
                    ),
                )
