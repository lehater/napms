from collections import defaultdict

from psycopg import Connection, Error as PsycopgError
from psycopg.errors import UniqueViolation

from napms.resource_catalogue.application.ports import (
    ResourceCatalogueCommandReceipt,
    ResourceCatalogueConcurrencyConflict,
    ResourceCatalogueIdempotencyConflict,
    ResourceCataloguePersistenceError,
    ResourceCataloguePersistenceOutcomeUnknown,
)
from napms.resource_catalogue.domain.model import (
    EndpointAddress,
    Resource,
    ResourceCatalogueInvariantError,
    ResourceLifecycleState,
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
)
from napms.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibility,
    ResourceResponsibilityRole,
)


class PostgresResourceCatalogueCurationRepository:
    """Task-oriented RC curation repository and transaction boundary."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection
        self._pending_receipt: tuple[str, str, ResourceCatalogueCommandReceipt] | None = None

    def get_resource(self, resource_reference: str) -> Resource | None:
        row = self._fetchone(
            """
            SELECT resource_reference, provenance_reference, display_name,
                   lifecycle_state, retirement_provenance_reference, version
            FROM napms_resource_catalogue.resources
            WHERE resource_reference = %s
            """,
            (resource_reference,),
        )
        return self._resource(row) if row is not None else None

    def add_resource(self, resource: Resource) -> None:
        self._execute(
            """
            INSERT INTO napms_resource_catalogue.resources (
                resource_reference, provenance_reference, display_name,
                lifecycle_state, retirement_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                resource.resource_reference,
                resource.provenance_reference,
                resource.display_name,
                resource.lifecycle_state.value,
                resource.retirement_provenance_reference,
                resource.version,
            ),
        )

    def save_resource(self, resource: Resource, *, expected_version: int) -> None:
        result = self._execute(
            """
            UPDATE napms_resource_catalogue.resources
            SET display_name = %s,
                lifecycle_state = %s,
                retirement_provenance_reference = %s,
                version = %s
            WHERE resource_reference = %s
              AND version = %s
            """,
            (
                resource.display_name,
                resource.lifecycle_state.value,
                resource.retirement_provenance_reference,
                resource.version,
                resource.resource_reference,
                expected_version,
            ),
        )
        self._require_updated(result)

    def has_effective_scope_affiliations(self, *, resource_reference: str, as_of) -> bool:
        return self._fetchone(
            """
            SELECT 1
            FROM napms_resource_catalogue.resource_scope_affiliations
            WHERE resource_reference = %s
              AND valid_from <= %s
              AND (valid_to IS NULL OR %s < valid_to)
            LIMIT 1
            """,
            (resource_reference, as_of, as_of),
        ) is not None

    def has_effective_responsibilities(self, *, resource_reference: str, as_of) -> bool:
        return self._fetchone(
            """
            SELECT 1
            FROM napms_resource_catalogue.resource_responsibilities
            WHERE resource_reference = %s
              AND valid_from <= %s
              AND (valid_to IS NULL OR %s < valid_to)
            LIMIT 1
            """,
            (resource_reference, as_of, as_of),
        ) is not None

    def get_realization(self, fact_reference: str) -> ResourceRealizationVersion | None:
        rows = self._realization_rows("WHERE r.fact_reference = %s", (fact_reference,))
        if not rows:
            return None
        return self._realizations(rows)[0]

    def find_overlapping_realizations(
        self,
        *,
        resource_reference: str,
        valid_from,
        valid_to,
    ) -> tuple[ResourceRealizationVersion, ...]:
        rows = self._realization_rows(
            """
            WHERE r.resource_reference = %s
              AND r.valid_from < COALESCE(%s, 'infinity'::timestamptz)
              AND %s < COALESCE(r.valid_to, 'infinity'::timestamptz)
            """,
            (resource_reference, valid_to, valid_from),
        )
        return self._realizations(rows)

    def add_realization(self, realization: ResourceRealizationVersion) -> None:
        self._execute(
            """
            INSERT INTO napms_resource_catalogue.resource_realization_versions (
                fact_reference, resource_reference, valid_from, valid_to,
                provenance_reference, end_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                realization.fact_reference,
                realization.resource_reference,
                realization.valid_from,
                realization.valid_to,
                realization.provenance_reference,
                realization.end_provenance_reference,
                realization.version,
            ),
        )
        for endpoint in realization.endpoint_realizations:
            self._execute(
                """
                INSERT INTO napms_resource_catalogue.resource_endpoints (
                    fact_reference, endpoint_reference, technical_address
                )
                VALUES (%s, %s, %s)
                """,
                (
                    realization.fact_reference,
                    endpoint.endpoint_reference,
                    endpoint.technical_address,
                ),
            )

    def save_realization(
        self,
        realization: ResourceRealizationVersion,
        *,
        expected_version: int,
    ) -> None:
        result = self._execute(
            """
            UPDATE napms_resource_catalogue.resource_realization_versions
            SET valid_to = %s,
                end_provenance_reference = %s,
                version = %s
            WHERE fact_reference = %s
              AND resource_reference = %s
              AND version = %s
            """,
            (
                realization.valid_to,
                realization.end_provenance_reference,
                realization.version,
                realization.fact_reference,
                realization.resource_reference,
                expected_version,
            ),
        )
        self._require_updated(result)

    def get_scope_affiliation(self, affiliation_reference: str) -> ResourceScopeAffiliation | None:
        row = self._fetchone(
            """
            SELECT affiliation_reference, resource_reference, responsibility_scope,
                   valid_from, valid_to, provenance_reference,
                   end_provenance_reference, version
            FROM napms_resource_catalogue.resource_scope_affiliations
            WHERE affiliation_reference = %s
            """,
            (affiliation_reference,),
        )
        return self._affiliation(row) if row is not None else None

    def find_overlapping_scope_affiliations(
        self,
        *,
        resource_reference: str,
        responsibility_scope: str,
        valid_from,
        valid_to,
    ) -> tuple[ResourceScopeAffiliation, ...]:
        rows = self._fetchall(
            """
            SELECT affiliation_reference, resource_reference, responsibility_scope,
                   valid_from, valid_to, provenance_reference,
                   end_provenance_reference, version
            FROM napms_resource_catalogue.resource_scope_affiliations
            WHERE resource_reference = %s
              AND responsibility_scope = %s
              AND valid_from < COALESCE(%s, 'infinity'::timestamptz)
              AND %s < COALESCE(valid_to, 'infinity'::timestamptz)
            ORDER BY valid_from, affiliation_reference
            """,
            (resource_reference, responsibility_scope, valid_to, valid_from),
        )
        return tuple(self._affiliation(row) for row in rows)

    def add_scope_affiliation(self, affiliation: ResourceScopeAffiliation) -> None:
        self._execute(
            """
            INSERT INTO napms_resource_catalogue.resource_scope_affiliations (
                affiliation_reference, resource_reference, responsibility_scope,
                valid_from, valid_to, provenance_reference,
                end_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                affiliation.affiliation_reference,
                affiliation.resource_reference,
                affiliation.responsibility_scope,
                affiliation.valid_from,
                affiliation.valid_to,
                affiliation.provenance_reference,
                affiliation.end_provenance_reference,
                affiliation.version,
            ),
        )

    def save_scope_affiliation(
        self,
        affiliation: ResourceScopeAffiliation,
        *,
        expected_version: int,
    ) -> None:
        result = self._execute(
            """
            UPDATE napms_resource_catalogue.resource_scope_affiliations
            SET valid_to = %s,
                end_provenance_reference = %s,
                version = %s
            WHERE affiliation_reference = %s
              AND resource_reference = %s
              AND responsibility_scope = %s
              AND version = %s
            """,
            (
                affiliation.valid_to,
                affiliation.end_provenance_reference,
                affiliation.version,
                affiliation.affiliation_reference,
                affiliation.resource_reference,
                affiliation.responsibility_scope,
                expected_version,
            ),
        )
        self._require_updated(result)

    def get_responsibility(self, assignment_reference: str) -> ResourceResponsibility | None:
        row = self._fetchone(
            """
            SELECT assignment_reference, resource_reference, party_reference,
                   party_kind, role, display_name, contact, valid_from, valid_to,
                   provenance_reference, end_provenance_reference, version
            FROM napms_resource_catalogue.resource_responsibilities
            WHERE assignment_reference = %s
            """,
            (assignment_reference,),
        )
        return self._responsibility(row) if row is not None else None

    def add_responsibility(self, responsibility: ResourceResponsibility) -> None:
        self._execute(
            """
            INSERT INTO napms_resource_catalogue.resource_responsibilities (
                assignment_reference, resource_reference, party_reference,
                party_kind, role, display_name, contact, valid_from, valid_to,
                provenance_reference, end_provenance_reference, version
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                responsibility.assignment_reference,
                responsibility.resource_reference,
                responsibility.party_reference,
                responsibility.party_kind.value,
                responsibility.role.value,
                responsibility.display_name,
                responsibility.contact,
                responsibility.valid_from,
                responsibility.valid_to,
                responsibility.provenance_reference,
                responsibility.end_provenance_reference,
                responsibility.version,
            ),
        )

    def save_responsibility(
        self,
        responsibility: ResourceResponsibility,
        *,
        expected_version: int,
    ) -> None:
        result = self._execute(
            """
            UPDATE napms_resource_catalogue.resource_responsibilities
            SET valid_to = %s,
                end_provenance_reference = %s,
                version = %s
            WHERE assignment_reference = %s
              AND resource_reference = %s
              AND version = %s
            """,
            (
                responsibility.valid_to,
                responsibility.end_provenance_reference,
                responsibility.version,
                responsibility.assignment_reference,
                responsibility.resource_reference,
                expected_version,
            ),
        )
        self._require_updated(result)

    def list_resources(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
        include_retired: bool,
    ) -> tuple[Resource, ...]:
        if search:
            pattern = f"%{search}%"
            rows = self._fetchall(
                """
                SELECT resource_reference, provenance_reference, display_name,
                       lifecycle_state, retirement_provenance_reference, version
                FROM napms_resource_catalogue.resources
                WHERE (%s OR lifecycle_state = 'Active')
                  AND (resource_reference ILIKE %s OR display_name ILIKE %s)
                ORDER BY display_name NULLS LAST, resource_reference
                OFFSET %s LIMIT %s
                """,
                (include_retired, pattern, pattern, offset, limit),
            )
        else:
            rows = self._fetchall(
                """
                SELECT resource_reference, provenance_reference, display_name,
                       lifecycle_state, retirement_provenance_reference, version
                FROM napms_resource_catalogue.resources
                WHERE (%s OR lifecycle_state = 'Active')
                ORDER BY display_name NULLS LAST, resource_reference
                OFFSET %s LIMIT %s
                """,
                (include_retired, offset, limit),
            )
        return tuple(self._resource(row) for row in rows)

    def list_effective_realizations(
        self,
        *,
        resource_reference: str,
        as_of,
    ) -> tuple[ResourceRealizationVersion, ...]:
        rows = self._realization_rows(
            """
            WHERE r.resource_reference = %s
              AND r.valid_from <= %s
              AND (r.valid_to IS NULL OR %s < r.valid_to)
            """,
            (resource_reference, as_of, as_of),
        )
        return self._realizations(rows)

    def list_effective_scope_affiliations(
        self,
        *,
        resource_reference: str,
        as_of,
    ) -> tuple[ResourceScopeAffiliation, ...]:
        rows = self._fetchall(
            """
            SELECT affiliation_reference, resource_reference, responsibility_scope,
                   valid_from, valid_to, provenance_reference,
                   end_provenance_reference, version
            FROM napms_resource_catalogue.resource_scope_affiliations
            WHERE resource_reference = %s
              AND valid_from <= %s
              AND (valid_to IS NULL OR %s < valid_to)
            ORDER BY responsibility_scope, affiliation_reference
            """,
            (resource_reference, as_of, as_of),
        )
        return tuple(self._affiliation(row) for row in rows)

    def list_effective_responsibilities(
        self,
        *,
        resource_reference: str,
        as_of,
    ) -> tuple[ResourceResponsibility, ...]:
        rows = self._fetchall(
            """
            SELECT assignment_reference, resource_reference, party_reference,
                   party_kind, role, display_name, contact, valid_from, valid_to,
                   provenance_reference, end_provenance_reference, version
            FROM napms_resource_catalogue.resource_responsibilities
            WHERE resource_reference = %s
              AND valid_from <= %s
              AND (valid_to IS NULL OR %s < valid_to)
            ORDER BY role, display_name, assignment_reference
            """,
            (resource_reference, as_of, as_of),
        )
        return tuple(self._responsibility(row) for row in rows)

    def find_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
    ) -> ResourceCatalogueCommandReceipt | None:
        row = self._fetchone(
            """
            SELECT command_kind, request_fingerprint, result_reference, result_version
            FROM napms_resource_catalogue.curation_command_receipts
            WHERE actor_id = %s AND idempotency_key = %s
            """,
            (actor_id, idempotency_key),
        )
        if row is None:
            return None
        return ResourceCatalogueCommandReceipt(
            command_kind=row[0],
            request_fingerprint=row[1],
            result_reference=row[2],
            result_version=row[3],
        )

    def record_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        receipt: ResourceCatalogueCommandReceipt,
    ) -> None:
        if self._pending_receipt is not None:
            raise ResourceCataloguePersistenceError(
                "only one command receipt may be staged"
            )
        self._pending_receipt = (actor_id, idempotency_key, receipt)

    def commit(self) -> None:
        try:
            if self._pending_receipt is not None:
                actor_id, idempotency_key, receipt = self._pending_receipt
                self._connection.execute(
                    """
                    INSERT INTO napms_resource_catalogue.curation_command_receipts (
                        actor_id, idempotency_key, command_kind,
                        request_fingerprint, result_reference, result_version
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        actor_id,
                        idempotency_key,
                        receipt.command_kind,
                        receipt.request_fingerprint,
                        receipt.result_reference,
                        receipt.result_version,
                    ),
                )
            self._connection.commit()
            self._pending_receipt = None
        except UniqueViolation as exc:
            self._connection.rollback()
            self._pending_receipt = None
            raise ResourceCatalogueIdempotencyConflict() from exc
        except PsycopgError as exc:
            self._pending_receipt = None
            raise ResourceCataloguePersistenceOutcomeUnknown() from exc

    def _realization_rows(self, where: str, params: tuple):
        return self._fetchall(
            f"""
            SELECT r.fact_reference, r.resource_reference, r.valid_from, r.valid_to,
                   r.provenance_reference, r.end_provenance_reference, r.version,
                   e.endpoint_reference, e.technical_address
            FROM napms_resource_catalogue.resource_realization_versions AS r
            JOIN napms_resource_catalogue.resource_endpoints AS e
              ON e.fact_reference = r.fact_reference
            {where}
            ORDER BY r.fact_reference, e.endpoint_reference, e.technical_address
            """,
            params,
        )

    def _realizations(self, rows) -> tuple[ResourceRealizationVersion, ...]:
        grouped: dict[str, list] = defaultdict(list)
        headers: dict[str, tuple] = {}
        for row in rows:
            headers[row[0]] = row[:7]
            grouped[row[0]].append(EndpointAddress(row[7], row[8]))
        values = []
        for fact_reference in sorted(headers):
            row = headers[fact_reference]
            try:
                values.append(
                    ResourceRealizationVersion(
                        fact_reference=row[0],
                        resource_reference=row[1],
                        endpoint_realizations=tuple(grouped[fact_reference]),
                        valid_from=row[2],
                        valid_to=row[3],
                        provenance_reference=row[4],
                        end_provenance_reference=row[5],
                        version=row[6],
                    )
                )
            except ResourceCatalogueInvariantError as exc:
                raise ResourceCataloguePersistenceError(
                    "invalid persisted Resource realization"
                ) from exc
        return tuple(values)

    def _require_updated(self, result) -> None:
        if result.rowcount != 1:
            self._connection.rollback()
            self._pending_receipt = None
            raise ResourceCatalogueConcurrencyConflict()

    def _execute(self, sql: str, params: tuple):
        try:
            return self._connection.execute(sql, params)
        except PsycopgError as exc:
            self._connection.rollback()
            self._pending_receipt = None
            raise ResourceCataloguePersistenceError() from exc

    def _fetchone(self, sql: str, params: tuple):
        try:
            return self._connection.execute(sql, params).fetchone()
        except PsycopgError as exc:
            raise ResourceCataloguePersistenceError() from exc

    def _fetchall(self, sql: str, params: tuple):
        try:
            return self._connection.execute(sql, params).fetchall()
        except PsycopgError as exc:
            raise ResourceCataloguePersistenceError() from exc

    @staticmethod
    def _resource(row) -> Resource:
        try:
            return Resource(
                resource_reference=row[0],
                provenance_reference=row[1],
                display_name=row[2],
                lifecycle_state=ResourceLifecycleState(row[3]),
                retirement_provenance_reference=row[4],
                version=row[5],
            )
        except (ValueError, ResourceCatalogueInvariantError) as exc:
            raise ResourceCataloguePersistenceError(
                "invalid persisted Resource"
            ) from exc

    @staticmethod
    def _affiliation(row) -> ResourceScopeAffiliation:
        try:
            return ResourceScopeAffiliation(
                affiliation_reference=row[0],
                resource_reference=row[1],
                responsibility_scope=row[2],
                valid_from=row[3],
                valid_to=row[4],
                provenance_reference=row[5],
                end_provenance_reference=row[6],
                version=row[7],
            )
        except ResourceCatalogueInvariantError as exc:
            raise ResourceCataloguePersistenceError(
                "invalid persisted Resource Scope Affiliation"
            ) from exc

    @staticmethod
    def _responsibility(row) -> ResourceResponsibility:
        try:
            return ResourceResponsibility(
                assignment_reference=row[0],
                resource_reference=row[1],
                party_reference=row[2],
                party_kind=ResponsiblePartyKind(row[3]),
                role=ResourceResponsibilityRole(row[4]),
                display_name=row[5],
                contact=row[6],
                valid_from=row[7],
                valid_to=row[8],
                provenance_reference=row[9],
                end_provenance_reference=row[10],
                version=row[11],
            )
        except (ValueError, ResourceCatalogueInvariantError) as exc:
            raise ResourceCataloguePersistenceError(
                "invalid persisted Resource Responsibility"
            ) from exc
