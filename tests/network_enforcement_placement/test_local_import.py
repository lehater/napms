import json
from uuid import UUID

import pytest

from napms.network_enforcement_placement.adapters.local_import import (
    LocalPlacementKnowledgeImportAdapter,
    LocalPlacementKnowledgeImportError,
)


def document():
    return {
        "source_reference": "lab-topology",
        "source_capture_reference": "capture-1",
        "validity": {
            "valid_from": "2026-09-09T10:00:00Z",
            "valid_until": "2026-09-10T10:00:00Z",
        },
        "relation": {
            "source_ip": "10.0.0.1",
            "destination_ip": "10.0.0.2",
        },
        "path": {
            "path_reference": "path-1",
            "traversal_points": [
                {
                    "provider_realization": {
                        "namespace": "lab",
                        "reference": "device-a",
                    },
                    "path_attachment": {
                        "namespace": "lab",
                        "reference": "edge-a",
                    },
                    "provenance": ["route:1"],
                }
            ],
            "provenance": ["path:1"],
        },
        "no_forwarding_path": None,
        "logical_firewalls": [
            {
                "logical_firewall_id": str(
                    UUID(int=1)
                ),
                "validity": {
                    "valid_from": "2026-01-01T00:00:00Z",
                    "valid_until": None,
                },
                "provenance": ["lf:1"],
            }
        ],
        "correspondences": [
            {
                "logical_firewall_id": str(
                    UUID(int=1)
                ),
                "provider_realization": {
                    "namespace": "lab",
                    "reference": "device-a",
                },
                "validity": {
                    "valid_from": "2026-01-01T00:00:00Z",
                    "valid_until": None,
                },
                "provenance": ["corr:1"],
            }
        ],
        "attachments": [
            {
                "enforcement_attachment_id": str(
                    UUID(int=10)
                ),
                "logical_firewall_id": str(
                    UUID(int=1)
                ),
                "provider_realization": {
                    "namespace": "lab",
                    "reference": "device-a",
                },
                "path_attachment": {
                    "namespace": "lab",
                    "reference": "edge-a",
                },
                "validity": {
                    "valid_from": "2026-01-01T00:00:00Z",
                    "valid_until": None,
                },
                "provenance": ["attachment:10"],
            }
        ],
        "complete_for_pair": True,
        "complete_for_attachments": True,
    }


def test_strict_import_normalizes_provider_and_firewall_identities_separately():
    capture = (
        LocalPlacementKnowledgeImportAdapter()
        .normalize(
            json.dumps(document())
        )
    )

    assert (
        capture.source.namespace
        == "local-import"
    )
    assert (
        capture.knowledge
        .logical_firewalls[0]
        .logical_firewall_id
        == UUID(int=1)
    )
    assert (
        capture.knowledge
        .attachments[0]
        .provider_realization
        .reference
        == "device-a"
    )
    assert (
        str(
            capture.knowledge
            .logical_firewalls[0]
            .logical_firewall_id
        )
        != "device-a"
    )


def test_duplicate_json_field_is_rejected():
    raw = (
        '{"source_reference":"a",'
        '"source_reference":"b"}'
    )
    with pytest.raises(
        LocalPlacementKnowledgeImportError
    ):
        (
            LocalPlacementKnowledgeImportAdapter()
            .normalize(raw)
        )


def test_unknown_provider_specific_field_is_rejected():
    value = document()
    value["path"][
        "traversal_points"
    ][0]["zone"] = "trust"

    with pytest.raises(
        LocalPlacementKnowledgeImportError
    ):
        (
            LocalPlacementKnowledgeImportAdapter()
            .normalize(
                json.dumps(value)
            )
        )


def test_naive_validity_is_rejected():
    value = document()
    value["validity"][
        "valid_from"
    ] = "2026-09-09T10:00:00"

    with pytest.raises(
        LocalPlacementKnowledgeImportError
    ):
        (
            LocalPlacementKnowledgeImportAdapter()
            .normalize(
                json.dumps(value)
            )
        )


def test_multiple_paths_shape_is_rejected_in_first_slice():
    value = document()
    value["paths"] = [
        value.pop("path")
    ]

    with pytest.raises(
        LocalPlacementKnowledgeImportError
    ):
        (
            LocalPlacementKnowledgeImportAdapter()
            .normalize(
                json.dumps(value)
            )
        )


def test_empty_fact_provenance_is_rejected():
    value = document()
    value["path"]["provenance"] = []

    with pytest.raises(
        LocalPlacementKnowledgeImportError
    ):
        (
            LocalPlacementKnowledgeImportAdapter()
            .normalize(
                json.dumps(value)
            )
        )
