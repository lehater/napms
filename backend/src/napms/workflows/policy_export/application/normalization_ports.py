from typing import Protocol

from napms.workflows.policy_export.application.normalization_types import DcsTrafficAlternative


class DcsProjectionDecodeError(Exception):
    """The captured ACC payload cannot be translated to the accepted I6 schema."""


class DcsProjectionDecoder(Protocol):
    def decode(self, payload: bytes) -> tuple[DcsTrafficAlternative, ...]: ...
