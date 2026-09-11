from datetime import datetime, timezone
from uuid import UUID

import psycopg
from psycopg.types.json import Jsonb

from napms.contexts.application_catalogue.infrastructure.integrations.dcs_json_codec import JsonDcsProjectionCodec
from napms.bootstrap.config import load_local_seed_config
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)


_SCOPE = "local-demo"
_APPLICATION_CATALOGUE_SCOPE = "application-catalogue"
_RESOURCE_CATALOGUE_SCOPE = "resource-catalogue"
_APPLICATION = UUID("00000000-0000-0000-0000-000000000100")
_SOURCE_COMPONENT = UUID("00000000-0000-0000-0000-000000000201")
_DESTINATION_COMPONENT = UUID("00000000-0000-0000-0000-000000000202")
_SOURCE = UUID("00000000-0000-0000-0000-000000000101")
_DESTINATION = UUID("00000000-0000-0000-0000-000000000102")
_DCS = UUID("00000000-0000-0000-0000-000000000103")
_VALID_FROM = datetime(2020, 1, 1, tzinfo=timezone.utc)
_CHECKER_CAPTURED_AT = datetime(2026, 9, 10, 0, 0, tzinfo=timezone.utc)
_CHECKER_RECORDED_AT = datetime(2026, 9, 10, 0, 5, tzinfo=timezone.utc)

_AUTHORITY_ACTIONS = (
    "ProposeConnectivity",
    "ReadAccessRule",
    "SetRuleOperationalState",
    "SetRuleEffectiveWindow",
    "ReadEffectiveDesiredPolicy",
    "DeclareConnectivityRequirement",
    "ReadConnectivityRequirement",
    "SetConnectivityRequirementApplicability",
    "SetConnectivityRequirementJustification",
    "RetireConnectivityRequirement",
    "DecideConnectivity",
    "ReadConnectivityDecision",
    "ReadScopedConnectivity",
    "ReadNetworkOperatorRealization",
)

_CATALOGUE_AUTHORITIES = (
    ("CurateApplicationCatalogue", _APPLICATION_CATALOGUE_SCOPE),
    ("CurateResourceCatalogue", _RESOURCE_CATALOGUE_SCOPE),
)


def _dcs_payload() -> bytes:
    return JsonDcsProjectionCodec().encode(
        (
            DcsTrafficAlternative(
                protocol="tcp",
                source_ports=PortConstraint.any(),
                destination_ports=PortConstraint.ranged(PortRange(443, 443)),
                service_reference="https",
            ),
        )
    )


def _configured_entry(
    *,
    entry_id: str,
    reference: str,
    source_first: str,
    source_last: str,
    destination_first: str,
    destination_last: str,
) -> dict:
    return {
        "evidence_entry_id": entry_id,
        "predicate": {
            "source_addresses": {
                "kind": "Ranges",
                "ranges": [{"first": source_first, "last": source_last}],
            },
            "destination_addresses": {
                "kind": "Ranges",
                "ranges": [
                    {"first": destination_first, "last": destination_last}
                ],
            },
            "protocol": {"kind": "IpProtocolNumber", "number": 6},
            "source_ports": {"kind": "Any", "ranges": []},
            "destination_ports": {
                "kind": "Ranges",
                "ranges": [{"first": 443, "last": 443}],
            },
        },
        "action": "Permit",
        "source_entry_reference": reference,
        "source_position": 100,
    }


def _seed_checker_evidence(connection) -> None:
    snapshots = (
        (
            UUID("00000000-0000-0000-0000-000000000301"),
            "fw-demo-edge",
            "local-demo:checker:edge:20260910",
            _configured_entry(
                entry_id="00000000-0000-0000-0000-000000000311",
                reference="ACL-DEMO-100",
                source_first="10.10.10.0",
                source_last="10.10.10.255",
                destination_first="10.20.20.0",
                destination_last="10.20.20.255",
            ),
        ),
        (
            UUID("00000000-0000-0000-0000-000000000302"),
            "fw-demo-core",
            "local-demo:checker:core:20260910",
            _configured_entry(
                entry_id="00000000-0000-0000-0000-000000000312",
                reference="CORE-DEMO-200",
                source_first="10.10.0.0",
                source_last="10.10.255.255",
                destination_first="10.20.0.0",
                destination_last="10.20.255.255",
            ),
        ),
    )
    for evidence_set_id, device_reference, capture_reference, entry in snapshots:
        connection.execute(
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NULL, NULL, %s, %s)
            ON CONFLICT (evidence_set_id) DO NOTHING
            """,
            (
                evidence_set_id,
                "Configured",
                "local-demo-firewall-import",
                "access-list-snapshot",
                device_reference,
                capture_reference,
                "Instant",
                _CHECKER_CAPTURED_AT,
                _CHECKER_RECORDED_AT,
                Jsonb([entry]),
            ),
        )


def _seed_authority(connection, *, actor_id: str, action: str, scope: str) -> None:
    connection.execute(
        """
        INSERT INTO napms_authority.authority_assignments (
            reference_id,
            actor_id,
            action,
            scope,
            valid_from,
            valid_to,
            provenance_reference
        )
        VALUES (%s, %s, %s, %s, %s, NULL, %s)
        ON CONFLICT (reference_id) DO NOTHING
        """,
        (
            f"local-demo:{actor_id}:{action}",
            actor_id,
            action,
            scope,
            _VALID_FROM,
            f"local-demo:authority:{action}",
        ),
    )


def seed_local_demo(connection, *, actor_id: str) -> None:
    if not actor_id:
        raise ValueError("local demo actor_id must be non-empty")

    for action in _AUTHORITY_ACTIONS:
        _seed_authority(connection, actor_id=actor_id, action=action, scope=_SCOPE)
    for action, scope in _CATALOGUE_AUTHORITIES:
        _seed_authority(connection, actor_id=actor_id, action=action, scope=scope)

    connection.execute(
        """
        INSERT INTO napms_application_catalogue.applications (
            application_id,
            display_name,
            provenance_reference
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (application_id) DO UPDATE
        SET display_name = EXCLUDED.display_name
        """,
        (_APPLICATION, "Demo Commerce", "local-demo:application"),
    )

    for component_id, display_name, provenance in (
        (_SOURCE_COMPONENT, "Demo Web", "local-demo:source-component"),
        (_DESTINATION_COMPONENT, "Demo Orders", "local-demo:destination-component"),
    ):
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.components (
                component_id,
                application_id,
                display_name,
                provenance_reference
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (component_id) DO UPDATE
            SET display_name = EXCLUDED.display_name
            """,
            (component_id, _APPLICATION, display_name, provenance),
        )

    for deployment_id, component_id, display_name, provenance in (
        (
            _SOURCE,
            _SOURCE_COMPONENT,
            "Demo Web Frontend",
            "local-demo:source-deployment",
        ),
        (
            _DESTINATION,
            _DESTINATION_COMPONENT,
            "Demo Orders API",
            "local-demo:destination-deployment",
        ),
    ):
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.component_deployments (
                component_deployment_id,
                component_id,
                provenance_reference,
                display_name
            )
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (component_deployment_id) DO UPDATE
            SET display_name = EXCLUDED.display_name
            """,
            (deployment_id, component_id, provenance, display_name),
        )

    connection.execute(
        """
        INSERT INTO napms_application_catalogue.dcs_revisions (
            revision_id,
            source_component_deployment_id,
            destination_component_deployment_id,
            projection_payload,
            provenance_reference,
            display_name
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (revision_id) DO UPDATE
        SET display_name = EXCLUDED.display_name
        """,
        (
            _DCS,
            _SOURCE,
            _DESTINATION,
            _dcs_payload(),
            "local-demo:https-dcs",
            "HTTPS Orders API",
        ),
    )

    for reference_id, deployment_id, resource_reference in (
        ("local-demo:binding:source", _SOURCE, "local-demo-source"),
        ("local-demo:binding:destination", _DESTINATION, "local-demo-destination"),
    ):
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.deployment_resource_bindings (
                reference_id,
                component_deployment_id,
                resource_reference,
                valid_from,
                valid_to,
                provenance_reference
            )
            VALUES (%s, %s, %s, %s, NULL, %s)
            ON CONFLICT (reference_id) DO NOTHING
            """,
            (
                reference_id,
                deployment_id,
                resource_reference,
                _VALID_FROM,
                f"{reference_id}:provenance",
            ),
        )

    for resource_reference, fact_reference, endpoint_reference, address in (
        (
            "local-demo-source",
            "local-demo:source-fact",
            "local-demo-source:endpoint",
            "10.10.10.10",
        ),
        (
            "local-demo-destination",
            "local-demo:destination-fact",
            "local-demo-destination:endpoint",
            "10.20.20.20",
        ),
    ):
        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resources (
                resource_reference,
                provenance_reference
            )
            VALUES (%s, %s)
            ON CONFLICT (resource_reference) DO NOTHING
            """,
            (resource_reference, f"{resource_reference}:provenance"),
        )
        if resource_reference == "local-demo-source":
            connection.execute(
                """
                INSERT INTO napms_resource_catalogue.resource_scope_affiliations (
                    affiliation_reference,
                    resource_reference,
                    responsibility_scope,
                    valid_from,
                    valid_to,
                    provenance_reference
                )
                VALUES (%s, %s, %s, %s, NULL, %s)
                ON CONFLICT (affiliation_reference) DO NOTHING
                """,
                (
                    f"local-demo:scope-affiliation:{resource_reference}",
                    resource_reference,
                    _SCOPE,
                    _VALID_FROM,
                    f"local-demo:scope-affiliation:{resource_reference}:provenance",
                ),
            )

        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resource_realization_versions (
                fact_reference,
                resource_reference,
                valid_from,
                valid_to,
                provenance_reference
            )
            VALUES (%s, %s, %s, NULL, %s)
            ON CONFLICT (fact_reference) DO NOTHING
            """,
            (
                fact_reference,
                resource_reference,
                _VALID_FROM,
                f"{fact_reference}:provenance",
            ),
        )
        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resource_endpoints (
                fact_reference,
                endpoint_reference,
                technical_address
            )
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (fact_reference, endpoint_reference, address),
        )

    _seed_checker_evidence(connection)
    connection.commit()


def run() -> None:
    config = load_local_seed_config()
    with psycopg.connect(config.application.postgres.dsn) as connection:
        seed_local_demo(connection, actor_id=config.actor_id)
    print("NAPMS local demo seed applied")
