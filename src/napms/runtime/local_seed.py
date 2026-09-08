from datetime import datetime, timezone
from uuid import UUID

import psycopg

from napms.application_catalogue.adapters.dcs_json_codec import JsonDcsProjectionCodec
from napms.runtime.config import load_local_seed_config
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)


_SCOPE = "local-demo"
_SOURCE = UUID("00000000-0000-0000-0000-000000000101")
_DESTINATION = UUID("00000000-0000-0000-0000-000000000102")
_DCS = UUID("00000000-0000-0000-0000-000000000103")
_VALID_FROM = datetime(2020, 1, 1, tzinfo=timezone.utc)

_AUTHORITY_ACTIONS = (
    "ProposeConnectivity",
    "ReadAccessRule",
    "SetRuleOperationalState",
    "SetRuleEffectiveWindow",
    "ReadEffectiveDesiredPolicy",
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


def seed_local_demo(connection, *, actor_id: str) -> None:
    if not actor_id:
        raise ValueError("local demo actor_id must be non-empty")

    for action in _AUTHORITY_ACTIONS:
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
                _SCOPE,
                _VALID_FROM,
                f"local-demo:authority:{action}",
            ),
        )

    for deployment_id, provenance in (
        (_SOURCE, "local-demo:source-deployment"),
        (_DESTINATION, "local-demo:destination-deployment"),
    ):
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.component_deployments (
                component_deployment_id,
                provenance_reference
            )
            VALUES (%s, %s)
            ON CONFLICT (component_deployment_id) DO NOTHING
            """,
            (deployment_id, provenance),
        )

    connection.execute(
        """
        INSERT INTO napms_application_catalogue.dcs_revisions (
            revision_id,
            source_component_deployment_id,
            destination_component_deployment_id,
            projection_payload,
            provenance_reference
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (revision_id) DO NOTHING
        """,
        (
            _DCS,
            _SOURCE,
            _DESTINATION,
            _dcs_payload(),
            "local-demo:https-dcs",
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

    connection.commit()


def run() -> None:
    config = load_local_seed_config()
    with psycopg.connect(config.application.postgres.dsn) as connection:
        seed_local_demo(connection, actor_id=config.actor_id)
    print("NAPMS local demo seed applied")
