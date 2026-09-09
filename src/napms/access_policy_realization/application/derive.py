from datetime import datetime

from napms.access_policy_realization.domain.model import (
    DomainInteractionIdentity,
    KnowledgeGap,
)
from napms.access_policy_realization.domain.realization import (
    DesiredEnforcementPolicy,
    DesiredPolicyContribution,
    derive_desired_enforcement_policy,
)


class DeriveDesiredEnforcementPolicy:
    def execute(
        self,
        *,
        governance_scope: str,
        as_of: datetime,
        desired_interactions: tuple[
            DomainInteractionIdentity,
            ...,
        ],
        contributions: tuple[
            DesiredPolicyContribution,
            ...,
        ],
        knowledge_gaps: tuple[
            KnowledgeGap,
            ...,
        ] = (),
    ) -> DesiredEnforcementPolicy:
        return derive_desired_enforcement_policy(
            governance_scope=governance_scope,
            as_of=as_of,
            desired_interactions=desired_interactions,
            contributions=contributions,
            knowledge_gaps=knowledge_gaps,
        )
