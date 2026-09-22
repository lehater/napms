#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SECURITY = ROOT / "docs/architecture/mvp-security-architecture.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def finding(code: str, message: str, **details: Any) -> dict[str, Any]:
    return {"code": code, "message": message, **details}


def explicit(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (dict, list, tuple, set)):
        return bool(value)
    return True


def require_fields(
    mapping: Any,
    fields: tuple[str, ...],
    *,
    code: str,
    context: str,
    findings: list[dict[str, Any]],
) -> None:
    if not isinstance(mapping, dict):
        findings.append(finding(code, f"{context} must be an explicit mapping."))
        return
    for field in fields:
        if not explicit(mapping.get(field)):
            findings.append(
                finding(
                    code,
                    f"{context} must define {field}.",
                    field=field,
                )
            )


def evaluate_identity(security: dict[str, Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []

    require_fields(
        security.get("authentication"),
        ("mechanism", "issuer", "required_claims", "dependency_semantics"),
        code="IDENTITY_AUTHENTICATION_INCOMPLETE",
        context="authentication",
        findings=findings,
    )
    require_fields(
        security.get("principal"),
        ("subject", "instance_permissions_claim", "authority_claim", "rules"),
        code="IDENTITY_PRINCIPAL_INCOMPLETE",
        context="principal",
        findings=findings,
    )

    development = security.get("development_authentication")
    require_fields(
        development,
        ("applicability", "fixed_credentials", "endpoint", "token_source", "rules"),
        code="DEVELOPMENT_AUTH_INCOMPLETE",
        context="development_authentication",
        findings=findings,
    )

    lifecycle = security.get("browser_credential_lifecycle")
    require_fields(
        lifecycle,
        (
            "current_scope",
            "acquisition",
            "credential_storage",
            "expiry_renewal",
            "logout_invalidation",
            "rejection_recovery",
            "non_local",
        ),
        code="BROWSER_IDENTITY_LIFECYCLE_INCOMPLETE",
        context="browser_credential_lifecycle",
        findings=findings,
    )
    if not isinstance(lifecycle, dict):
        return findings

    acquisition = lifecycle.get("acquisition")
    local_dev = acquisition.get("local_dev") if isinstance(acquisition, dict) else None
    require_fields(
        local_dev,
        ("mechanism", "endpoint", "credentials"),
        code="BROWSER_ACQUISITION_INCOMPLETE",
        context="browser_credential_lifecycle.acquisition.local_dev",
        findings=findings,
    )
    require_fields(
        lifecycle.get("credential_storage"),
        ("location", "persistence"),
        code="BROWSER_STORAGE_INCOMPLETE",
        context="browser_credential_lifecycle.credential_storage",
        findings=findings,
    )
    require_fields(
        lifecycle.get("expiry_renewal"),
        ("access_token", "refresh", "recovery"),
        code="BROWSER_EXPIRY_RENEWAL_INCOMPLETE",
        context="browser_credential_lifecycle.expiry_renewal",
        findings=findings,
    )
    require_fields(
        lifecycle.get("logout_invalidation"),
        ("explicit_logout", "runtime_clear", "server_invalidation"),
        code="BROWSER_LOGOUT_INVALIDATION_INCOMPLETE",
        context="browser_credential_lifecycle.logout_invalidation",
        findings=findings,
    )
    require_fields(
        lifecycle.get("rejection_recovery"),
        ("unauthenticated", "forbidden"),
        code="BROWSER_REJECTION_RECOVERY_INCOMPLETE",
        context="browser_credential_lifecycle.rejection_recovery",
        findings=findings,
    )
    require_fields(
        lifecycle.get("non_local"),
        ("state", "reopening_condition"),
        code="NON_LOCAL_IDENTITY_DECISION_INCOMPLETE",
        context="browser_credential_lifecycle.non_local",
        findings=findings,
    )

    if isinstance(development, dict) and isinstance(local_dev, dict):
        development_endpoint = development.get("endpoint")
        expected_endpoint = (
            development_endpoint.get("path")
            if isinstance(development_endpoint, dict)
            else None
        )
        if (
            explicit(expected_endpoint)
            and local_dev.get("endpoint") != expected_endpoint
        ):
            findings.append(
                finding(
                    "DEVELOPMENT_AUTH_ENDPOINT_MISMATCH",
                    "Browser acquisition endpoint must match the canonical development authentication endpoint.",
                    expected=expected_endpoint,
                    actual=local_dev.get("endpoint"),
                )
            )
        expected_credentials = development.get("fixed_credentials")
        if (
            isinstance(expected_credentials, dict)
            and local_dev.get("credentials") != expected_credentials
        ):
            findings.append(
                finding(
                    "DEVELOPMENT_AUTH_CREDENTIAL_MISMATCH",
                    "Browser acquisition credentials must match the canonical development authentication credentials.",
                )
            )

    questions = security.get("security_questions_remaining")
    if questions:
        findings.append(
            finding(
                "IDENTITY_QUESTIONS_REMAIN",
                "Security Architecture still declares unresolved security questions.",
            )
        )

    return findings


def semantic_evaluation(findings: list[dict[str, Any]]) -> dict[str, Any]:
    accepted = not findings
    return {
        "version": 1,
        "kind": "harness-artifact-semantic-evaluation",
        "artifact": "SECURITY-ARCHITECTURE",
        "capability": "engineering.security.browser-identity",
        "status": "ACCEPTED" if accepted else "REJECTED",
        "findings": findings,
        "semantic_claims": {
            "accepted": ["engineering.security.identity"] if accepted else []
        },
    }


def evaluate() -> dict[str, Any]:
    security = load_yaml(SECURITY)
    return {
        "version": 1,
        "kind": "harness-semantic-evaluation-set",
        "semantic_evaluations": [
            semantic_evaluation(evaluate_identity(security)),
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--require-accepted", action="store_true")
    args = parser.parse_args()

    result = evaluate()
    encoded = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(encoded + "\n", encoding="utf-8")
    else:
        print(encoded)

    rejected = [
        item
        for item in result["semantic_evaluations"]
        if item["status"] != "ACCEPTED"
    ]
    if args.require_accepted and rejected:
        for item in rejected:
            print(
                f"{item['artifact']}: semantic acceptance REJECTED",
                *[
                    f"  - {x['code']}: {x['message']}"
                    for x in item["findings"]
                ],
                sep="\n",
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
