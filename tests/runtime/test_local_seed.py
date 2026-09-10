from uuid import UUID

import pytest

from napms.runtime.local_seed import seed_local_demo


class FakeConnection:
    def __init__(self):
        self.calls = []
        self.commits = 0

    def execute(self, sql, params=None):
        self.calls.append((sql, params))

    def commit(self):
        self.commits += 1


def test_local_demo_seed_uses_actor_and_correct_authority_scopes():
    connection = FakeConnection()

    seed_local_demo(connection, actor_id="local-admin")

    authority_rows = [
        params
        for sql, params in connection.calls
        if "INSERT INTO napms_authority.authority_assignments" in sql
    ]
    by_action = {row[2]: row for row in authority_rows}
    assert set(by_action) == {
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
        "CurateApplicationCatalogue",
        "CurateResourceCatalogue",
    }
    assert all(row[1] == "local-admin" for row in authority_rows)
    assert by_action["CurateApplicationCatalogue"][3] == "application-catalogue"
    assert by_action["CurateResourceCatalogue"][3] == "resource-catalogue"
    assert all(
        row[3] == "local-demo"
        for action, row in by_action.items()
        if action not in {"CurateApplicationCatalogue", "CurateResourceCatalogue"}
    )
    assert connection.commits == 1


def test_local_demo_seed_contains_one_directed_https_interaction():
    connection = FakeConnection()

    seed_local_demo(connection, actor_id="local-admin")

    dcs_rows = [
        params
        for sql, params in connection.calls
        if "INSERT INTO napms_application_catalogue.dcs_revisions" in sql
    ]
    assert len(dcs_rows) == 1
    revision_id, source_id, destination_id, payload, provenance, display_name = dcs_rows[0]
    assert revision_id != source_id
    assert revision_id != destination_id
    assert source_id != destination_id
    assert b'"protocol":"tcp"' in payload
    assert b'"ranges":[[443,443]]' in payload
    assert provenance == "local-demo:https-dcs"
    assert display_name == "HTTPS Orders API"


def test_local_demo_seed_requires_explicit_actor():
    with pytest.raises(ValueError):
        seed_local_demo(FakeConnection(), actor_id="")


def test_local_demo_seed_contains_explicit_application_component_deployment_hierarchy():
    connection = FakeConnection()

    seed_local_demo(connection, actor_id="local-admin")

    application_rows = [
        params
        for sql, params in connection.calls
        if "INSERT INTO napms_application_catalogue.applications" in sql
    ]
    component_rows = [
        params
        for sql, params in connection.calls
        if "INSERT INTO napms_application_catalogue.components" in sql
    ]
    deployment_rows = [
        params
        for sql, params in connection.calls
        if "INSERT INTO napms_application_catalogue.component_deployments" in sql
    ]

    application_id = UUID("00000000-0000-0000-0000-000000000100")
    source_component = UUID("00000000-0000-0000-0000-000000000201")
    destination_component = UUID("00000000-0000-0000-0000-000000000202")
    source_deployment = UUID("00000000-0000-0000-0000-000000000101")
    destination_deployment = UUID("00000000-0000-0000-0000-000000000102")

    assert application_rows == [
        (application_id, "Demo Commerce", "local-demo:application")
    ]
    assert {(row[0], row[1], row[2]) for row in component_rows} == {
        (source_component, application_id, "Demo Web"),
        (destination_component, application_id, "Demo Orders"),
    }
    assert {(row[0], row[1], row[3]) for row in deployment_rows} == {
        (source_deployment, source_component, "Demo Web Frontend"),
        (destination_deployment, destination_component, "Demo Orders API"),
    }


def test_local_demo_seed_affiliates_only_local_resource_with_scope():
    connection = FakeConnection()

    seed_local_demo(connection, actor_id="local-admin")

    affiliation_rows = [
        params
        for sql, params in connection.calls
        if "INSERT INTO napms_resource_catalogue.resource_scope_affiliations" in sql
    ]
    assert len(affiliation_rows) == 1
    assert affiliation_rows[0][1] == "local-demo-source"
    assert affiliation_rows[0][2] == "local-demo"
