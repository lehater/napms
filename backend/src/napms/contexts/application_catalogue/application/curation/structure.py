"""Compatibility exports for pre-M5 Application Catalogue structure mutation imports."""

from napms.contexts.application_catalogue.application.curation.application_structure import (
    ApplicationMutationResult,
    RenameApplication,
    RenameApplicationCommand,
    RetireApplication,
    RetireApplicationCommand,
)
from napms.contexts.application_catalogue.application.curation.component_structure import (
    ComponentMutationResult,
    CreateComponent,
    CreateComponentCommand,
    RenameComponent,
    RenameComponentCommand,
    RetireComponent,
    RetireComponentCommand,
)
from napms.contexts.application_catalogue.application.curation.mutation import (
    CatalogueMutationOutcome,
)

__all__ = [
    "ApplicationMutationResult",
    "CatalogueMutationOutcome",
    "ComponentMutationResult",
    "CreateComponent",
    "CreateComponentCommand",
    "RenameApplication",
    "RenameApplicationCommand",
    "RenameComponent",
    "RenameComponentCommand",
    "RetireApplication",
    "RetireApplicationCommand",
    "RetireComponent",
    "RetireComponentCommand",
]
