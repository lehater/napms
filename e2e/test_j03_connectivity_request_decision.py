import os
import re

from playwright.sync_api import Page, expect, sync_playwright


BASE_URL = os.environ.get("NAPMS_E2E_BASE_URL", "http://127.0.0.1:8080")
LOGIN = os.environ.get("NAPMS_E2E_LOGIN", "local-admin")
PASSWORD = os.environ.get("NAPMS_E2E_PASSWORD", "local-e2e-password")


def _demo_relationship_row(page: Page):
    return (
        page.get_by_role("row")
        .filter(has_text="Demo Web Frontend")
        .filter(has_text="Demo Orders API")
        .filter(has_text="HTTPS Orders API")
    )


def _assert_demo_state(page: Page, *, need: str, decision: str, policy: str) -> None:
    row = _demo_relationship_row(page)
    expect(row).to_have_count(1)
    expect(row.get_by_text(need, exact=True)).to_be_visible()
    expect(row.get_by_text(decision, exact=True)).to_be_visible()
    expect(row.get_by_text(policy, exact=True)).to_be_visible()


def _select_option_containing(page: Page, label: str, text: str) -> None:
    select = page.get_by_label(label)
    option = select.locator("option").filter(has_text=text)
    expect(option).to_have_count(1)
    value = option.get_attribute("value")
    assert value
    select.select_option(value=value)


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

        demo_row = _demo_relationship_row(page)
        expect(demo_row).to_have_count(1)
        _assert_demo_state(
            page,
            need="No current need",
            decision="No final decision",
            policy="No rule",
        )

        demo_row.get_by_role("button", name="Request access", exact=True).click()
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
        _assert_demo_state(
            page,
            need="Required",
            decision="No final decision",
            policy="No rule",
        )

        # The same local demo principal exercises the logically independent decision
        # role. Select the seeded interaction explicitly so J03 stays isolated from
        # target-authored rows created by J01 in the same browser-gate database.
        desktop_nav.get_by_role("button", name="Decisions").click()
        expect(page.get_by_role("heading", name="Decisions", exact=True)).to_be_visible()
        expect(page.get_by_label("Decision Governance Scope")).to_have_value("local-demo")

        with page.expect_response(
            lambda response: "/api/v1/connectivity-decisions/interactions?" in response.url
            and "search=Demo+Web+Frontend" in response.url
        ):
            page.get_by_placeholder("Search interactions").fill("Demo Web Frontend")
        _select_option_containing(
            page,
            "Source Component Deployment",
            "Demo Web Frontend",
        )
        _select_option_containing(
            page,
            "Destination Component Deployment",
            "Demo Orders API",
        )
        _select_option_containing(page, "DCS / Access", "HTTPS Orders API")
        expect(page.get_by_label("Final outcome")).to_have_value("Allowed")
        page.get_by_label("Reason code").fill("j03-approved")
        page.get_by_role("textbox", name="Reason", exact=True).fill(
            "Connectivity Requirement reviewed for the J03 acceptance journey."
        )
        page.get_by_role("button", name="Record Decision", exact=True).click()
        expect(page.get_by_text(re.compile(r"^Decision .* recorded\.$"))).to_be_visible()

        desktop_nav.get_by_role("button", name="Connectivity").click()
        expect(page.get_by_role("heading", name="Connectivity", exact=True)).to_be_visible()
        _assert_demo_state(
            page,
            need="Required",
            decision="Allowed",
            policy="No rule",
        )

        # A second proposal now consumes the explicit Allowed Decision. It reuses the
        # existing Requirement and materializes the separate Access Rule state.
        _demo_relationship_row(page).get_by_role(
            "button", name="Request access", exact=True
        ).click()
        expect(page.get_by_role("heading", name="Request access", exact=True)).to_be_visible()
        expect(page.get_by_text("Confirm access proposal", exact=True)).to_be_visible()
        page.get_by_role("button", name="Request access", exact=True).click()
        expect(page.get_by_text("Access authorized", exact=True)).to_be_visible()

        result_section = page.locator("section").filter(has_text="Access authorized")
        result_section.get_by_role(
            "button", name="Back to Connectivity", exact=True
        ).click()
        expect(page.get_by_role("heading", name="Connectivity", exact=True)).to_be_visible()
        _assert_demo_state(
            page,
            need="Required",
            decision="Allowed",
            policy="Covered",
        )
        expect(
            _demo_relationship_row(page).get_by_role(
                "cell", name="Active · effective", exact=True
            )
        ).to_be_visible()

        browser.close()
