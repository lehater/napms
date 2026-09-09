from datetime import datetime
from typing import Protocol

from napms.access_policy_realization.domain.model import (
    DomainKnowledgeSnapshot,
    TechnicalAccessPredicate,
)


class DomainKnowledgePort(Protocol):
    def load_for(
        self,
        *,
        predicate: TechnicalAccessPredicate,
        as_of: datetime,
    ) -> DomainKnowledgeSnapshot: ...
