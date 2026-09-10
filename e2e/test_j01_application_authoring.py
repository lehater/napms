import os
import re

from playwright.sync_api import Page, expect, sync_playwright


BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
LOGIN = os.environ.get("NAPMS_E2E_LOGIN", "local-admin")
PASSWORD = os.environ.get("NAPMS_E2E_PASSWORD", "local-e2e-password")


def _component_section(page: Page, name: str):
    return page.get_by_role("heading", name=name, exact=True).locator(
        "xpath=ancestor::section[1]"
    )


def _add_component(page: Page, name: str) -> None:
    field = page.get_by_placeholder("Component name, e.g. Orders API")
    field.fill(name)
    page.get_by_role("button", name="Create component").click()
    expect(page.get_by_role("heading", name=name, exact=True)).to_be_visible()


def _add_deployment(page: Page, component_name: str) -> None:
    section = _component_section(page, component_name)
    section.get_by_placeholder(
        "Deployment name (optional), e.g. production"
    ).fill("production")
    section.get_by_role("button", name="Add deployment").click()
    expect(section.get_by_text("production", exact=True)).to_be_visible()


def _create_communication(
    page: Page,
    *,
    source: str,
    destination: str,
    label: str,
    port: int,
) -> None:
    page.get_by_label("Source deployment").select_option(label=source)
    page.get_by_label("Destination deployment").select_option(label=destination)
    page.get_by_label("Label").fill(label)
    page.get_by_label("Protocol").select_option("tcp")
    page.get_by_label("Destination port").fill(str(port))
    page.get_by_role("button", name="Create specification").click()
    expect(
        page.get_by_text(f"Communication specification {label} created.", exact=True)
    ).to_be_visible()


def test_j01_application_authoring_survives_correction_and_reopen() -> None:
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
        desktop_nav.get_by_role("button", name="Applications").click()
        expect(page.get_by_role("heading", name="Applications", exact=True)).to_be_visible()

        page.get_by_label("Application name").fill("Order Management")
        page.get_by_role("button", name="Create", exact=True).click()
        expect(
            page.get_by_role("heading", name="Order Management", exact=True)
        ).to_be_visible()

        for component in ("Web UI", "Orders API", "Database"):
            _add_component(page, component)
            _add_deployment(page, component)

        # Participant discovery is backend-owned. Searching after structure creation
        # refreshes the selectable Active deployment projection without using IDs.
        page.get_by_placeholder("Application, component or deployment").fill(
            "Order Management"
        )

        _create_communication(
            page,
            source="Order Management / Web UI / production",
            destination="Order Management / Orders API / production",
            label="Web to Orders",
            port=443,
        )
        _create_communication(
            page,
            source="Order Management / Orders API / production",
            destination="Order Management / Database / production",
            label="Orders to Database",
            port=5432,
        )

        # Exercise an ordinary correction through the accepted stable-identity rename path.
        page.locator("main").get_by_role("button", name="Rename").first.click()
        page.get_by_label("New display name").fill("Order Management Platform")
        page.get_by_role("button", name="Save", exact=True).click()
        expect(
            page.get_by_role("heading", name="Order Management Platform", exact=True)
        ).to_be_visible()

        # A history-ending lifecycle action must be deliberate; dismissing confirmation
        # must leave the active Component untouched.
        confirmation_messages: list[str] = []

        def dismiss_retirement(dialog) -> None:
            confirmation_messages.append(dialog.message)
            dialog.dismiss()

        web_section = _component_section(page, "Web UI")
        page.once("dialog", dismiss_retirement)
        web_section.get_by_role("button", name="Retire").first.click()
        assert confirmation_messages == [
            "Retire Web UI? Active deployments must be retired first. Historical references will be preserved."
        ]
        expect(page.get_by_role("heading", name="Web UI", exact=True)).to_be_visible()

        # Reopen from another workspace. The durable model must remain understandable
        # through names and traffic semantics, not implementation UUIDs.
        desktop_nav.get_by_role("button", name="Connectivity").click()
        expect(page).to_have_url(re.compile(r"#connectivity"))
        desktop_nav.get_by_role("button", name="Applications").click()
        expect(page.get_by_role("heading", name="Applications", exact=True)).to_be_visible()

        page.get_by_label("Search applications").fill("Order Management Platform")
        page.get_by_role("button", name="Search").click()
        result = page.locator("main").get_by_role("button").filter(
            has_text="Order Management Platform"
        )
        expect(result).to_have_count(1)
        result.click()

        expect(
            page.get_by_role("heading", name="Order Management Platform", exact=True)
        ).to_be_visible()
        for component in ("Web UI", "Orders API", "Database"):
            expect(page.get_by_role("heading", name=component, exact=True)).to_be_visible()
        expect(page.get_by_text("production", exact=True)).to_have_count(3)

        web_section = _component_section(page, "Web UI")
        expect(web_section.get_by_text("Web to Orders", exact=True)).to_be_visible()
        expect(
            web_section.get_by_text(
                "Web UI / production → Orders API / production", exact=True
            )
        ).to_be_visible()
        expect(
            web_section.get_by_text(
                "TCP · source any port → destination 443", exact=True
            )
        ).to_be_visible()

        database_section = _component_section(page, "Database")
        expect(
            database_section.get_by_text("Orders to Database", exact=True)
        ).to_be_visible()
        expect(
            database_section.get_by_text(
                "Orders API / production → Database / production", exact=True
            )
        ).to_be_visible()
        expect(
            database_section.get_by_text(
                "TCP · source any port → destination 5432", exact=True
            )
        ).to_be_visible()

        browser.close()
