import { readdir, readFile } from "node:fs/promises"
import { join, relative } from "node:path"
import { fileURLToPath } from "node:url"

const webRoot = fileURLToPath(new URL("..", import.meta.url))
const srcRoot = join(webRoot, "src")
const designSystemRoot = join(srcRoot, "design-system")
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

if (failures.length > 0) {
  console.error("UI ownership boundary check failed:\n" + failures.map((item) => `- ${item}`).join("\n"))
  process.exit(1)
}

console.log("UI ownership boundaries OK")
