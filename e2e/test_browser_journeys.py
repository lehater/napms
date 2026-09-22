from __future__ import annotations

import json
import os
import ssl
import urllib.request
from uuid import uuid4

from playwright.sync_api import Browser, Page, sync_playwright

BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
OIDC_URL = os.environ.get("NAPMS_E2E_OIDC_URL", "https://127.0.0.1:8443")


def token(profile: str = "full") -> str:
    context = ssl._create_unverified_context()
    with urllib.request.urlopen(f"{OIDC_URL}/token?profile={profile}", context=context, timeout=5) as response:
        return json.load(response)["access_token"]


def page_with_token(browser: Browser, access_token: str | None = None, *, width: int = 1280) -> Page:
    context = browser.new_context(viewport={"width": width, "height": 900})
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
    line = page.get_by_text(name + " ·", exact=False).first.text_content() or ""
    return line.split("·", 1)[1].strip()


def test_browser_semantic_journey_and_shared_ui_evidence() -> None:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = page_with_token(browser)
        suffix = uuid4().hex[:8]

        resource_ref = create_resource(page, f"E2E Resource {suffix}")
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

        application_ref = create_application(page, f"E2E Application {suffix}")
        source_ref = add_component(page, application_ref, f"Source {suffix}")
        destination_ref = add_component(page, application_ref, f"Destination {suffix}")

        goto(page, "/interactions/new", "Create interaction")
        page.get_by_label("Source Component ID").fill(source_ref)
        page.get_by_label("Destination Component ID").fill(destination_ref)
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
        page.get_by_text('"ipProtocol": 6').wait_for()
        revision_text = page.get_by_text("Revision 1").locator("..").text_content() or ""
        assert "443" in revision_text and "8000" in revision_text and "8080" in revision_text

        goto(page, "/deployments/new", "Deployments")
        page.get_by_label("Component ID").fill(source_ref)
        page.get_by_label("Resource ID").fill(resource_ref)
        page.get_by_role("button", name="Create Deployment", exact=True).click()
        page.wait_for_url("**/deployments")
        page.get_by_text(f"Component {source_ref} · Resource {resource_ref}").wait_for()

        goto(page, "/business-processes/new", "Business Processes")
        page.get_by_label("Name").fill(f"E2E Process {suffix}")
        page.get_by_label("Description").fill("Independent business justification")
        page.get_by_label("Criticality").fill("HIGH")
        page.get_by_role("button", name="Create Business Process", exact=True).click()
        page.wait_for_url("**/business-processes/*")
        page.get_by_text("Independent business justification").wait_for()
        page.get_by_label("Responsible organization reference").fill("ORG-E2E")
        page.get_by_label("Responsible organization name").fill("E2E Organization")
        page.get_by_role("button", name="Save responsible organization").click()
        page.get_by_label("Interaction ID").fill(interaction_ref)
        page.get_by_label("Participant Component ID").fill(source_ref)
        page.get_by_label("Business basis").fill("Required for order processing")
        page.locator("form").get_by_role("button", name="Declare Connectivity Need", exact=True).click()
        page.get_by_text("Required for order processing").wait_for()
        page.get_by_role("button", name="Retire Connectivity Need", exact=True).wait_for()

        for path, heading in [
            ("/access-requests", "Access Requests"),
            ("/policy-rules", "Policy Rules"),
            ("/policy-materializations/new", "Policy Export"),
        ]:
            goto(page, path, heading)

        goto(page, "/access-requests/new", "Access Requests")
        assert page.get_by_role("button", name="Submit Request").is_disabled()

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
