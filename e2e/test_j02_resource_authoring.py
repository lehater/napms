import os

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
LOGIN = os.environ.get("NAPMS_E2E_LOGIN", "local-admin")
PASSWORD = os.environ.get("NAPMS_E2E_PASSWORD", "local-e2e-password")


def test_j02_resource_authoring_reaches_supported_correction_path() -> None:
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
        desktop_nav.get_by_role("button", name="Resources").click()
        expect(page.get_by_role("heading", name="Resources", exact=True)).to_be_visible()

        page.get_by_label("Resource name").fill("Orders Database")
        page.get_by_role("button", name="Create", exact=True).click()
        expect(
            page.get_by_role("heading", name="Orders Database", exact=True)
        ).to_be_visible()

        page.get_by_label("Technical addresses").fill("10.20.30.40")
        page.get_by_role("button", name="Add addresses").click()
        expect(page.get_by_text("10.20.30.40", exact=True)).to_be_visible()

        page.get_by_label("External scope reference").fill("orders-prod")
        page.get_by_role("button", name="Add affiliation").click()
        expect(page.get_by_text("orders-prod", exact=True)).to_be_visible()

        page.get_by_label("Party kind").select_option("Team")
        page.get_by_label("Role").select_option("TechnicalOwner")
        page.get_by_label("External person/team reference").fill(
            "team:orders-platform"
        )
        page.get_by_label("Display name").fill("Orders Platform")
        page.get_by_label("Contact (optional)").fill("orders@example.test")
        page.get_by_role("button", name="Add responsibility").click()
        expect(page.get_by_text("Orders Platform", exact=True)).to_be_visible()
        expect(page.get_by_text("orders@example.test", exact=True)).to_be_visible()

        page.get_by_label("Technical addresses").fill("10.20.30.41")
        page.get_by_role("button", name="Replace addresses").click()
        expect(page.get_by_text("10.20.30.41", exact=True)).to_be_visible()
        expect(page.get_by_text("10.20.30.40", exact=True)).to_have_count(0)

        # Accepted Resource identity correction is rename-with-stable-identity.
        # Baseline intentionally stops here if the supported UI does not expose it.
        expect(page.get_by_role("button", name="Rename", exact=True)).to_be_visible()

        browser.close()
