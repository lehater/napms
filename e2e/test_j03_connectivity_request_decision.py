import os
import re

from playwright.sync_api import expect, sync_playwright


BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
LOGIN = os.environ.get("NAPMS_E2E_LOGIN", "local-admin")
PASSWORD = os.environ.get("NAPMS_E2E_PASSWORD", "local-e2e-password")


def test_j03_requirement_decision_and_rule_remain_independent_authoritative_states() -> None:
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

        # Requirement creation is not authorization. Without a trustworthy final
        # Decision, proposal materialization must fail closed and preserve the need.
        expect(page.get_by_text("Access authorized", exact=True)).to_have_count(0)
        expect(page.get_by_text("DecisionUnknown", exact=True)).to_be_visible()
        expect(
            page.get_by_text(
                "The Connectivity Requirement was recorded before the later access step failed.",
                exact=True,
            )
        ).to_be_visible()

        page.get_by_role("button", name="Back to Connectivity", exact=True).click()
        expect(page.get_by_role("heading", name="Connectivity", exact=True)).to_be_visible()
        expect(page.get_by_text("Required", exact=True)).to_be_visible()
        expect(page.get_by_text("No final decision", exact=True)).to_be_visible()
        expect(page.get_by_text("No rule", exact=True)).to_be_visible()

        # The same local demo principal exercises the logically independent decision
        # role. The Decision itself remains an explicit, final authoritative record.
        desktop_nav.get_by_role("button", name="Decisions").click()
        expect(page.get_by_role("heading", name="Decisions", exact=True)).to_be_visible()
        expect(page.get_by_label("Decision Governance Scope")).to_have_value("local-demo")

        page.get_by_label("Source Component Deployment").select_option(index=1)
        page.get_by_label("Destination Component Deployment").select_option(index=1)
        page.get_by_label("DCS / Access").select_option(index=1)
        expect(page.get_by_label("Final outcome")).to_have_value("Allowed")
        page.get_by_label("Reason code").fill("j03-approved")
        page.get_by_role("textbox", name="Reason", exact=True).fill(
            "Connectivity Requirement reviewed for the J03 acceptance journey."
        )
        page.get_by_role("button", name="Record Decision", exact=True).click()
        expect(page.get_by_text(re.compile(r"^Decision .* recorded\.$"))).to_be_visible()

        desktop_nav.get_by_role("button", name="Connectivity").click()
        expect(page.get_by_role("heading", name="Connectivity", exact=True)).to_be_visible()
        expect(page.get_by_text("Required", exact=True)).to_be_visible()
        expect(page.get_by_text("Allowed", exact=True)).to_be_visible()
        expect(page.get_by_text("No rule", exact=True)).to_be_visible()

        # A second proposal now consumes the explicit Allowed Decision. It reuses the
        # existing Requirement and materializes the separate Access Rule state.
        page.get_by_role("button", name="Request access", exact=True).click()
        expect(page.get_by_role("heading", name="Request access", exact=True)).to_be_visible()
        expect(page.get_by_text("Confirm access proposal", exact=True)).to_be_visible()
        page.get_by_role("button", name="Request access", exact=True).click()
        expect(page.get_by_text("Access authorized", exact=True)).to_be_visible()

        result_section = page.locator("section").filter(has_text="Access authorized")
        result_section.get_by_role(
            "button", name="Back to Connectivity", exact=True
        ).click()
        expect(page.get_by_role("heading", name="Connectivity", exact=True)).to_be_visible()
        expect(page.get_by_text("Required", exact=True)).to_be_visible()
        expect(page.get_by_text("Allowed", exact=True)).to_be_visible()
        expect(page.get_by_text("Covered", exact=True)).to_be_visible()
        expect(page.get_by_text("Active", exact=True)).to_be_visible()

        browser.close()
