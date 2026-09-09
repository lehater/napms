from datetime import datetime, timezone
from uuid import UUID

from napms.access_policy.application.ports import DecisionOutcome
from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.runtime.local_decision import LocalDevAllowedConnectivityDecisionAdapter


def test_local_dev_decision_adapter_allows_exact_subject_with_explicit_provenance():
    subject = RuleSemanticIdentity(
        source_component_deployment_id=UUID(int=1),
        destination_component_deployment_id=UUID(int=2),
        dcs_contract_revision_id=UUID(int=3),
    )

    as_of = datetime(2026, 9, 9, tzinfo=timezone.utc)
    result = LocalDevAllowedConnectivityDecisionAdapter().obtain(
        subject=subject,
        governance_scope="scope-1",
        as_of=as_of,
    )

    assert result.outcome is DecisionOutcome.ALLOWED
    assert result.subject == subject
    assert result.governance_scope == "scope-1"
    assert result.valid_from == as_of
    assert result.valid_until is None
    assert result.decision_reference == "local-dev:allowed"
