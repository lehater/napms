from napms.access_policy.application.ports import (
    AccessRulePersistenceError,
    AccessRuleRepository,
)
from napms.access_policy.domain.model import (
    OperationalState,
    RuleSemanticIdentity,
)
from napms.scoped_connectivity_inventory.application.model import (
    EffectiveAtAsOf,
    InteractionIdentity,
    PolicyOperationalState,
    PolicySummary,
    RuleExists,
)
from napms.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
    PolicySummaryReadResult,
)


class AccessPolicyScopedConnectivityAdapter:
    def __init__(self, *, rules: AccessRuleRepository) -> None:
        self._rules = rules

    def summarize_policy(
        self,
        *,
        identities,
        as_of,
    ) -> PolicySummaryReadResult:
        unique = tuple(dict.fromkeys(identities))
        if not unique:
            return PolicySummaryReadResult(DependencyAvailability.AVAILABLE, ())

        rule_identities = tuple(
            RuleSemanticIdentity(
                source_component_deployment_id=identity.source_component_deployment_id,
                destination_component_deployment_id=identity.destination_component_deployment_id,
                dcs_contract_revision_id=identity.dcs_contract_revision_id,
            )
            for identity in unique
        )
        try:
            rules = self._rules.find_inventory_summaries(rule_identities)
        except AccessRulePersistenceError:
            return PolicySummaryReadResult(DependencyAvailability.UNAVAILABLE)

        by_identity = {
            InteractionIdentity(
                rule.semantic_identity.source_component_deployment_id,
                rule.semantic_identity.destination_component_deployment_id,
                rule.semantic_identity.dcs_contract_revision_id,
            ): rule
            for rule in rules
        }

        items = []
        for identity in unique:
            rule = by_identity.get(identity)
            if rule is None:
                items.append(
                    PolicySummary(
                        identity=identity,
                        rule_exists=RuleExists.NO,
                        operational_state=PolicyOperationalState.UNAVAILABLE,
                        effective_at_as_of=EffectiveAtAsOf.UNAVAILABLE,
                    )
                )
                continue

            items.append(
                PolicySummary(
                    identity=identity,
                    rule_exists=RuleExists.YES,
                    operational_state=(
                        PolicyOperationalState.ACTIVE
                        if rule.operational_state is OperationalState.ACTIVE
                        else PolicyOperationalState.INACTIVE
                    ),
                    effective_at_as_of=(
                        EffectiveAtAsOf.YES
                        if rule.contributes_effect_at(as_of)
                        else EffectiveAtAsOf.NO
                    ),
                )
            )

        return PolicySummaryReadResult(
            DependencyAvailability.AVAILABLE,
            tuple(items),
        )
