import os
import re

from playwright.sync_api import Page, expect, sync_playwright


BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
LOGIN = os.environ.get("NAPMS_E2E_LOGIN", "local-admin")
PASSWORD = os.environ.get("NAPMS_E2E_PASSWORD", "local-e2e-password")


def _create_form(page: Page):
    return page.get_by_role("button", name="Create", exact=True).locator(
        "xpath=ancestor::form[1]"
    )


def _component_row(page: Page, name: str, component_type: str):
    return page.get_by_role(
        "row",
        name=re.compile(rf"^{re.escape(name)}\s+{re.escape(component_type)}(?:\s|$)"),
    )


def _add_component(page: Page, name: str, component_type: str = "Service") -> None:
    page.get_by_role("button", name="Add component").click()
    form = _create_form(page)
    form.get_by_label("Name").fill(name)
    form.get_by_label("Type").fill(component_type)
    form.get_by_role("button", name="Create", exact=True).click()
    expect(_component_row(page, name, component_type)).to_have_count(1)


def _select_component(page: Page, picker_label: str, name: str) -> None:
    search = page.get_by_label(f"Search {picker_label}")
    root = search.locator("xpath=ancestor::form[1]/..")
    search.fill(name)
    root.get_by_role("button", name="Search", exact=True).click()
    root.get_by_role("button", name=re.compile(rf"^{re.escape(name)}(?:\s|$)")).click()


def _add_interaction(
    page: Page,
    *,
    source: str,
    destination: str,
    destination_port: int,
) -> None:
    page.get_by_role("button", name="Add interaction").click()
    _select_component(page, "Source Component", source)
    _select_component(page, "Destination Component", destination)
    traffic_row = page.get_by_label("Destination ports").locator("xpath=..")
    traffic_row.get_by_label("Protocol").fill("tcp")
    traffic_row.get_by_label("Source ports").fill("any")
    traffic_row.get_by_label("Destination ports").fill(str(destination_port))
    page.get_by_role("button", name="Save interaction").click()
    expect(page.get_by_role("cell", name=source, exact=True)).to_be_visible()
    expect(page.get_by_role("cell", name=destination, exact=True)).to_be_visible()
    expect(page.get_by_role("cell", name=f"TCP ({destination_port})", exact=True)).to_be_visible()


def _add_deployment(page: Page) -> None:
    page.get_by_role("button", name="Deployments", exact=True).click()
    page.get_by_role("button", name="Add deployment").click()
    form = _create_form(page)
    form.get_by_label("Company").fill("Company A")
    form.get_by_label("Environment").fill("Production")
    form.get_by_label("Scope").fill("local-demo")
    form.get_by_role("button", name="Create", exact=True).click()
    expect(page.get_by_role("row", name=re.compile(r"Company A.*Production.*local-demo"))).to_have_count(1)


def test_j01_target_application_authoring_survives_correction_and_reopen() -> None:
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
        expect(page.get_by_role("button", name="Definitions", exact=True)).to_be_visible()
        expect(page.get_by_role("button", name="Deployments", exact=True)).to_be_visible()

        page.get_by_role("button", name="Add application").click()
        create_application = page.get_by_role(
            "heading", name="New application", exact=True
        ).locator("xpath=ancestor::form[1]")
        create_application.get_by_label("Name").fill("Order Management")
        create_application.get_by_label("Domain").fill("Commerce")
        create_application.get_by_label("Owner").fill("team:orders")
        create_application.get_by_role("button", name="Create", exact=True).click()
        expect(
            page.get_by_role("heading", name="Order Management", exact=True)
        ).to_be_visible()

        page.get_by_role("button", name="Components", exact=True).click()
        _add_component(page, "Web UI")
        _add_component(page, "Orders API")
        _add_component(page, "Database", component_type="Database")

        page.get_by_role("button", name="Interactions", exact=True).click()
        _add_interaction(
            page,
            source="Web UI",
            destination="Orders API",
            destination_port=443,
        )
        _add_interaction(
            page,
            source="Orders API",
            destination="Database",
            destination_port=5432,
        )

        _add_deployment(page)
        page.get_by_role("row", name=re.compile(r"Company A.*Production.*local-demo")).click()
        expect(page.get_by_role("heading", name=re.compile(r"Order Management — Company A / Production"))).to_be_visible()
        expect(page.get_by_role("heading", name="Connectivity 0 / 2", exact=True)).to_be_visible()

        page.get_by_role("button", name="Add interaction").click()
        page.get_by_label("Select Web UI to Orders API").check()
        page.get_by_label("Select Orders API to Database").check()
        page.get_by_role("button", name="Add selected").click()
        expect(page.get_by_role("heading", name="Connectivity 2 / 2", exact=True)).to_be_visible()
        expect(page.get_by_role("cell", name="TCP (443)", exact=True)).to_be_visible()
        expect(page.get_by_role("cell", name="TCP (5432)", exact=True)).to_be_visible()

        page.get_by_role("button", name="Deployments", exact=True).first.click()
        desktop_nav.get_by_role("button", name="Applications").click()
        page.get_by_placeholder("Search definitions").fill("Order Management")
        page.get_by_role("button", name="Apply", exact=True).click()
        page.get_by_role("cell", name="Order Management", exact=True).click()

        page.get_by_role("button", name="Edit", exact=True).click()
        page.get_by_label("Application name").fill("Order Management Platform")
        page.get_by_role("button", name="Save", exact=True).click()
        expect(
            page.get_by_role("heading", name="Order Management Platform", exact=True)
        ).to_be_visible()

        desktop_nav.get_by_role("button", name="Connectivity").click()
        expect(page).to_have_url(re.compile(r"#connectivity"))
        desktop_nav.get_by_role("button", name="Applications").click()
        page.get_by_placeholder("Search definitions").fill("Order Management Platform")
        page.get_by_role("button", name="Apply", exact=True).click()
        expect(page.get_by_role("cell", name="Order Management Platform", exact=True)).to_be_visible()
        row = page.get_by_role("row", name=re.compile(r"Order Management Platform.*Commerce.*3.*2.*1"))
        expect(row).to_have_count(1)
        row.click()

        page.get_by_role("button", name="Components", exact=True).click()
        expect(_component_row(page, "Web UI", "Service")).to_have_count(1)
        expect(_component_row(page, "Orders API", "Service")).to_have_count(1)
        expect(_component_row(page, "Database", "Database")).to_have_count(1)

        page.get_by_role("button", name="Interactions", exact=True).click()
        expect(page.get_by_role("cell", name="TCP (443)", exact=True)).to_be_visible()
        expect(page.get_by_role("cell", name="TCP (5432)", exact=True)).to_be_visible()

        page.get_by_role("button", name="Deployments", exact=True).click()
        deployment_row = page.get_by_role("row", name=re.compile(r"Company A.*Production.*local-demo.*2 / 2"))
        expect(deployment_row).to_have_count(1)
        deployment_row.click()
        expect(page.get_by_role("heading", name="Connectivity 2 / 2", exact=True)).to_be_visible()

        browser.close()
