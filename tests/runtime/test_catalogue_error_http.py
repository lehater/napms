from fastapi import FastAPI
from fastapi.testclient import TestClient

from napms.application_catalogue.domain.model import CatalogueInvariantError
from napms.runtime.catalogue_error_http import catalogue_invariant_error_handler


def test_catalogue_invariant_is_exposed_as_structured_422():
    app = FastAPI()
    app.add_exception_handler(
        CatalogueInvariantError,
        catalogue_invariant_error_handler,
    )

    @app.get("/invalid")
    def invalid():
        raise CatalogueInvariantError("port range requires first <= last")

    response = TestClient(app).get("/invalid")

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "CatalogueValidationError"
    assert response.json()["error"]["message"] == "port range requires first <= last"
    assert response.json()["error"]["correlationId"]
