"""Compatibility facade for temporal Catalogue HTTP during I32 migration.

Feature endpoints live in their semantic owners; this module only aggregates routers.
"""

from fastapi import APIRouter

from napms.application_catalogue.adapters.http.legacy_temporal import (
    create_application_catalogue_temporal_router,
)
from napms.resource_catalogue.adapters.http.temporal import (
    create_resource_catalogue_temporal_router,
)


def create_catalogue_temporal_curation_router(**kwargs) -> APIRouter:
    router = APIRouter()
    router.include_router(create_resource_catalogue_temporal_router(**kwargs))
    router.include_router(create_application_catalogue_temporal_router(**kwargs))
    return router
