from __future__ import annotations

import json
import os
import ssl
import urllib.request

from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
OIDC_URL = os.environ.get("NAPMS_E2E_OIDC_URL", "https://127.0.0.1:8443")


def token(profile: str = "full") -> str:
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(
        f"{OIDC_URL}/token?profile={profile}", context=context, timeout=5
    ) as response:
        return json.load(response)["access_token"]


def assert_resource_state(
    access_token: str,
    *,
    expected_http_status: int,
    authorization_rejected: bool,
) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        context.add_init_script(
            "window.__NAPMS_RUNTIME_ACCESS_TOKEN__ = "
            + json.dumps(access_token)
            + ";"
        )
        page = context.new_page()
        with page.expect_response(
            lambda response: response.url.split("?", 1)[0].endswith("/v1/resources")
        ) as response_info:
            page.goto(f"{BASE_URL}/resources")
        assert response_info.value.status == expected_http_status
        page.get_by_role("heading", name="Resources").wait_for()
        rejection = page.get_by_text(
            "Resource catalogue access was rejected by the backend."
        )
        if authorization_rejected:
            rejection.wait_for()
        else:
            rejection.wait_for(state="detached")
        browser.close()


def test_missing_token_is_gated_by_development_login() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{BASE_URL}/resources")
        page.get_by_role("heading", name="Sign in").wait_for()
        assert page.get_by_label("Login").input_value() == "admin"
        assert page.get_by_label("Password").input_value() == "admin"
        browser.close()


def test_local_development_login_enters_authenticated_product() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{BASE_URL}/resources")
        page.get_by_role("heading", name="Sign in").wait_for()

        with page.expect_response(
            lambda response: response.url.endswith("/dev-auth/login")
        ) as login_response:
            with page.expect_response(
                lambda response: response.url.split("?", 1)[0].endswith(
                    "/v1/resources"
                )
            ) as resource_response:
                page.get_by_role("button", name="Sign in").click()

        assert login_response.value.status == 200
        assert resource_response.value.status == 200
        page.get_by_role("heading", name="Resources").wait_for()

        page.reload()
        page.get_by_role("heading", name="Sign in").wait_for()
        browser.close()


def test_local_development_login_rejects_wrong_password() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto(f"{BASE_URL}/resources")
        page.get_by_role("heading", name="Sign in").wait_for()
        page.get_by_label("Password").fill("wrong")

        with page.expect_response(
            lambda response: response.url.endswith("/dev-auth/login")
        ) as login_response:
            page.get_by_role("button", name="Sign in").click()

        assert login_response.value.status == 401
        page.get_by_text("Invalid login or password.").wait_for()
        page.get_by_role("heading", name="Sign in").wait_for()
        browser.close()


def test_browser_uses_signed_oidc_token_through_runtime_auth_session() -> None:
    assert_resource_state(
        token("full"),
        expected_http_status=200,
        authorization_rejected=False,
    )


def test_invalid_and_expired_tokens_are_unauthenticated() -> None:
    for value in ("not-a-jwt", token("expired")):
        assert_resource_state(
            value,
            expected_http_status=401,
            authorization_rejected=True,
        )


def test_authenticated_principal_without_permission_is_forbidden() -> None:
    assert_resource_state(
        token("restricted"),
        expected_http_status=403,
        authorization_rejected=True,
    )
