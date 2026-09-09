import AxeBuilder from "@axe-core/playwright"
import { expect, test, type Page, type TestInfo } from "@playwright/test"

const loginName = process.env.NAPMS_E2E_LOGIN ?? "ui-test"
const password = process.env.NAPMS_E2E_PASSWORD ?? "ui-test-password"

async function login(page: Page) {
  await page.goto("/")
  await expect(page.getByRole("heading", { name: "Sign in to NAPMS" })).toBeVisible()
  await page.getByLabel("Login").fill(loginName)
  await page.getByLabel("Password").fill(password)
  await page.getByRole("button", { name: "Sign in" }).click()
  await expect(
    page.getByRole("heading", { name: "Compose Connectivity" }),
  ).toBeVisible()
}

async function selectByText(page: Page, label: string, text: string) {
  const select = page.getByLabel(label)
  await expect(select).toBeEnabled()
  const option = select.locator("option").filter({ hasText: text }).first()
  await expect(option).toHaveCount(1)
  const value = await option.getAttribute("value")
  expect(value, `option ${text} must have a value`).toBeTruthy()
  await select.selectOption(value!)
}

async function expectNoSeriousAccessibilityViolations(page: Page) {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze()
  const blocking = results.violations.filter(
    (violation) =>
      violation.impact === "critical" || violation.impact === "serious",
  )
  expect(
    blocking,
    blocking
      .map(
        (violation) =>
          `${violation.impact}: ${violation.id} — ${violation.help}; targets: ${violation.nodes
            .flatMap((node) => node.target)
            .join(", ")}`,
      )
      .join("\n"),
  ).toEqual([])
}

async function expectNoDocumentHorizontalOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }))
  expect(
    dimensions.scrollWidth,
    `document overflows horizontally: ${JSON.stringify(dimensions)}`,
  ).toBeLessThanOrEqual(dimensions.clientWidth)
}

async function attachScreenshot(
  page: Page,
  testInfo: TestInfo,
  name: string,
) {
  await testInfo.attach(name, {
    body: await page.screenshot({ fullPage: true }),
    contentType: "image/png",
  })
}

test.describe.configure({ mode: "serial" })

test("login handles failure, success and logout through visible controls", async ({
  page,
}, testInfo) => {
  await page.goto("/")
  await expect(page.getByRole("heading", { name: "Sign in to NAPMS" })).toBeVisible()
  await expectNoSeriousAccessibilityViolations(page)

  await page.getByLabel("Login").fill(loginName)
  await page.getByLabel("Password").fill("definitely-wrong")
  await page.getByRole("button", { name: "Sign in" }).click()
  await expect(page.getByRole("alert")).toBeVisible()

  await page.getByLabel("Password").fill(password)
  await page.getByRole("button", { name: "Sign in" }).click()
  await expect(
    page.getByRole("heading", { name: "Compose Connectivity" }),
  ).toBeVisible()

  await attachScreenshot(page, testInfo, "compose-after-login")
  await page.getByRole("button", { name: "Logout" }).click()
  await expect(page.getByRole("heading", { name: "Sign in to NAPMS" })).toBeVisible()
})

test("desktop navigation exposes every implemented workspace without layout overflow", async ({
  page,
}, testInfo) => {
  await login(page)

  const destinations = [
    ["My Connectivity Needs", "My Connectivity Needs"],
    ["Compose Connectivity", "Compose Connectivity"],
    ["Access Rules", "Access Rules"],
    ["Effective Policy", "Effective Desired Policy"],
    ["Normalized Policy", "Normalized Policy"],
  ] as const

  for (const [buttonName, headingName] of destinations) {
    await page.getByRole("button", { name: buttonName, exact: true }).click()
    await expect(page.getByRole("heading", { name: headingName })).toBeVisible()
    await expectNoDocumentHorizontalOverflow(page)
    await expectNoSeriousAccessibilityViolations(page)
    await attachScreenshot(
      page,
      testInfo,
      `desktop-${buttonName.toLowerCase().replaceAll(" ", "-")}`,
    )
  }
})

test("critical user journey persists Requirement and Access Rule mutations after reload", async ({
  page,
}, testInfo) => {
  await login(page)
  await page
    .getByRole("button", { name: "My Connectivity Needs", exact: true })
    .click()
  await expect(page.getByRole("heading", { name: "My Connectivity Needs" })).toBeVisible()

  await expect(page.getByLabel("Requirement Governance Scope")).toHaveValue(
    "local-demo",
  )
  await selectByText(page, "Source Component Deployment", "Demo Web Frontend")
  await selectByText(page, "Destination Component Deployment", "Demo Orders API")
  await selectByText(
    page,
    "Directed Communication Specification revision",
    "HTTPS Orders API",
  )
  await selectByText(
    page,
    "Dependent Component Deployment",
    "Demo Web Frontend",
  )
  await page
    .getByLabel("Business justification")
    .fill("Browser quality gate connectivity requirement.")
  await page.getByRole("button", { name: "Declare Requirement" }).click()
  await expect(page.getByRole("status")).toContainText(
    "Connectivity Requirement declared.",
  )

  const requirementRow = page
    .getByRole("row")
    .filter({ hasText: "Demo Web Frontend" })
    .filter({ hasText: "Demo Orders API" })
    .filter({ hasText: "local-demo" })
    .first()
  await expect(requirementRow).toBeVisible()
  await requirementRow
    .getByRole("button", { name: /Open Requirement/i })
    .click()

  await expect(page.getByRole("heading", { name: "Requirement lifecycle" })).toBeVisible()
  const justification = page.getByRole("textbox", {
    name: "Business justification",
  })
  await justification.fill("Browser quality gate updated justification.")
  await page.getByRole("button", { name: "Save justification" }).click()
  await expect(page.getByRole("status")).toContainText("justification")
  await page.reload()
  await expect(justification).toHaveValue(
    "Browser quality gate updated justification.",
  )

  await page
    .getByRole("button", { name: "Compose Connectivity", exact: true })
    .click()
  await expect(page.getByLabel("Governance scope")).toHaveValue("local-demo")
  await selectByText(page, "Source Component Deployment", "Demo Web Frontend")
  await selectByText(page, "Destination Component Deployment", "Demo Orders API")
  await selectByText(
    page,
    "Directed Communication Specification revision",
    "HTTPS Orders API",
  )
  await page.getByRole("button", { name: "Submit proposal" }).click()
  await expect(page.getByText(/Materialized|Resolved/).first()).toBeVisible()

  await page.getByRole("button", { name: "Access Rules", exact: true }).click()
  const ruleRow = page
    .getByRole("row")
    .filter({ hasText: "Demo Web Frontend" })
    .filter({ hasText: "Demo Orders API" })
    .first()
  await expect(ruleRow).toBeVisible()
  await ruleRow.getByRole("button", { name: /^Open Rule / }).click()

  await expect(page.getByRole("heading", { name: "Operational state" })).toBeVisible()
  await page.getByRole("button", { name: "Set Inactive" }).click()
  await expect(page.getByRole("button", { name: "Set Active" })).toBeVisible()
  await page.reload()
  await expect(page.getByRole("button", { name: "Set Active" })).toBeVisible()

  await attachScreenshot(page, testInfo, "rule-inactive-after-reload")
  await expectNoSeriousAccessibilityViolations(page)
})

test("request failure is visible and does not leave Compose submit actionable", async ({
  page,
}) => {
  await page.route("**/api/v1/access-rule-proposals/scopes", async (route) => {
    await route.abort("failed")
  })

  await login(page)
  await expect(page.getByRole("alert")).toBeVisible()
  await expect(page.getByRole("button", { name: "Submit proposal" })).toBeDisabled()
})

test("mobile shell navigation fits the viewport and remains operable", async ({
  page,
}, testInfo) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await login(page)

  const mobileDestinations = [
    ["Needs", "My Connectivity Needs"],
    ["Compose", "Compose Connectivity"],
    ["Rules", "Access Rules"],
    ["Effective", "Effective Desired Policy"],
    ["Normalized", "Normalized Policy"],
  ] as const

  for (const [buttonName, headingName] of mobileDestinations) {
    await page.getByRole("button", { name: buttonName, exact: true }).click()
    await expect(page.getByRole("heading", { name: headingName })).toBeVisible()
    await expectNoDocumentHorizontalOverflow(page)
  }

  await attachScreenshot(page, testInfo, "mobile-normalized-policy")
})
