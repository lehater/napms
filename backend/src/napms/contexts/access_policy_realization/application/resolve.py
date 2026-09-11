from datetime import datetime

from napms.contexts.access_policy_realization.application.ports import (
    DomainKnowledgePort,
)
from napms.contexts.access_policy_realization.domain.algebra import (
    resolve_domain_access,
)
from napms.contexts.access_policy_realization.domain.model import (
    DomainAccessResolution,
    InputProvenance,
    ProtocolSelectorKind,
    TechnicalAccessPredicate,
    require_aware,
)


class ResolveTechnicalAccess:
    def __init__(
        self,
        *,
        domain_knowledge: DomainKnowledgePort,
    ) -> None:
        self._domain_knowledge = domain_knowledge

    def execute(
        self,
        *,
        predicate: TechnicalAccessPredicate,
        as_of: datetime,
        input_provenance: InputProvenance = (
            InputProvenance()
        ),
    ) -> DomainAccessResolution:
        require_aware(as_of)
        if (
            predicate.protocol.kind
            is ProtocolSelectorKind.ANY
        ):
            return resolve_domain_access(
                predicate,
                as_of=as_of,
                knowledge=None,
                input_provenance=input_provenance,
            )
        knowledge = (
            self._domain_knowledge.load_for(
                predicate=predicate,
                as_of=as_of,
            )
        )
        return resolve_domain_access(
            predicate,
            as_of=as_of,
            knowledge=knowledge,
            input_provenance=input_provenance,
        )
