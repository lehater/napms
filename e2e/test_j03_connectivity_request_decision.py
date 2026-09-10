import os

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
LOGIN = os.environ.get("NAPMS_E2E_LOGIN", "local-admin")
PASSWORD = os.environ.get("NAPMS_E2E_PASSWORD", "local-e2e-password")


def test_j03_request_without_final_decision_does_not_authorize_access() -> None:
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
        desktop_nav.get_by_role("button", name="Connectivity").click()
        expect(page.get_by_role("heading", name="Connectivity", exact=True)).to_be_visible()

        expect(page.get_by_text("Demo Web Frontend", exact=True)).to_be_visible()
        expect(page.get_by_text("Demo Orders API", exact=True)).to_be_visible()
        expect(page.get_by_text("No current need", exact=True)).to_be_visible()
        expect(page.get_by_text("No final decision", exact=True)).to_be_visible()
        expect(page.get_by_text("No rule", exact=True)).to_be_visible()

        page.get_by_role("button", name="Request access", exact=True).click()
        expect(page.get_by_role("heading", name="Request access", exact=True)).to_be_visible()
        expect(page.get_by_text("HTTPS Orders API", exact=True)).to_be_visible()

        page.get_by_label("Business justification").fill(
            "Demo Web requires the Orders API for checkout."
        )
        page.get_by_role("button", name="Request access", exact=True).click()

        # A Requirement may be recorded, but accepted product semantics explicitly say
        # that no final Decision must never be converted into Allowed or an Access Rule.
        expect(page.get_by_text("Access authorized", exact=True)).to_have_count(0)
        expect(
            page.get_by_text(
                "The Connectivity Requirement was recorded before the later access step failed.",
                exact=True,
            )
        ).to_be_visible()

        browser.close()
