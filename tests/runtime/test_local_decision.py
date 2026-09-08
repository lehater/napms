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

    result = LocalDevAllowedConnectivityDecisionAdapter().obtain(subject=subject)

    assert result.outcome is DecisionOutcome.ALLOWED
    assert result.subject == subject
    assert result.decision_reference == "local-dev:allowed"
