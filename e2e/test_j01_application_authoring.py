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


def _deployment_row(page: Page):
    return page.get_by_role("cell", name="Company A", exact=True).locator("xpath=..")


def _create_resource(
    page: Page,
    desktop_nav,
    *,
    name: str,
    address: str,
) -> str:
    desktop_nav.get_by_role("button", name="Resources").click()
    expect(page.get_by_role("heading", name="Resources", exact=True)).to_be_visible()
    page.get_by_label("Resource name").fill(name)
    page.get_by_role("button", name="Create", exact=True).click()
    expect(page.get_by_role("heading", name=name, exact=True)).to_be_visible()

    identity_text = page.locator("header").get_by_text(
        re.compile(r"resource:[0-9a-f-]{36}")
    ).text_content()
    match = re.search(r"resource:[0-9a-f-]{36}", identity_text or "")
    assert match is not None
    resource_reference = match.group(0)

    page.get_by_label("Technical addresses").fill(address)
    page.get_by_role("button", name="Add addresses").click()
    expect(page.get_by_text(address, exact=True)).to_be_visible()

    page.get_by_label("External scope reference").fill("local-demo")
    page.get_by_role("button", name="Add affiliation").click()
    expect(page.get_by_text("local-demo", exact=True)).to_be_visible()
    return resource_reference


def _add_component(page: Page, name: str, component_type: str = "Service") -> None:
    page.get_by_role("button", name="Add component").click()
    form = _create_form(page)
    form.get_by_label("Name").fill(name)
    form.get_by_label("Type").fill(component_type)
    form.get_by_role("button", name="Create", exact=True).click()
    expect(_component_row(page, name, component_type)).to_have_count(1)


def _select_component(page: Page, picker_label: str, name: str) -> None:
    root = page.get_by_role("group", name=picker_label, exact=True)
    search = root.get_by_label(f"Search {picker_label}")
    search.fill(name)
    root.get_by_role("button", name="Search", exact=True).click()
    root.get_by_role("button", name=name, exact=True).click()


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
    deployment_row = _deployment_row(page)
    expect(deployment_row).to_have_count(1)
    expect(deployment_row.get_by_role("cell", name="Production", exact=True)).to_be_visible()
    expect(deployment_row.get_by_role("cell", name="local-demo", exact=True)).to_be_visible()


def _add_resource_to_current_set(page: Page, resource_name: str) -> None:
    page.get_by_role("button", name="Add resource", exact=True).click()
    panel = page.get_by_role("heading", name="Add resource", exact=True).locator("xpath=..")
    panel.get_by_label("Search Resource Catalogue").fill(resource_name)
    panel.get_by_role("button", name="Search", exact=True).click()
    choice = panel.get_by_role("button").filter(has_text=resource_name)
    expect(choice).to_have_count(1)
    choice.click()
    panel.get_by_role("button", name="Add resource", exact=True).click()
    expect(page.get_by_role("cell", name=resource_name, exact=True)).to_be_visible()


def _select_option_containing(page: Page, label: str, text: str) -> None:
    select = page.get_by_label(label)
    option = select.locator("option").filter(has_text=text)
    expect(option).to_have_count(1)
    value = option.get_attribute("value")
    assert value
    select.select_option(value=value)


def _open_target_connectivity(page: Page, desktop_nav, resource_reference: str) -> None:
    desktop_nav.get_by_role("button", name="Connectivity").click()
    expect(page.get_by_role("heading", name="Connectivity", exact=True)).to_be_visible()
    page.get_by_placeholder("Resource reference…").fill(resource_reference)
    page.get_by_role("button", name="Search", exact=True).click()
    expect(page.get_by_text(resource_reference, exact=True)).to_be_visible()
    expect(page.get_by_text("Web UI", exact=True)).to_be_visible()
    expect(page.get_by_text("Orders API", exact=True)).to_be_visible()


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

        web_resource_reference = _create_resource(
            page,
            desktop_nav,
            name="J01 Web Resource",
            address="10.31.0.10",
        )
        _create_resource(
            page,
            desktop_nav,
            name="J01 API Resource",
            address="10.31.0.20",
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
        _deployment_row(page).click()
        expect(
            page.get_by_role(
                "heading",
                name="Order Management — Company A / Production",
                exact=True,
            )
        ).to_be_visible()
        expect(page.get_by_role("heading", name="Connectivity 0 / 2", exact=True)).to_be_visible()

        page.get_by_role("button", name="Add interaction").click()
        page.get_by_label("Select Web UI to Orders API").check()
        page.get_by_label("Select Orders API to Database").check()
        page.get_by_role("button", name="Add selected").click()
        expect(page.get_by_role("heading", name="Connectivity 2 / 2", exact=True)).to_be_visible()
        expect(page.get_by_role("cell", name="TCP (443)", exact=True)).to_be_visible()
        expect(page.get_by_role("cell", name="TCP (5432)", exact=True)).to_be_visible()

        web_to_api = page.get_by_role("cell", name="Web UI", exact=True).locator("xpath=..")
        web_to_api.get_by_role("button", name="0 resources", exact=True).first.click()
        expect(page.get_by_role("heading", name="Source resources", exact=True)).to_be_visible()
        _add_resource_to_current_set(page, "J01 Web Resource")
        page.get_by_role("button", name="Deployment", exact=True).click()

        web_to_api = page.get_by_role("cell", name="Web UI", exact=True).locator("xpath=..")
        expect(web_to_api.get_by_role("button", name="1 resource", exact=True)).to_be_visible()
        web_to_api.get_by_role("button", name="0 resources", exact=True).click()
        expect(page.get_by_role("heading", name="Destination resources", exact=True)).to_be_visible()
        _add_resource_to_current_set(page, "J01 API Resource")
        page.get_by_role("button", name="Deployment", exact=True).click()

        web_to_api = page.get_by_role("cell", name="Web UI", exact=True).locator("xpath=..")
        expect(web_to_api.get_by_role("button", name="1 resource", exact=True)).to_have_count(2)

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
        deployment_row = _deployment_row(page)
        expect(deployment_row).to_have_count(1)
        expect(deployment_row.get_by_role("cell", name="Production", exact=True)).to_be_visible()
        expect(deployment_row.get_by_role("cell", name="local-demo", exact=True)).to_be_visible()
        expect(deployment_row.get_by_role("cell", name="2 / 2", exact=True)).to_be_visible()
        deployment_row.click()
        expect(page.get_by_role("heading", name="Connectivity 2 / 2", exact=True)).to_be_visible()

        # Target-authored Resource membership must feed the unchanged downstream
        # compatibility identity rather than requiring target IDs in peer contexts.
        _open_target_connectivity(page, desktop_nav, web_resource_reference)
        expect(page.get_by_text("No current need", exact=True)).to_be_visible()
        expect(page.get_by_text("No final decision", exact=True)).to_be_visible()
        expect(page.get_by_text("No rule", exact=True)).to_be_visible()

        page.get_by_role("button", name="Request access", exact=True).click()
        expect(page.get_by_role("heading", name="Request access", exact=True)).to_be_visible()
        page.get_by_label("Business justification").fill(
            "Target-authored Web UI requires the Orders API for checkout."
        )
        page.get_by_role("button", name="Request access", exact=True).click()
        expect(page.get_by_text("DecisionUnknown", exact=True)).to_be_visible()
        expect(
            page.get_by_text(
                "The Connectivity Requirement was recorded before the later access step failed.",
                exact=True,
            )
        ).to_be_visible()

        page.get_by_role("button", name="Back to Connectivity", exact=True).click()
        expect(page.get_by_text("Required", exact=True)).to_be_visible()
        expect(page.get_by_text("No final decision", exact=True)).to_be_visible()
        expect(page.get_by_text("No rule", exact=True)).to_be_visible()

        desktop_nav.get_by_role("button", name="Decisions").click()
        expect(page.get_by_role("heading", name="Decisions", exact=True)).to_be_visible()
        expect(page.get_by_label("Decision Governance Scope")).to_have_value("local-demo")
        page.get_by_placeholder("Search interactions").fill("Web UI")
        _select_option_containing(page, "Source Component Deployment", "Web UI")
        _select_option_containing(page, "Destination Component Deployment", "Orders API")
        page.get_by_label("DCS / Access").select_option(index=1)
        expect(page.get_by_label("Final outcome")).to_have_value("Allowed")
        page.get_by_label("Reason code").fill("j01-target-approved")
        page.get_by_role("textbox", name="Reason", exact=True).fill(
            "Target-authored compatibility interaction accepted end to end."
        )
        page.get_by_role("button", name="Record Decision", exact=True).click()
        expect(page.get_by_text(re.compile(r"^Decision .* recorded\.$"))).to_be_visible()

        _open_target_connectivity(page, desktop_nav, web_resource_reference)
        expect(page.get_by_text("Required", exact=True)).to_be_visible()
        expect(page.get_by_text("Allowed", exact=True)).to_be_visible()
        expect(page.get_by_text("No rule", exact=True)).to_be_visible()

        page.get_by_role("button", name="Request access", exact=True).click()
        expect(page.get_by_text("Confirm access proposal", exact=True)).to_be_visible()
        page.get_by_role("button", name="Request access", exact=True).click()
        expect(page.get_by_text("Access authorized", exact=True)).to_be_visible()
        page.locator("section").filter(has_text="Access authorized").get_by_role(
            "button", name="Back to Connectivity", exact=True
        ).click()
        expect(page.get_by_text("Required", exact=True)).to_be_visible()
        expect(page.get_by_text("Allowed", exact=True)).to_be_visible()
        expect(page.get_by_text("Covered", exact=True)).to_be_visible()
        expect(page.get_by_role("cell", name="Active · effective", exact=True)).to_be_visible()

        browser.close()
