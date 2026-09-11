import os

from playwright.sync_api import expect, sync_playwright


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

        aside = page.locator("aside")
        desktop_nav = aside.get_by_role("navigation", name="Primary navigation")
        account = aside.get_by_role("group", name=f"Signed in as {LOGIN}")
        expect(account).to_be_visible()
        expect(aside.get_by_role("button", name="Logout")).to_be_visible()

        aside_box = aside.bounding_box()
        account_box = account.bounding_box()
        assert aside_box is not None and account_box is not None
        assert 228 <= aside_box["width"] <= 236
        assert account_box["y"] > aside_box["height"] * 0.8

        _create_resource(page, desktop_nav, "Visual Resource Alpha")
        _create_resource(page, desktop_nav, "Visual Resource Beta")

        desktop_nav.get_by_role("button", name="Resources").click()
        expect(page.get_by_role("heading", name="Resource Catalogue", exact=True)).to_be_visible()
        search = page.get_by_label("Search resources")
        search.fill("Visual Resource")
        expect(page.get_by_role("cell", name="Visual Resource Alpha", exact=True)).to_be_visible()
        expect(page.get_by_role("cell", name="Visual Resource Beta", exact=True)).to_be_visible()
        expect(page.get_by_label("Select all resources on this page")).to_be_visible()

        name_header = page.get_by_role("columnheader", name="Sort by name")
        expect(name_header).to_have_attribute("aria-sort", "ascending")
        name_header.get_by_role("button", name="Sort by name").click()
        expect(name_header).to_have_attribute("aria-sort", "descending")
        name_header.get_by_role("button", name="Sort by name").click()
        expect(name_header).to_have_attribute("aria-sort", "ascending")

        for label, count in (
            ("All", 2),
            ("Active", 2),
            ("Retired", 0),
            ("No address", 2),
            ("No responsibility", 2),
            ("No scope", 2),
        ):
            expect(page.get_by_role("button", name=f"{label} {count}", exact=True)).to_be_visible()

        expect(page.get_by_text("Showing 1–2 of 2", exact=True)).to_be_visible()
        rows_per_page = page.get_by_label("Rows per page")
        expect(rows_per_page).to_have_value("50")
        expect(page.get_by_role("button", name="Previous page")).to_be_disabled()
        expect(page.get_by_role("button", name="Next page")).to_be_disabled()
        expect(page.get_by_role("button", name="1", exact=True)).to_have_attribute("aria-current", "page")

        page.get_by_role("cell", name="Visual Resource Alpha", exact=True).get_by_role("button").click()
        expect(page.get_by_role("heading", name="Visual Resource Alpha", exact=True)).to_be_visible()
        expect(page.get_by_role("button", name="Overview", exact=True)).to_be_visible()
        expect(page.get_by_role("button", name="History", exact=True)).to_be_visible()
        expect(page.get_by_role("button", name="Technical details", exact=True)).to_be_visible()

        workspace = page.locator("main > div").first
        max_width = workspace.evaluate("element => getComputedStyle(element).maxWidth")
        assert max_width == "none"
        main_box = page.locator("main").bounding_box()
        workspace_box = workspace.bounding_box()
        assert main_box is not None and workspace_box is not None
        assert workspace_box["width"] >= main_box["width"] - 60

        browser.close()