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


def test_local_demo_seed_uses_actor_for_all_current_authority_actions():
    connection = FakeConnection()

    seed_local_demo(connection, actor_id="local-admin")

    authority_rows = [
        params
        for sql, params in connection.calls
        if "INSERT INTO napms_authority.authority_assignments" in sql
    ]
    assert {row[2] for row in authority_rows} == {
        "ProposeConnectivity",
        "ReadAccessRule",
        "SetRuleOperationalState",
        "SetRuleEffectiveWindow",
        "ReadEffectiveDesiredPolicy",
    }
    assert all(row[1] == "local-admin" for row in authority_rows)
    assert all(row[3] == "local-demo" for row in authority_rows)
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
    revision_id, source_id, destination_id, payload, provenance = dcs_rows[0]
    assert revision_id != source_id
    assert revision_id != destination_id
    assert source_id != destination_id
    assert b'"protocol":"tcp"' in payload
    assert b'"ranges":[[443,443]]' in payload
    assert provenance == "local-demo:https-dcs"


def test_local_demo_seed_requires_explicit_actor():
    with pytest.raises(ValueError):
        seed_local_demo(FakeConnection(), actor_id="")
