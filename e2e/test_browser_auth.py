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
    with urllib.request.urlopen(f"{OIDC_URL}/token?profile={profile}", context=context, timeout=5) as response:
        return json.load(response)["access_token"]


def assert_resource_state(access_token: str | None, expected: str | None) -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context()
        value = "" if access_token is None else access_token
        context.add_init_script(
            "window.__NAPMS_RUNTIME_ACCESS_TOKEN__ = " + json.dumps(value) + ";"
        )
        page = context.new_page()
        page.goto(f"{BASE_URL}/resources")
        page.get_by_role("heading", name="Resources").wait_for()
        if expected is None:
            page.get_by_text("Resource operation:").wait_for(state="detached")
        else:
            page.get_by_text(f"Resource operation: {expected}.").wait_for()
        browser.close()


def test_browser_uses_signed_oidc_token_through_runtime_auth_session() -> None:
    assert_resource_state(token("full"), None)


def test_missing_invalid_and_expired_tokens_are_unauthenticated() -> None:
    for value in (None, "not-a-jwt", token("expired")):
        assert_resource_state(value, "unauthenticated")


def test_authenticated_principal_without_permission_is_forbidden() -> None:
    assert_resource_state(token("restricted"), "forbidden")
