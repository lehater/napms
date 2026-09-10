import os

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
LOGIN = os.environ.get("NAPMS_E2E_LOGIN", "local-admin")
PASSWORD = os.environ.get("NAPMS_E2E_PASSWORD", "local-e2e-password")


def _accept_next_dialog(page) -> None:
    page.once("dialog", lambda dialog: dialog.accept())


def test_j02_resource_authoring_survives_correction_reopen_and_retirement() -> None:
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

        # Correct display metadata without changing Resource identity.
        page.get_by_role("button", name="Rename", exact=True).click()
        page.get_by_label("New display name").fill("Orders Database Primary")
        page.get_by_role("button", name="Save", exact=True).click()
        expect(
            page.get_by_role("heading", name="Orders Database Primary", exact=True)
        ).to_be_visible()

        # Prove the durable authored state by leaving the workspace and reopening it
        # through normal user discovery rather than retaining an internal identifier.
        desktop_nav.get_by_role("button", name="Connectivity").click()
        desktop_nav.get_by_role("button", name="Resources").click()
        expect(page.get_by_role("heading", name="Resources", exact=True)).to_be_visible()
        page.get_by_label("Search resources").fill("Orders Database Primary")
        page.get_by_role("button", name="Apply resource filters").click()
        result = page.locator("main").get_by_role("button").filter(
            has_text="Orders Database Primary"
        )
        expect(result).to_have_count(1)
        result.click()

        expect(
            page.get_by_role("heading", name="Orders Database Primary", exact=True)
        ).to_be_visible()
        expect(page.get_by_text("10.20.30.41", exact=True)).to_be_visible()
        expect(page.get_by_text("orders-prod", exact=True)).to_be_visible()
        expect(page.get_by_text("Orders Platform", exact=True)).to_be_visible()
        expect(page.get_by_text("orders@example.test", exact=True)).to_be_visible()

        # Retirement is deliberately blocked while authoritative current ownership
        # relations exist; the UI must expose that reason rather than cascade-delete.
        _accept_next_dialog(page)
        page.get_by_role("button", name="Retire", exact=True).click()
        expect(page.get_by_role("alert")).to_contain_text(
            "End current scope affiliations and responsibilities before retiring this resource."
        )

        scope_section = page.locator("section").filter(
            has=page.get_by_role("heading", name="Responsibility scopes", exact=True)
        )
        _accept_next_dialog(page)
        scope_section.get_by_role("button", name="End", exact=True).click()
        expect(scope_section.get_by_text("orders-prod", exact=True)).to_have_count(0)

        responsibility_section = page.locator("section").filter(
            has=page.get_by_role("heading", name="Responsibilities", exact=True)
        )
        _accept_next_dialog(page)
        responsibility_section.get_by_role("button", name="End", exact=True).click()
        expect(
            responsibility_section.get_by_text("Orders Platform", exact=True)
        ).to_have_count(0)

        _accept_next_dialog(page)
        page.get_by_role("button", name="Retire", exact=True).click()
        expect(page.get_by_text("Retired", exact=True)).to_be_visible()
        expect(page.get_by_role("button", name="Rename", exact=True)).to_have_count(0)

        # Default discovery is the Active workspace; retired history is no longer
        # presented as current work.
        desktop_nav.get_by_role("button", name="Resources").click()
        page.get_by_label("Search resources").fill("Orders Database Primary")
        page.get_by_role("button", name="Apply resource filters").click()
        expect(page.get_by_text("No resources match the current view.")).to_be_visible()

        browser.close()
