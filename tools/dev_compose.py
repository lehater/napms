import argparse
import base64
import hashlib
import http.cookiejar
import json
import os
import secrets
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=2**14,
        r=8,
        p=1,
        dklen=32,
    )
    return "$".join(
        (
            "scrypt-v1",
            base64.urlsafe_b64encode(salt).decode("ascii"),
            base64.urlsafe_b64encode(digest).decode("ascii"),
        )
    )


def compose(*args: str, env=None, check: bool = True):
    return subprocess.run(
        ["docker", "compose", *args],
        env=env,
        check=check,
    )


def wait_ready(base_url: str) -> None:
    last_error = None
    for _ in range(60):
        try:
            with urllib.request.urlopen(
                f"{base_url}/health/ready",
                timeout=2,
            ) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as exc:
            last_error = exc
        time.sleep(1)
    raise RuntimeError(f"NAPMS public readiness did not become healthy: {last_error}")


def authenticated_smoke(
    *,
    base_url: str,
    login: str,
    password: str,
) -> None:
    cookies = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(cookies)
    )

    request = urllib.request.Request(
        f"{base_url}/api/v1/session",
        method="POST",
        data=json.dumps(
            {"login": login, "password": password}
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(request, timeout=5) as response:
        if response.status != 200:
            raise RuntimeError("local login smoke failed")

    with opener.open(f"{base_url}/api/v1/session", timeout=5) as response:
        payload = json.load(response)
        if payload["actor"]["login"] != login:
            raise RuntimeError("authenticated session actor mismatch")

    with opener.open(
        f"{base_url}/api/v1/access-rule-proposals/scopes",
        timeout=5,
    ) as response:
        payload = json.load(response)
        scopes = {item["scope"] for item in payload["scopes"]}
        if "local-demo" not in scopes:
            raise RuntimeError("local demo authority seed is unavailable")

    with opener.open(
        f"{base_url}/api/v1/access-rule-proposals/interactions"
        "?scope=local-demo&page=1&pageSize=50",
        timeout=5,
    ) as response:
        payload = json.load(response)
        if len(payload["items"]) != 1:
            raise RuntimeError("local demo interaction seed is unavailable")
        catalogue = payload["items"][0].get("catalogue") or {}
        if catalogue.get("sourceDisplayName") != "Demo Web Frontend":
            raise RuntimeError("local demo source display metadata is unavailable")
        if catalogue.get("destinationDisplayName") != "Demo Orders API":
            raise RuntimeError("local demo destination display metadata is unavailable")
        if catalogue.get("dcsDisplayName") != "HTTPS Orders API":
            raise RuntimeError("local demo DCS display metadata is unavailable")
        alternatives = catalogue.get("trafficAlternatives") or []
        if not alternatives or alternatives[0].get("protocol") != "tcp":
            raise RuntimeError("local demo DCS traffic summary is unavailable")

    with opener.open(
        f"{base_url}/api/v1/access-rules?page=1&pageSize=50",
        timeout=5,
    ) as response:
        before_rules = json.load(response)
        if before_rules.get("items"):
            raise RuntimeError(
                "local demo must start without authoritative Access Rules"
            )

    with opener.open(
        f"{base_url}/api/v1/connectivity-requirements/scopes",
        timeout=5,
    ) as response:
        payload = json.load(response)
        scopes = {item["scope"] for item in payload["scopes"]}
        if "local-demo" not in scopes:
            raise RuntimeError(
                "local demo Connectivity Requirements authority seed is unavailable"
            )

    with opener.open(
        f"{base_url}/api/v1/connectivity-requirements/interactions"
        "?scope=local-demo&page=1&pageSize=50",
        timeout=5,
    ) as response:
        payload = json.load(response)
        items = payload.get("items") or []
        if len(items) != 1:
            raise RuntimeError(
                "local demo Connectivity Requirements interaction is unavailable"
            )
        interaction = items[0]

    connectivity_query = urllib.parse.urlencode(
        {
            "scope": "local-demo",
            "asOf": "2026-09-09T12:00:00+00:00",
            "page": 1,
            "pageSize": 50,
        }
    )
    connectivity_url = f"{base_url}/api/v1/connectivity?{connectivity_query}"

    with opener.open(connectivity_url, timeout=5) as response:
        connectivity = json.load(response)
        items = connectivity.get("items") or []
        if len(items) != 1:
            raise RuntimeError(
                "Scoped Connectivity must expose exactly the local demo Resource"
            )
        local = items[0]
        if local["resource"].get("resourceReference") != "local-demo-source":
            raise RuntimeError(
                "Scoped Connectivity local Resource derivation is incorrect"
            )
        components = local.get("components") or []
        if len(components) != 1:
            raise RuntimeError(
                "Scoped Connectivity local Component binding is unavailable"
            )
        relationships = components[0].get("relationships") or []
        if len(relationships) != 1:
            raise RuntimeError(
                "Scoped Connectivity exact interaction is unavailable"
            )
        relationship = relationships[0]
        if relationship.get("direction") != "Outgoing":
            raise RuntimeError(
                "Scoped Connectivity local-relative direction is incorrect"
            )
        remote_resources = relationship.get("remoteResources") or []
        if (
            len(remote_resources) != 1
            or remote_resources[0].get("resourceReference")
            != "local-demo-destination"
        ):
            raise RuntimeError(
                "Scoped Connectivity foreign remote Resource is unavailable"
            )
        if relationship["need"].get("current") != "None":
            raise RuntimeError(
                "initial Scoped Connectivity Need must be absent"
            )
        if relationship["policy"].get("ruleExists") != "No":
            raise RuntimeError(
                "initial Scoped Connectivity Policy must have no Rule"
            )
        if relationship["decision"].get("state") != "NoFinalDecision":
            raise RuntimeError(
                "Scoped Connectivity must report authoritative no-final-Decision absence"
            )
        if connectivity.get("partial") is not False:
            raise RuntimeError(
                "Scoped Connectivity must not be partial when all enrichments are available"
            )

    declaration = urllib.request.Request(
        f"{base_url}/api/v1/connectivity-requirements",
        method="POST",
        data=json.dumps(
            {
                "authorityScope": "local-demo",
                "dependentComponentDeploymentId": interaction[
                    "sourceComponentDeploymentId"
                ],
                "sourceComponentDeploymentId": interaction[
                    "sourceComponentDeploymentId"
                ],
                "destinationComponentDeploymentId": interaction[
                    "destinationComponentDeploymentId"
                ],
                "dcsContractRevisionId": interaction["dcsContractRevisionId"],
                "applicability": {"kind": "Ongoing"},
                "justification": "Local Docker smoke connectivity need.",
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(declaration, timeout=5) as response:
        if response.status != 201:
            raise RuntimeError("Connectivity Requirement declaration smoke failed")
        declared = json.load(response)
        requirement_id = declared["requirement"]["requirementId"]

    with opener.open(
        f"{base_url}/api/v1/connectivity-requirements?page=1&pageSize=50",
        timeout=5,
    ) as response:
        payload = json.load(response)
        visible_ids = {item["requirementId"] for item in payload["items"]}
        if requirement_id not in visible_ids:
            raise RuntimeError(
                "declared Connectivity Requirement is not visible through public list"
            )

    with opener.open(
        f"{base_url}/api/v1/access-rules?page=1&pageSize=50",
        timeout=5,
    ) as response:
        after_requirement = json.load(response)
        if after_requirement.get("items"):
            raise RuntimeError(
                "Connectivity Requirement declaration created an Access Rule side effect"
            )

    alignment_query = urllib.parse.urlencode(
        {"asOf": "2026-09-09T12:00:00+00:00"}
    )
    alignment_url = (
        f"{base_url}/api/v1/connectivity-requirements/"
        f"{requirement_id}/alignment?{alignment_query}"
    )
    with opener.open(alignment_url, timeout=5) as response:
        alignment = json.load(response)
        if alignment.get("status") != "Uncovered":
            raise RuntimeError(
                "Requirement without effective Access Rule must be Uncovered"
            )

    proposal = urllib.request.Request(
        f"{base_url}/api/v1/access-rule-proposals",
        method="POST",
        data=json.dumps(
            {
                "authorityScope": "local-demo",
                "sourceComponentDeploymentId": interaction[
                    "sourceComponentDeploymentId"
                ],
                "destinationComponentDeploymentId": interaction[
                    "destinationComponentDeploymentId"
                ],
                "dcsContractRevisionId": interaction["dcsContractRevisionId"],
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(proposal, timeout=5) as response:
        materialized = json.load(response)
        if materialized.get("outcome") not in {"Materialized", "Resolved"}:
            raise RuntimeError("explicit Access Rule proposal smoke failed")
        rule_id = materialized["rule"]["ruleId"]

    with opener.open(alignment_url, timeout=5) as response:
        alignment = json.load(response)
        if alignment.get("status") != "Covered":
            raise RuntimeError(
                "effective exact Access Rule must cover Connectivity Requirement"
            )


    with opener.open(connectivity_url, timeout=5) as response:
        connectivity = json.load(response)
        relationship = (
            connectivity["items"][0]["components"][0]["relationships"][0]
        )
        if relationship["need"].get("current") != "Required":
            raise RuntimeError(
                "Scoped Connectivity must reflect the current Requirement"
            )
        if relationship["need"].get("coverage") != "Covered":
            raise RuntimeError(
                "Scoped Connectivity must reflect Requirement policy coverage"
            )
        policy = relationship["policy"]
        if (
            policy.get("ruleExists") != "Yes"
            or policy.get("operationalState") != "Active"
            or policy.get("effectiveAtAsOf") != "Yes"
        ):
            raise RuntimeError(
                "Scoped Connectivity must reflect effective Access Policy"
            )

    state_change = urllib.request.Request(
        f"{base_url}/api/v1/access-rules/{rule_id}/operational-state",
        method="PATCH",
        data=json.dumps({"targetState": "Inactive"}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(state_change, timeout=5) as response:
        changed_rule = json.load(response)
        if changed_rule.get("outcome") != "Updated":
            raise RuntimeError("Access Rule state mutation smoke failed")

    with opener.open(alignment_url, timeout=5) as response:
        alignment = json.load(response)
        if alignment.get("status") != "Uncovered":
            raise RuntimeError(
                "Inactive exact Access Rule must not cover Connectivity Requirement"
            )

    justification_change = urllib.request.Request(
        f"{base_url}/api/v1/connectivity-requirements/{requirement_id}/justification",
        method="PATCH",
        data=json.dumps(
            {"justification": "Updated local Docker smoke connectivity need."}
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(justification_change, timeout=5) as response:
        changed = json.load(response)
        if changed.get("outcome") != "Updated":
            raise RuntimeError(
                "Connectivity Requirement justification mutation smoke failed"
            )

    applicability_change = urllib.request.Request(
        f"{base_url}/api/v1/connectivity-requirements/{requirement_id}/applicability",
        method="PATCH",
        data=json.dumps(
            {
                "applicability": {
                    "kind": "AbsoluteWindow",
                    "start": "2030-01-01T08:00:00+00:00",
                    "end": "2030-01-01T18:00:00+00:00",
                }
            }
        ).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with opener.open(applicability_change, timeout=5) as response:
        changed = json.load(response)
        if changed.get("outcome") != "Updated":
            raise RuntimeError(
                "Connectivity Requirement applicability mutation smoke failed"
            )

    with opener.open(alignment_url, timeout=5) as response:
        alignment = json.load(response)
        if alignment.get("status") != "NotCurrent":
            raise RuntimeError(
                "Requirement outside applicability must be NotCurrent"
            )

    retirement = urllib.request.Request(
        f"{base_url}/api/v1/connectivity-requirements/{requirement_id}/retirement",
        method="POST",
    )
    with opener.open(retirement, timeout=5) as response:
        retired = json.load(response)
        if retired.get("outcome") != "Retired":
            raise RuntimeError("Connectivity Requirement retirement smoke failed")

    with opener.open(
        f"{base_url}/api/v1/connectivity-requirements/{requirement_id}",
        timeout=5,
    ) as response:
        detail = json.load(response)
        requirement = detail["requirement"]
        if requirement.get("lifecycleState") != "Retired":
            raise RuntimeError(
                "Connectivity Requirement retirement did not persist publicly"
            )
        if requirement.get("version") != 4:
            raise RuntimeError(
                "Connectivity Requirement mutation history/version is inconsistent"
            )

    with opener.open(
        f"{base_url}/api/v1/access-rules?page=1&pageSize=50",
        timeout=5,
    ) as response:
        after_rules = json.load(response)
        items = after_rules.get("items") or []
        if len(items) != 1 or items[0].get("operationalState") != "Inactive":
            raise RuntimeError(
                "explicitly materialized Access Rule state did not persist"
            )


def up(*, print_credentials: bool = True) -> None:
    login = os.environ.get("NAPMS_LOCAL_AUTH_LOGIN", "local-admin")
    actor_id = os.environ.get("NAPMS_LOCAL_AUTH_ACTOR_ID", login)
    password = secrets.token_urlsafe(15)
    password_hash = hash_password(password)
    port = os.environ.get("NAPMS_WEB_PORT", "8080")
    base_url = f"http://127.0.0.1:{port}"

    env = os.environ.copy()
    env.update(
        {
            "NAPMS_LOCAL_AUTH_LOGIN": login,
            "NAPMS_LOCAL_AUTH_ACTOR_ID": actor_id,
            "NAPMS_LOCAL_AUTH_PASSWORD_HASH": password_hash,
        }
    )

    try:
        compose("up", "--build", "--detach", "--remove-orphans", env=env)
        wait_ready(base_url)
        authenticated_smoke(
            base_url=base_url,
            login=login,
            password=password,
        )
    except Exception:
        compose("ps", env=env, check=False)
        raise

    print(f"NAPMS ready: {base_url}")
    if print_credentials:
        print(f"Login: {login}")
        print(f"Password: {password}")
        print("Password was generated for this run and was not written to disk.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("up",))
    parser.add_argument(
        "--no-print-credentials",
        action="store_true",
        help="run authenticated smoke without printing generated credentials",
    )
    args = parser.parse_args()

    if args.action == "up":
        up(print_credentials=not args.no_print_credentials)


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, subprocess.CalledProcessError, urllib.error.URLError) as exc:
        print(f"NAPMS local startup failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
