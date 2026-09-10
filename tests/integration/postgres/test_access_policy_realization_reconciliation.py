import json
import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.application.materialize_rule import (
    MaterializationOutcome,
    MaterializeAllowedAccessRule,
    SubmitAccessRuleProposal,
)
from napms.access_policy.application.ports import (
    ConnectivityDecision,
    DecisionOutcome,
)
from napms.access_policy.application.set_operational_state import (
    OperationalStateMutationOutcome,
    SetAccessRuleOperationalState,
    SetRuleOperationalState,
)
from napms.access_policy.domain.model import (
    OperationalState,
)
from napms.access_policy_realization.application.ports import (
    ConfiguredPolicySemantics,
    ManagedReconciliationScopeContract,
)
from napms.access_policy_realization.domain.realization import (
    EnforcementTarget,
    ManagedReconciliationScope,
    ReconciliationStatus,
    RequiredSemanticChange,
)
from napms.application_catalogue.adapters.dcs_json_codec import (
    JsonDcsProjectionCodec,
)
from napms.composition.access_policy_realization_postgres import (
    open_access_policy_realization_scope,
)
from napms.composition.config import (
    ApplicationConfig,
    PostgresConfig,
)
from napms.composition.greenfield_postgres import (
    open_greenfield_scope,
)
from napms.composition.network_enforcement_placement_postgres import (
    open_network_enforcement_placement_scope,
)
from napms.composition.postgres_migrations import (
    apply_greenfield_migrations,
)
from napms.composition.technical_access_evidence_postgres import (
    open_technical_access_evidence_scope,
)
from napms.network_enforcement_placement.adapters.local_import import (
    LocalPlacementKnowledgeImportAdapter,
)
from napms.network_enforcement_placement.application.record import (
    RecordPlacementKnowledgeOutcome,
)
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)
from napms.technical_access_evidence.application.record import (
    RecordEvidenceOutcome,
    RecordEvidenceSet,
)
from napms.technical_access_evidence.domain.model import (
    AddressConstraint,
    AddressRange,
    EvidenceAction,
    EvidenceKind,
    EvidenceSourceReference,
    EvidenceTime,
    PortConstraint as TaePortConstraint,
    PortRange as TaePortRange,
    ProtocolSelector,
    SourceCaptureReference,
    SourceScopeReference,
    TechnicalAccessEntryPayload,
    TechnicalAccessPredicate,
)


pytestmark = pytest.mark.postgres

ACTOR = "actor-i20"
SCOPE = "scope-i20"
APPLICATION = UUID(int=2000)
SOURCE_PARENT_COMPONENT = UUID(int=2011)
DESTINATION_PARENT_COMPONENT = UUID(int=2012)
SOURCE_COMPONENT = UUID(int=2001)
DESTINATION_COMPONENT = UUID(int=2002)
DCS = UUID(int=2003)
RULE = UUID(int=2004)
TARGET_A = EnforcementTarget(
    UUID(int=2101),
    UUID(int=2111),
)
TARGET_B = EnforcementTarget(
    UUID(int=2201),
    UUID(int=2211),
)
SOURCE_IP = "198.51.100.10"
DESTINATION_IP = "203.0.113.20"
AS_OF = datetime(
    2026,
    9,
    9,
    12,
    tzinfo=timezone.utc,
)
SWITCH = AS_OF + timedelta(hours=1)
PROPOSAL_TIME = AS_OF - timedelta(hours=2)
VALID_FROM = AS_OF - timedelta(days=1)
VALID_TO = AS_OF + timedelta(days=1)
EVIDENCE_SOURCE = EvidenceSourceReference(
    "controller",
    "fw-a",
)
EVIDENCE_SCOPE = SourceScopeReference(
    "policy-package-a"
)


class AllowedDecision:
    def obtain(
        self,
        *,
        subject,
        governance_scope,
        as_of,
    ):
        return ConnectivityDecision(
            outcome=DecisionOutcome.ALLOWED,
            subject=subject,
            governance_scope=governance_scope,
            valid_from=as_of,
            decision_reference=(
                "decision-i20"
            ),
        )


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get(
        "NAPMS_TEST_POSTGRES_DSN"
    )
    if not dsn:
        pytest.skip(
            "NAPMS_TEST_POSTGRES_DSN is required "
            "for PostgreSQL integration tests"
        )
    return dsn


@pytest.fixture(scope="session")
def config(postgres_dsn):
    value = ApplicationConfig(
        environment="local-dev",
        postgres=PostgresConfig(
            postgres_dsn
        ),
    )
    apply_greenfield_migrations(
        value
    )
    return value


@pytest.fixture(autouse=True)
def clean(postgres_dsn, config):
    with psycopg.connect(
        postgres_dsn,
        autocommit=True,
    ) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_access_policy.access_rule_effective_window_changes,
                napms_access_policy.access_rule_effective_windows,
                napms_access_policy.access_rule_state_transitions,
                napms_access_policy.access_rules
            """
        )
        connection.execute(
            "TRUNCATE TABLE "
            "napms_authority.authority_assignments"
        )
        connection.execute(
            """
            TRUNCATE TABLE
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments,
                napms_application_catalogue.components,
                napms_application_catalogue.applications
            CASCADE
            """
        )
        connection.execute(
            """
            TRUNCATE TABLE
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resources
            CASCADE
            """
        )
        connection.execute(
            """
            TRUNCATE TABLE
                napms_technical_access_evidence.evidence_sets
            """
        )
        connection.execute(
            """
            TRUNCATE TABLE
                napms_network_enforcement_placement.knowledge_captures
            """
        )


def dcs_payload():
    return JsonDcsProjectionCodec().encode(
        (
            DcsTrafficAlternative(
                protocol="tcp",
                source_ports=(
                    PortConstraint.any()
                ),
                destination_ports=(
                    PortConstraint.ranged(
                        PortRange(
                            443,
                            443,
                        )
                    )
                ),
                service_reference="https",
            ),
        )
    )


def seed_domain(postgres_dsn):
    with psycopg.connect(
        postgres_dsn
    ) as connection:
        for (
            reference,
            action,
            provenance,
        ) in (
            (
                "authority-propose-i20",
                "ProposeConnectivity",
                "authority-propose-prov-i20",
            ),
            (
                "authority-read-i20",
                "ReadEffectiveDesiredPolicy",
                "authority-read-prov-i20",
            ),
            (
                "authority-mutate-i20",
                "SetRuleOperationalState",
                "authority-mutate-prov-i20",
            ),
        ):
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
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    reference,
                    ACTOR,
                    action,
                    SCOPE,
                    VALID_FROM,
                    VALID_TO,
                    provenance,
                ),
            )

        connection.execute(
            """
            INSERT INTO napms_application_catalogue.applications (
                application_id,
                display_name,
                provenance_reference
            )
            VALUES (%s, %s, %s)
            """,
            (APPLICATION, "I20 test application", "application-prov-i20"),
        )
        for component_id, display_name, provenance in (
            (
                SOURCE_PARENT_COMPONENT,
                "Source component",
                "source-parent-component-prov",
            ),
            (
                DESTINATION_PARENT_COMPONENT,
                "Destination component",
                "destination-parent-component-prov",
            ),
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
                """,
                (
                    component_id,
                    APPLICATION,
                    display_name,
                    provenance,
                ),
            )

        for deployment, component_id, provenance in (
            (
                SOURCE_COMPONENT,
                SOURCE_PARENT_COMPONENT,
                "source-component-prov",
            ),
            (
                DESTINATION_COMPONENT,
                DESTINATION_PARENT_COMPONENT,
                "destination-component-prov",
            ),
        ):
            connection.execute(
                """
                INSERT INTO napms_application_catalogue.component_deployments (
                    component_deployment_id,
                    component_id,
                    provenance_reference
                )
                VALUES (%s, %s, %s)
                """,
                (
                    deployment,
                    component_id,
                    provenance,
                ),
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
            """,
            (
                DCS,
                SOURCE_COMPONENT,
                DESTINATION_COMPONENT,
                dcs_payload(),
                "dcs-prov-i20",
            ),
        )
        for row in (
            (
                "binding-source-i20",
                SOURCE_COMPONENT,
                "resource-source-i20",
                "binding-source-prov-i20",
            ),
            (
                "binding-destination-i20",
                DESTINATION_COMPONENT,
                "resource-destination-i20",
                "binding-destination-prov-i20",
            ),
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
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    row[0],
                    row[1],
                    row[2],
                    VALID_FROM,
                    VALID_TO,
                    row[3],
                ),
            )

        for resource in (
            "resource-source-i20",
            "resource-destination-i20",
        ):
            connection.execute(
                """
                INSERT INTO napms_resource_catalogue.resources (
                    resource_reference,
                    provenance_reference
                )
                VALUES (%s, %s)
                """,
                (
                    resource,
                    "resource-prov:"
                    + resource,
                ),
            )
        for (
            fact,
            resource,
            endpoint,
            address,
        ) in (
            (
                "source-fact-i20",
                "resource-source-i20",
                "source-endpoint-i20",
                SOURCE_IP,
            ),
            (
                "destination-fact-i20",
                "resource-destination-i20",
                "destination-endpoint-i20",
                DESTINATION_IP,
            ),
        ):
            connection.execute(
                """
                INSERT INTO napms_resource_catalogue.resource_realization_versions (
                    fact_reference,
                    resource_reference,
                    valid_from,
                    valid_to,
                    provenance_reference
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    fact,
                    resource,
                    VALID_FROM,
                    VALID_TO,
                    "realization-prov:"
                    + fact,
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
                """,
                (
                    fact,
                    endpoint,
                    address,
                ),
            )
        connection.commit()


def materialize_rule(config):
    with open_greenfield_scope(
        config
    ) as scope:
        result = MaterializeAllowedAccessRule(
            authority=scope.authority,
            catalogue=scope.proposal_catalogue,
            decisions=AllowedDecision(),
            rules=scope.access_rules,
            new_rule_id=lambda: RULE,
        ).execute(
            SubmitAccessRuleProposal(
                actor_id=ACTOR,
                authority_scope=SCOPE,
                effective_time=(
                    PROPOSAL_TIME
                ),
                source_component_deployment_id=(
                    SOURCE_COMPONENT
                ),
                destination_component_deployment_id=(
                    DESTINATION_COMPONENT
                ),
                dcs_contract_revision_id=DCS,
            )
        )
    assert (
        result.outcome
        is MaterializationOutcome.MATERIALIZED
    )


def placement_document(
    *,
    target,
    capture_reference,
    valid_from,
    valid_until,
):
    return {
        "source_reference": (
            "i20-topology"
        ),
        "source_capture_reference": (
            capture_reference
        ),
        "validity": {
            "valid_from": (
                valid_from.isoformat()
            ),
            "valid_until": (
                valid_until.isoformat()
                if valid_until
                is not None
                else None
            ),
        },
        "relation": {
            "source_ip": SOURCE_IP,
            "destination_ip": (
                DESTINATION_IP
            ),
        },
        "path": {
            "path_reference": (
                "path:"
                + capture_reference
            ),
            "traversal_points": [
                {
                    "provider_realization": {
                        "namespace": (
                            "lab"
                        ),
                        "reference": (
                            "device:"
                            + str(
                                target.logical_firewall_id
                            )
                        ),
                    },
                    "path_attachment": {
                        "namespace": (
                            "lab"
                        ),
                        "reference": (
                            "edge:"
                            + str(
                                target.enforcement_attachment_id
                            )
                        ),
                    },
                    "provenance": [
                        "route:"
                        + capture_reference
                    ],
                }
            ],
            "provenance": [
                "path-prov:"
                + capture_reference
            ],
        },
        "no_forwarding_path": None,
        "logical_firewalls": [
            {
                "logical_firewall_id": (
                    str(
                        target.logical_firewall_id
                    )
                ),
                "validity": {
                    "valid_from": (
                        valid_from.isoformat()
                    ),
                    "valid_until": (
                        valid_until.isoformat()
                        if valid_until
                        is not None
                        else None
                    ),
                },
                "provenance": [
                    "lf:"
                    + str(
                        target.logical_firewall_id
                    )
                ],
            }
        ],
        "correspondences": [
            {
                "logical_firewall_id": (
                    str(
                        target.logical_firewall_id
                    )
                ),
                "provider_realization": {
                    "namespace": "lab",
                    "reference": (
                        "device:"
                        + str(
                            target.logical_firewall_id
                        )
                    ),
                },
                "validity": {
                    "valid_from": (
                        valid_from.isoformat()
                    ),
                    "valid_until": (
                        valid_until.isoformat()
                        if valid_until
                        is not None
                        else None
                    ),
                },
                "provenance": [
                    "corr:"
                    + str(
                        target.logical_firewall_id
                    )
                ],
            }
        ],
        "attachments": [
            {
                "enforcement_attachment_id": (
                    str(
                        target.enforcement_attachment_id
                    )
                ),
                "logical_firewall_id": (
                    str(
                        target.logical_firewall_id
                    )
                ),
                "provider_realization": {
                    "namespace": "lab",
                    "reference": (
                        "device:"
                        + str(
                            target.logical_firewall_id
                        )
                    ),
                },
                "path_attachment": {
                    "namespace": "lab",
                    "reference": (
                        "edge:"
                        + str(
                            target.enforcement_attachment_id
                        )
                    ),
                },
                "validity": {
                    "valid_from": (
                        valid_from.isoformat()
                    ),
                    "valid_until": (
                        valid_until.isoformat()
                        if valid_until
                        is not None
                        else None
                    ),
                },
                "provenance": [
                    "attachment:"
                    + str(
                        target.enforcement_attachment_id
                    )
                ],
            }
        ],
        "complete_for_pair": True,
        "complete_for_attachments": True,
    }


def record_placement(
    config,
    *,
    target,
    capture_reference,
    valid_from,
    valid_until,
):
    command = (
        LocalPlacementKnowledgeImportAdapter()
        .normalize(
            json.dumps(
                placement_document(
                    target=target,
                    capture_reference=(
                        capture_reference
                    ),
                    valid_from=valid_from,
                    valid_until=valid_until,
                )
            )
        )
    )
    with (
        open_network_enforcement_placement_scope(
            config
        )
    ) as scope:
        result = (
            scope.record_placement_knowledge
            .execute(command)
        )
    assert result.outcome in (
        RecordPlacementKnowledgeOutcome.RECORDED,
        RecordPlacementKnowledgeOutcome.RESOLVED,
    )


def configured_predicate(
    destination_port,
):
    return TechnicalAccessPredicate(
        source_addresses=(
            AddressConstraint.ranged(
                AddressRange(
                    SOURCE_IP,
                    SOURCE_IP,
                )
            )
        ),
        destination_addresses=(
            AddressConstraint.ranged(
                AddressRange(
                    DESTINATION_IP,
                    DESTINATION_IP,
                )
            )
        ),
        protocol=(
            ProtocolSelector.ip_protocol(
                6
            )
        ),
        source_ports=(
            TaePortConstraint.any()
        ),
        destination_ports=(
            TaePortConstraint.ranged(
                TaePortRange(
                    destination_port,
                    destination_port,
                )
            )
        ),
    )


def record_evidence(
    config,
    *,
    capture_reference,
    ports,
):
    entries = tuple(
        TechnicalAccessEntryPayload(
            predicate=(
                configured_predicate(
                    port
                )
            ),
            action=EvidenceAction.PERMIT,
            source_entry_reference=(
                "configured:"
                + str(port)
            ),
            source_position=index,
        )
        for index, port
        in enumerate(ports)
    )
    with (
        open_technical_access_evidence_scope(
            config
        )
    ) as scope:
        result = (
            scope.record_technical_access_evidence
            .execute(
                RecordEvidenceSet(
                    kind=(
                        EvidenceKind.CONFIGURED
                    ),
                    source=EVIDENCE_SOURCE,
                    source_scope=(
                        EVIDENCE_SCOPE
                    ),
                    source_capture_reference=(
                        SourceCaptureReference(
                            capture_reference
                        )
                    ),
                    evidence_time=(
                        EvidenceTime.instant(
                            AS_OF
                        )
                    ),
                    entries=entries,
                )
            )
        )
    assert result.outcome in (
        RecordEvidenceOutcome.RECORDED,
        RecordEvidenceOutcome.RESOLVED,
    )
    assert result.evidence_set is not None
    return result.evidence_set.evidence_set_id


def contract(
    target,
    *,
    complete=True,
):
    return ManagedReconciliationScopeContract(
        managed_scope=(
            ManagedReconciliationScope(
                SCOPE,
                target,
                "contract:i20",
            )
        ),
        evidence_source_namespace=(
            EVIDENCE_SOURCE.namespace
        ),
        evidence_source_reference=(
            EVIDENCE_SOURCE.reference
        ),
        evidence_source_scope_reference=(
            EVIDENCE_SCOPE.value
        ),
        semantics=(
            ConfiguredPolicySemantics.EFFECTIVE_PERMIT_SET
        ),
        complete_for_managed_scope=(
            complete
        ),
        provenance_reference=(
            "contract-provenance:i20"
        ),
    )


def test_postgres_reconciliation_proves_complete_semantic_delta_set(
    postgres_dsn,
    config,
):
    seed_domain(postgres_dsn)
    materialize_rule(config)
    record_placement(
        config,
        target=TARGET_A,
        capture_reference="placement-a",
        valid_from=VALID_FROM,
        valid_until=VALID_TO,
    )
    noop_id = record_evidence(
        config,
        capture_reference="configured-noop",
        ports=(443,),
    )
    add_id = record_evidence(
        config,
        capture_reference="configured-empty",
        ports=(),
    )
    replace_id = record_evidence(
        config,
        capture_reference="configured-replace",
        ports=(80,),
    )

    with (
        open_access_policy_realization_scope(
            config,
            actor_id=ACTOR,
        )
    ) as scope:
        desired = scope.derive_desired.execute(
            governance_scope=SCOPE,
            as_of=AS_OF,
        )
        assert desired.regions_for(
            TARGET_A
        )

        results = {}
        for name, evidence_id in (
            ("noop", noop_id),
            ("add", add_id),
            ("replace", replace_id),
        ):
            configured = (
                scope.build_configured.execute(
                    evidence_set_id=(
                        evidence_id
                    ),
                    contract=contract(
                        TARGET_A
                    ),
                    as_of=AS_OF,
                )
            )
            results[name] = (
                scope.reconcile.execute(
                    desired=desired,
                    configured=configured,
                )
            )

    assert (
        results["noop"].status
        is ReconciliationStatus.SATISFIED
    )
    assert (
        results["noop"].required_change
        is RequiredSemanticChange.NO_OP
    )
    assert (
        results["add"].required_change
        is RequiredSemanticChange.ADD
    )
    assert (
        results["replace"].required_change
        is RequiredSemanticChange.REPLACE
    )
    assert results["replace"].missing
    assert results["replace"].extra

    with open_greenfield_scope(
        config
    ) as owner:
        mutation = (
            SetAccessRuleOperationalState(
                authority=owner.authority,
                rules=owner.access_rules,
            ).execute(
                SetRuleOperationalState(
                    rule_id=RULE,
                    target_state=(
                        OperationalState.INACTIVE
                    ),
                    actor_id=ACTOR,
                    effective_time=AS_OF,
                )
            )
        )
    assert (
        mutation.outcome
        is OperationalStateMutationOutcome.UPDATED
    )

    with (
        open_access_policy_realization_scope(
            config,
            actor_id=ACTOR,
        )
    ) as scope:
        desired_empty = (
            scope.derive_desired.execute(
                governance_scope=SCOPE,
                as_of=AS_OF,
            )
        )
        assert desired_empty.intents == ()
        configured = (
            scope.build_configured.execute(
                evidence_set_id=noop_id,
                contract=contract(
                    TARGET_A
                ),
                as_of=AS_OF,
            )
        )
        removed = scope.reconcile.execute(
            desired=desired_empty,
            configured=configured,
        )

    assert (
        removed.status
        is ReconciliationStatus.DRIFT
    )
    assert (
        removed.required_change
        is RequiredSemanticChange.REMOVE
    )
    assert removed.extra


def test_postgres_incomplete_configured_contract_is_unknown(
    postgres_dsn,
    config,
):
    seed_domain(postgres_dsn)
    materialize_rule(config)
    record_placement(
        config,
        target=TARGET_A,
        capture_reference="placement-a",
        valid_from=VALID_FROM,
        valid_until=VALID_TO,
    )
    evidence_id = record_evidence(
        config,
        capture_reference="configured-noop",
        ports=(443,),
    )

    with (
        open_access_policy_realization_scope(
            config,
            actor_id=ACTOR,
        )
    ) as scope:
        desired = scope.derive_desired.execute(
            governance_scope=SCOPE,
            as_of=AS_OF,
        )
        configured = (
            scope.build_configured.execute(
                evidence_set_id=evidence_id,
                contract=contract(
                    TARGET_A,
                    complete=False,
                ),
                as_of=AS_OF,
            )
        )
        result = scope.reconcile.execute(
            desired=desired,
            configured=configured,
        )

    assert (
        result.status
        is ReconciliationStatus.UNKNOWN
    )
    assert result.required_change is None


def test_postgres_nep_temporal_change_moves_desired_target(
    postgres_dsn,
    config,
):
    seed_domain(postgres_dsn)
    materialize_rule(config)
    record_placement(
        config,
        target=TARGET_A,
        capture_reference="placement-a",
        valid_from=VALID_FROM,
        valid_until=SWITCH,
    )
    record_placement(
        config,
        target=TARGET_B,
        capture_reference="placement-b",
        valid_from=SWITCH,
        valid_until=VALID_TO,
    )

    with (
        open_access_policy_realization_scope(
            config,
            actor_id=ACTOR,
        )
    ) as scope:
        before = scope.derive_desired.execute(
            governance_scope=SCOPE,
            as_of=AS_OF,
        )
        after = scope.derive_desired.execute(
            governance_scope=SCOPE,
            as_of=SWITCH,
        )

    assert before.regions_for(
        TARGET_A
    )
    assert before.regions_for(
        TARGET_B
    ) == ()
    assert after.regions_for(
        TARGET_A
    ) == ()
    assert after.regions_for(
        TARGET_B
    )
    assert (
        before.desired_interactions
        == after.desired_interactions
    )
