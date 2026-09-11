import { readdir, readFile } from "node:fs/promises"
import { join, relative } from "node:path"
import { fileURLToPath } from "node:url"

const webRoot = fileURLToPath(new URL("..", import.meta.url))
const srcRoot = join(webRoot, "src")
const designSystemRoot = join(srcRoot, "design-system")
const featureRoot = join(srcRoot, "features")
const legacyUiRoot = join(srcRoot, "components", "ui")

async function sourceFiles(root) {
  const result = []
  async function walk(directory) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name)
      if (entry.isDirectory()) await walk(path)
      else if (/\.(?:ts|tsx|js|jsx)$/.test(entry.name)) result.push(path)
    }
  }
  await walk(root)
  return result
}

const failures = []

for (const path of await sourceFiles(designSystemRoot)) {
  const content = await readFile(path, "utf8")
  if (content.includes("@/components/ui/")) {
    failures.push(
      `${relative(webRoot, path)}: design-system must not depend on legacy components/ui`,
    )
  }
  if (content.includes("@/features/")) {
    failures.push(
      `${relative(webRoot, path)}: generic design-system must not depend on feature semantics`,
    )
  }
}

for (const path of await sourceFiles(legacyUiRoot)) {
  const content = await readFile(path, "utf8")
  if (!content.includes("@/design-system/components/")) {
    failures.push(
      `${relative(webRoot, path)}: legacy components/ui may only delegate to design-system components`,
    )
  }
  if (content.includes("@/features/")) {
    failures.push(
      `${relative(webRoot, path)}: legacy compatibility adapters must not depend on features`,
    )
  }
}

const tailwindPalette = /(?:^|[\s"'`])(?:bg|text|border|ring|outline|fill|stroke)-(?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)-(?:50|100|200|300|400|500|600|700|800|900|950)(?=$|[\s"'`:/])/m
const namedColor = /(?:^|[\s"'`])(?:bg|text|border|ring|outline|fill|stroke)-(?:white|black)(?=$|[\s"'`:/])/m
const rawHexColor = /#[0-9a-fA-F]{3,8}\b/
const localPageWidth = /(?:^|[\s"'`])max-w-\[(?:\d+(?:\.\d+)?)(?:px|rem|em|vw|%)\](?=$|[\s"'`:/])/m
const arbitraryTypography = /(?:^|[\s"'`])text-\[(?:\d+(?:\.\d+)?)(?:px|rem|em)\](?=$|[\s"'`:/])/m
const arbitraryRadius = /(?:^|[\s"'`])rounded-\[(?!var\()[^\]]+\](?=$|[\s"'`:/])/m
const arbitraryShadow = /(?:^|[\s"'`])shadow-\[(?!var\()[^\]]+\](?=$|[\s"'`:/])/m

for (const path of await sourceFiles(featureRoot)) {
  const content = await readFile(path, "utf8")
  const displayPath = relative(webRoot, path)

  if (content.includes("@/components/ui/")) {
    failures.push(`${displayPath}: feature code must import durable design-system owners, not legacy components/ui`)
  }
  if (rawHexColor.test(content)) {
    failures.push(`${displayPath}: raw hex colors belong in design-system tokens, not feature code`)
  }
  if (tailwindPalette.test(content) || namedColor.test(content)) {
    failures.push(`${displayPath}: Tailwind palette colors belong in design-system tokens/components, not feature code`)
  }
  if (localPageWidth.test(content)) {
    failures.push(`${displayPath}: local fixed max-width belongs in PageWorkspace width presets`)
  }
  if (arbitraryTypography.test(content)) {
    failures.push(`${displayPath}: arbitrary typography sizes belong in design-system tokens/components`)
  }
  if (arbitraryRadius.test(content) || arbitraryShadow.test(content)) {
    failures.push(`${displayPath}: arbitrary radius/shadow values belong in design-system tokens/components`)
  }
  if (/<table\b/i.test(content)) {
    failures.push(`${displayPath}: feature tables must compose the shared DataTable pattern`)
  }
}

if (failures.length > 0) {
  console.error("UI ownership boundary check failed:\n" + failures.map((item) => `- ${item}`).join("\n"))
  process.exit(1)
}

console.log("UI ownership boundaries OK")
