from napms.contexts.access_policy.application.ports import (
    AccessRulePersistenceError,
    AccessRuleRepository,
)
from napms.contexts.access_policy.domain.model import RuleSemanticIdentity
from napms.requirement_policy_alignment.application.model import (
    AlignmentSemanticIdentity,
)
from napms.requirement_policy_alignment.application.ports import (
    PolicyCoverageOutcome,
)


class AccessPolicyAlignmentAdapter:
    def __init__(self, *, rules: AccessRuleRepository) -> None:
        self._rules = rules

    def check_exact_coverage(
        self,
        *,
        semantic_identity: AlignmentSemanticIdentity,
        as_of,
    ) -> PolicyCoverageOutcome:
        identity = RuleSemanticIdentity(
            source_component_deployment_id=(
                semantic_identity.source_component_deployment_id
            ),
            destination_component_deployment_id=(
                semantic_identity.destination_component_deployment_id
            ),
            dcs_contract_revision_id=semantic_identity.dcs_contract_revision_id,
        )
        try:
            rule = self._rules.find_by_identity(identity)
        except AccessRulePersistenceError:
            return PolicyCoverageOutcome.UNKNOWN

        if rule is None:
            return PolicyCoverageOutcome.UNCOVERED
        if rule.semantic_identity != identity:
            return PolicyCoverageOutcome.UNKNOWN
        return (
            PolicyCoverageOutcome.COVERED
            if rule.contributes_effect_at(as_of)
            else PolicyCoverageOutcome.UNCOVERED
        )
