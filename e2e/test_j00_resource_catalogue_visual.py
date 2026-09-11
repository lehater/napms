import os

from playwright.sync_api import expect, sync_playwright

from e2e.screenshot_regression import (
    application_main_fingerprint,
    assert_resource_screen_fingerprints,
)


BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
LOGIN = os.environ.get("NAPMS_E2E_LOGIN", "local-admin")
PASSWORD = os.environ.get("NAPMS_E2E_PASSWORD", "local-e2e-password")


def _create_resource(page, desktop_nav, name: str) -> None:
    desktop_nav.get_by_role("button", name="Resources").click()
    expect(page.get_by_role("heading", name="Resource Catalogue", exact=True)).to_be_visible()
    page.get_by_role("button", name="New resource", exact=True).click()
    dialog = page.get_by_role("dialog")
    dialog.get_by_label("Display name").fill(name)
    dialog.get_by_role("button", name="Create resource", exact=True).click()
    expect(page.get_by_role("heading", name=name, exact=True)).to_be_visible()


def test_j00_resource_catalogue_reference_layout() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.set_default_timeout(15_000)

        page.goto(BASE_URL)
        page.get_by_label("Login").fill(LOGIN)
        page.get_by_label("Password").fill(PASSWORD)
        page.get_by_role("button", name="Sign in").click()

        desktop_nav = page.locator("aside").get_by_role(
            "navigation", name="Primary navigation"
        )
        _create_resource(page, desktop_nav, "Visual Resource Alpha")
        _create_resource(page, desktop_nav, "Visual Resource Beta")

        desktop_nav.get_by_role("button", name="Resources").click()
        expect(page.get_by_role("heading", name="Resource Catalogue", exact=True)).to_be_visible()
        expect(page.get_by_role("cell", name="Visual Resource Alpha", exact=True)).to_be_visible()
        expect(page.get_by_role("cell", name="Visual Resource Beta", exact=True)).to_be_visible()
        expect(page.get_by_label("Select all resources on this page")).to_be_visible()

        screenshots = {"resource-catalogue": application_main_fingerprint(page)}
        assert_resource_screen_fingerprints(screenshots)
        browser.close()
