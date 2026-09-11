from dataclasses import dataclass
from datetime import datetime

from napms.contexts.access_policy.domain.model import (
    EffectiveWindow,
    OperationalState,
    RuleSemanticIdentity,
)


@dataclass(frozen=True, slots=True)
class AccessRuleInventorySnapshot:
    semantic_identity: RuleSemanticIdentity
    operational_state: OperationalState
    effective_window: EffectiveWindow | None

    def contributes_effect_at(self, as_of: datetime) -> bool:
        if self.operational_state is not OperationalState.ACTIVE:
            return False
        return self.effective_window is None or self.effective_window.contains(as_of)
