from __future__ import annotations

import json
import os
import ssl
import urllib.request
from pathlib import Path
from uuid import uuid4

from playwright.sync_api import Browser, Page, sync_playwright

BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
OIDC_URL = os.environ.get("NAPMS_E2E_OIDC_URL", "https://127.0.0.1:8443")


def token(profile: str = "full") -> str:
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(f"{OIDC_URL}/token?profile={profile}", context=context, timeout=5) as response:
        return json.load(response)["access_token"]


def page_with_token(
    browser: Browser,
    access_token: str | None = None,
    *,
    width: int = 1280,
    height: int = 900,
) -> Page:
    context = browser.new_context(viewport={"width": width, "height": height})
    value = token("full") if access_token is None else access_token
    context.add_init_script("window.__NAPMS_RUNTIME_ACCESS_TOKEN__ = " + json.dumps(value) + ";")
    page = context.new_page()
    return page


def goto(page: Page, path: str, heading: str) -> None:
    page.goto(f"{BASE_URL}{path}")
    page.get_by_role("heading", name=heading).wait_for()


def create_resource(page: Page, name: str) -> str:
    goto(page, "/resources/new", "Resources")
    page.get_by_label("Display name").fill(name)
    page.get_by_label("Authority scope").fill("e2e-scope")
    page.get_by_role("button", name="Create Resource", exact=True).click()
    page.wait_for_url(lambda url: "/resources/" in url and not url.endswith("/resources/new"))
    return page.url.rsplit("/", 1)[-1]


def create_application(page: Page, name: str) -> str:
    goto(page, "/applications/new", "Applications")
    page.get_by_label("Name").fill(name)
    page.get_by_role("button", name="Create Application", exact=True).click()
    page.wait_for_url(lambda url: "/applications/" in url and not url.endswith("/applications/new"))
    return page.url.rsplit("/", 1)[-1]


def add_component(page: Page, application_ref: str, name: str) -> str:
    page.goto(f"{BASE_URL}/applications/{application_ref}/components/new")
    page.get_by_role("heading", name="Components").wait_for()
    page.get_by_label("Component name").fill(name)
    page.locator("form").get_by_role("button", name="Add Component", exact=True).click()
    page.wait_for_url(f"**/applications/{application_ref}")
    row = page.get_by_role("list", name="Components").locator("li", has_text=name)
    marker = row.locator("[data-component-ref]").first
    component_ref = marker.get_attribute("data-component-ref")
    assert component_ref
    return component_ref


def test_00_rendered_presentation_evidence() -> None:
    artifacts = Path("e2e-artifacts")
    artifacts.mkdir(exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = page_with_token(browser, width=1440, height=1000)

        create_resource(page, "Rendered Resource")

        drawer = page.locator(".MuiDrawer-paper")
        drawer_box = drawer.bounding_box()
        assert drawer_box is not None
        assert round(drawer_box["width"]) == 232

        main = page.locator("main")
        padding_left = page.evaluate(
            "(element) => parseFloat(getComputedStyle(element).paddingLeft)",
            main.element_handle(),
        )
        assert round(padding_left) == 24

        title_size = page.evaluate(
            "(element) => getComputedStyle(element).fontSize",
            page.get_by_role("heading", name="Rendered Resource").element_handle(),
        )
        assert title_size == "20px"

        detail = page.locator('[data-presentation-pattern="detail"]')
        main_box = main.bounding_box()
        detail_box = detail.bounding_box()
        assert main_box is not None and detail_box is not None
        expected_detail_width = main_box["width"] - (2 * padding_left)
        assert abs(detail_box["width"] - expected_detail_width) <= 1

        page.screenshot(
            path=str(artifacts / "resource-detail-desktop.png"),
            full_page=True,
            mask=[page.locator("[data-presentation-technical-context]")],
            mask_color="#E2E8F0",
        )

        goto(page, "/resources", "Resources")
        page.locator('[data-presentation-pattern="filter-bar"]').wait_for()
        header_cell = page.locator("thead th").first
        body_row = page.locator("tbody tr").first
        header_box = header_cell.bounding_box()
        row_box = body_row.bounding_box()
        assert header_box is not None and row_box is not None
        assert round(header_box["height"]) == 40
        assert round(row_box["height"]) == 40

        page.screenshot(
            path=str(artifacts / "resource-catalogue-desktop.png"),
            full_page=True,
            mask=[page.locator('[data-emphasis="technical"]')],
            mask_color="#E2E8F0",
        )

        narrow = page_with_token(browser, width=390, height=900)
        goto(narrow, "/resources", "Resources")
        assert not narrow.locator(".MuiDrawer-paper").is_visible()
        assert narrow.get_by_role("navigation", name="Primary").is_visible()
        narrow.screenshot(
            path=str(artifacts / "resource-catalogue-narrow.png"),
            full_page=True,
            mask=[narrow.locator('[data-emphasis="technical"]')],
            mask_color="#E2E8F0",
        )

        browser.close()


def test_browser_semantic_journey_and_shared_ui_evidence() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = page_with_token(browser)
        suffix = uuid4().hex[:8]

        resource_name = f"E2E Resource {suffix}"
        resource_ref = create_resource(page, resource_name)

        goto(page, "/resources", "Resources")
        page.get_by_label("Search Resources").fill(resource_name)
        page.get_by_label("Authority scope").fill("e2e-scope")
        page.get_by_label("Sort by").click()
        page.get_by_role("option", name="Reference").click()
        page.get_by_label("Sort direction").click()
        page.get_by_role("option", name="Descending").click()
        resource_row = page.locator("tbody tr", has_text=resource_name)
        resource_row.wait_for()
        assert resource_ref in (resource_row.text_content() or "")
        resource_row.click()
        page.wait_for_url(f"**/resources/{resource_ref}")
        breadcrumb = page.get_by_role("navigation", name="Breadcrumb")
        breadcrumb.get_by_role("button", name="Resources", exact=True).wait_for()

        page.get_by_role("heading", name="Current facts").wait_for()
        page.locator("[data-version]").wait_for()
        assert page.locator("[data-version]").get_attribute("data-version") == "1"
        page.get_by_role("button", name="Add endpoint", exact=True).click()
        page.locator('[data-version="2"]').wait_for()
        endpoint_line = page.locator("h4", has_text="Endpoints").locator("xpath=following-sibling::p[1]")
        endpoint_ref = (endpoint_line.text_content() or "").split(" · ")[0].strip()
        page.get_by_label("Endpoint ID").fill(endpoint_ref)
        page.get_by_label("Address value").fill("10.10.0.1")
        page.get_by_role("button", name="Set endpoint address", exact=True).click()
        page.locator('[data-version="3"]').wait_for()
        page.get_by_text("HOST 10.10.0.1").wait_for()
        page.get_by_text("Provenance and history").click()

        breadcrumb.get_by_role("button", name="Resources", exact=True).click()
        page.wait_for_url("**/resources")
        page.get_by_role("heading", name="Resources").wait_for()
        page.get_by_label("Search Resources").fill(resource_name)
        refreshed_row = page.locator("tbody tr", has_text=resource_name)
        refreshed_row.wait_for()
        assert "HOST 10.10.0.1" in (refreshed_row.text_content() or "")

        application_name = f"E2E Application {suffix}"
        application_ref = create_application(page, application_name)
        source_name = f"Source {suffix}"
        destination_name = f"Destination {suffix}"
        source_ref = add_component(page, application_ref, source_name)
        destination_ref = add_component(page, application_ref, destination_name)

        goto(page, "/applications", "Applications")
        page.get_by_label("Search Applications").fill(application_name)
        page.get_by_label("Component ID").fill(source_ref)
        page.get_by_label("Sort by").click()
        page.get_by_role("option", name="Reference").click()
        page.get_by_label("Sort direction").click()
        page.get_by_role("option", name="Descending").click()
        application_row = page.locator("tbody tr", has_text=application_name)
        application_row.wait_for()
        assert application_ref in (application_row.text_content() or "")
        application_row.click()
        page.wait_for_url(f"**/applications/{application_ref}")

        goto(page, "/interactions/new", "Create interaction")
        page.get_by_label("Source Component").fill(source_name)
        page.get_by_role("option", name=f"{source_name} — {application_name}").click()
        page.get_by_label("Destination Component").fill(destination_name)
        page.get_by_role(
            "option", name=f"{destination_name} — {application_name}"
        ).click()
        page.get_by_label("Purpose").fill("E2E directed business flow")
        page.get_by_role("button", name="Create interaction").click()
        page.wait_for_url("**/interactions/*/revisions/new")
        interaction_ref = page.url.split("/interactions/", 1)[1].split("/", 1)[0]
        page.get_by_label("IP protocol number").fill("6")
        page.get_by_label("Source ports").fill("1024-65535")
        page.get_by_label("Destination ports").fill("443,8000-8080")
        page.get_by_role("button", name="Publish revision").click()

        goto(page, f"/applications/{application_ref}", f"E2E Application {suffix}")
        page.get_by_text("E2E directed business flow").wait_for()
        page.get_by_text(source_name, exact=True).wait_for()
        page.get_by_text(destination_name, exact=True).wait_for()
        page.get_by_text('"ipProtocol": 6').wait_for()
        revision_text = page.get_by_text("Revision 1").locator("..").text_content() or ""
        assert "443" in revision_text and "8000" in revision_text and "8080" in revision_text
        revision_block = page.locator("[data-interaction-revision-ref]").filter(
            has_text="Revision 1"
        ).first
        interaction_revision_ref = revision_block.get_attribute(
            "data-interaction-revision-ref"
        )
        assert interaction_revision_ref

        goto(page, "/deployments/new", "Deployments")
        page.get_by_label("Component").fill(source_name)
        page.get_by_role("option", name=f"{source_name} — {application_name}").click()
        page.get_by_label("Resource").fill(resource_name)
        page.get_by_role("option", name=resource_name, exact=True).click()
        page.get_by_role("button", name="Create Deployment", exact=True).click()
        page.wait_for_url(lambda url: "/deployments/" in url and not url.endswith("/deployments/new"))
        deployment_ref = page.url.rsplit("/", 1)[-1]
        page.get_by_role("heading", name="Deployment").wait_for()
        page.get_by_text(source_name, exact=True).wait_for()
        page.get_by_text(resource_name, exact=True).wait_for()
        page.get_by_text(source_ref, exact=True).wait_for()
        page.get_by_text(resource_ref, exact=True).wait_for()

        goto(page, "/deployments", "Deployments")
        page.get_by_label("Search Deployments").fill(deployment_ref)
        page.get_by_label("Component ID").fill(source_ref)
        page.get_by_label("Resource ID").fill(resource_ref)
        page.get_by_label("Sort by").click()
        page.get_by_role("option", name="Resource").click()
        page.get_by_label("Sort direction").click()
        page.get_by_role("option", name="Descending").click()
        deployment_row = page.locator("tbody tr", has_text=deployment_ref)
        deployment_row.wait_for()
        deployment_text = deployment_row.text_content() or ""
        assert source_name in deployment_text
        assert resource_name in deployment_text
        assert source_ref in deployment_text
        assert resource_ref in deployment_text
        deployment_row.click()
        page.wait_for_url(f"**/deployments/{deployment_ref}")

        goto(page, "/deployments/new", "Deployments")
        page.get_by_label("Component").fill(destination_name)
        page.get_by_role(
            "option", name=f"{destination_name} — {application_name}"
        ).click()
        page.get_by_label("Resource").fill(resource_name)
        page.get_by_role("option", name=resource_name, exact=True).click()
        page.get_by_role("button", name="Create Deployment", exact=True).click()
        page.wait_for_url(
            lambda url: "/deployments/" in url
            and not url.endswith("/deployments/new")
        )
        destination_deployment_ref = page.url.rsplit("/", 1)[-1]

        process_name = f"E2E Process {suffix}"
        goto(page, "/business-processes/new", "Business Processes")
        page.get_by_label("Name").fill(process_name)
        page.get_by_label("Description").fill("Independent business justification")
        page.get_by_label("Criticality").fill("HIGH")
        page.get_by_role("button", name="Create Business Process", exact=True).click()
        page.wait_for_url(
            lambda url: "/business-processes/" in url
            and not url.endswith("/business-processes/new")
        )
        process_ref = page.url.rsplit("/", 1)[-1]
        page.get_by_text("Independent business justification").wait_for()
        page.get_by_label("Responsible organization reference").fill("ORG-E2E")
        page.get_by_label("Responsible organization name").fill("E2E Organization")
        page.get_by_role("button", name="Save responsible organization").click()
        page.locator('[data-version="2"]').wait_for()
        interaction_label = (
            f"{source_name} — {application_name} → "
            f"{destination_name} — {application_name} — E2E directed business flow"
        )
        page.get_by_label("Interaction").fill("E2E directed business flow")
        page.get_by_role("option", name=interaction_label).click()
        page.get_by_label("Participant Component").click()
        page.get_by_role(
            "option", name=f"{source_name} — {application_name}"
        ).click()
        page.get_by_label("Business basis").fill("Required for order processing")
        page.locator("form").get_by_role("button", name="Declare Connectivity Need", exact=True).click()
        page.locator('[data-version="3"]').wait_for()
        page.get_by_text("Required for order processing").wait_for()
        need_marker = page.locator("[data-connectivity-need-ref]").filter(
            has_text="Required for order processing"
        ).first
        need_ref = need_marker.get_attribute("data-connectivity-need-ref")
        assert need_ref
        page.get_by_role("button", name="Retire Connectivity Need", exact=True).wait_for()

        goto(page, "/business-processes", "Business Processes")
        page.get_by_label("Search Business Processes").fill(process_name)
        page.get_by_label("Criticality").fill("HIGH")
        page.get_by_label("Responsible organization reference").fill("ORG-E2E")
        page.get_by_label("Sort by").click()
        page.get_by_role("option", name="Reference").click()
        page.get_by_label("Sort direction").click()
        page.get_by_role("option", name="Descending").click()
        process_row = page.locator("tbody tr", has_text=process_name)
        process_row.wait_for()
        assert process_ref in (process_row.text_content() or "")
        assert "E2E Organization" in (process_row.text_content() or "")
        process_row.click()
        page.wait_for_url(f"**/business-processes/{process_ref}")
        page.get_by_text("Required for order processing").wait_for()

        goto(page, "/access-requests/new", "Access Requests")
        page.get_by_label("Source Deployment ID").fill(deployment_ref)
        page.get_by_label("Destination Deployment ID").fill(
            destination_deployment_ref
        )
        page.get_by_label("Interaction Revision ID").fill(interaction_revision_ref)
        page.get_by_label("Connectivity Need ID").fill(need_ref)
        page.get_by_role("button", name="Submit Request", exact=True).click()
        page.wait_for_url("**/access-requests/*/decision")
        request_ref = page.url.split("/access-requests/", 1)[1].split("/", 1)[0]

        goto(page, "/access-requests", "Access Requests")
        page.get_by_label("Search Access Requests").fill(request_ref)
        page.get_by_label("Source Deployment ID").fill(deployment_ref)
        page.get_by_label("Destination Deployment ID").fill(
            destination_deployment_ref
        )
        page.get_by_label("Sort by").click()
        page.get_by_role("option", name="Request").click()
        page.get_by_label("Sort direction").click()
        page.get_by_role("option", name="Descending").click()
        request_row = page.locator("tbody tr", has_text=request_ref)
        request_row.wait_for()
        assert "PENDING" in (request_row.text_content() or "")
        request_row.click()
        page.wait_for_url(f"**/access-requests/{request_ref}/decision")

        page.get_by_label("External decision reference").fill(
            f"E2E-decision-{suffix}"
        )
        page.get_by_role("button", name="Record Decision", exact=True).click()
        page.wait_for_url("**/policy-rules/*")
        policy_rule_ref = page.url.rsplit("/", 1)[-1]
        page.get_by_role("heading", name="Policy Rules").wait_for()
        page.get_by_text(deployment_ref, exact=False).wait_for()
        page.get_by_text(destination_deployment_ref, exact=False).wait_for()

        goto(page, "/access-requests", "Access Requests")
        page.get_by_label("Search Access Requests").fill(request_ref)
        page.get_by_label("Source Deployment ID").fill(deployment_ref)
        page.get_by_label("Destination Deployment ID").fill(
            destination_deployment_ref
        )
        page.get_by_label("Decision").click()
        page.get_by_role("option", name="Allowed").click()
        decided_row = page.locator("tbody tr", has_text=request_ref)
        decided_row.wait_for()
        assert "ALLOWED" in (decided_row.text_content() or "")

        goto(page, "/policy-rules", "Policy Rules")
        page.get_by_label("Search Policy Rules").fill(policy_rule_ref)
        page.get_by_label("Source Deployment ID").fill(deployment_ref)
        page.get_by_label("Destination Deployment ID").fill(
            destination_deployment_ref
        )
        page.get_by_label("State").click()
        page.get_by_role("option", name="Active", exact=True).click()
        page.get_by_label("Sort by").click()
        page.get_by_role("option", name="State").click()
        page.get_by_label("Sort direction").click()
        page.get_by_role("option", name="Descending").click()
        policy_row = page.locator("tbody tr", has_text=policy_rule_ref)
        policy_row.wait_for()
        assert deployment_ref in (policy_row.text_content() or "")
        assert destination_deployment_ref in (policy_row.text_content() or "")
        policy_row.click()
        page.wait_for_url(f"**/policy-rules/{policy_rule_ref}")

        goto(page, "/policy-materializations/new", "Policy Export")
        page.get_by_role("button", name="Execute Export").click()
        page.get_by_text("Export result: COMPLETE").wait_for()
        page.get_by_text("Provenance and history").click()
        page.get_by_role("heading", name="Rule provenance").wait_for()

        mobile = page_with_token(browser, width=390)
        goto(mobile, "/resources", "Resources")
        assert mobile.get_by_role("button", name="Create Resource").is_visible()
        mobile.keyboard.press("Tab")
        assert mobile.evaluate("document.activeElement !== document.body")
        browser.close()
