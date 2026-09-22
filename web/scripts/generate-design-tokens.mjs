import { readFile, writeFile } from "node:fs/promises"
import { fileURLToPath } from "node:url"

const sourcePath = fileURLToPath(
  new URL("../../docs/contracts/ui/mvp-design-tokens.json", import.meta.url),
)
const targetPath = fileURLToPath(
  new URL("../src/design-system/tokens.css", import.meta.url),
)
const checkOnly = process.argv.includes("--check")

const document = JSON.parse(await readFile(sourcePath, "utf8"))
const tokens = new Map()

function collect(value, path = []) {
  if (!value || typeof value !== "object" || Array.isArray(value)) return
  if (Object.hasOwn(value, "$value")) {
    tokens.set(path.join("."), value)
    return
  }
  for (const [key, child] of Object.entries(value)) {
    if (!key.startsWith("$")) collect(child, [...path, key])
  }
}

collect(document)

function resolve(name, stack = []) {
  if (stack.includes(name)) {
    throw new Error(`Circular token alias: ${[...stack, name].join(" -> ")}`)
  }
  const token = tokens.get(name)
  if (!token) throw new Error(`Unknown token alias: ${name}`)
  const value = token.$value
  if (typeof value === "string") {
    const match = /^\{([^{}]+)\}$/.exec(value)
    if (match) return resolve(match[1], [...stack, name])
  }
  return { type: token.$type, value }
}

function cssName(name) {
  return `--napms-${name.replace(/[^a-zA-Z0-9]+/g, "-").toLowerCase()}`
}

function scalar(value) {
  if (value && typeof value === "object" && "value" in value && "unit" in value) {
    return `${value.value}${value.unit}`
  }
  return String(value)
}

const lines = [
  "/* Generated from docs/contracts/ui/mvp-design-tokens.json. Do not edit manually. */",
  ":root {",
]

for (const name of [...tokens.keys()].sort()) {
  const resolved = resolve(name)
  if (resolved.type === "color") {
    const value = resolved.value
    if (!value || typeof value !== "object") {
      throw new Error(`Invalid color token: ${name}`)
    }
    const css = value.hex
      ?? `color(${value.colorSpace} ${value.components.join(" ")})`
    lines.push(`  ${cssName(name)}: ${css};`)
  } else if (resolved.type === "dimension" || resolved.type === "number") {
    lines.push(`  ${cssName(name)}: ${scalar(resolved.value)};`)
  } else if (resolved.type === "typography") {
    const value = resolved.value
    const prefix = cssName(name)
    lines.push(`  ${prefix}-font-family: ${value.fontFamily.join(", ")};`)
    lines.push(`  ${prefix}-font-size: ${scalar(value.fontSize)};`)
    lines.push(`  ${prefix}-font-weight: ${value.fontWeight};`)
    lines.push(`  ${prefix}-line-height: ${value.lineHeight};`)
  }
}
lines.push("}", "")

const generated = lines.join("\n")

if (checkOnly) {
  const existing = await readFile(targetPath, "utf8").catch(() => "")
  if (existing !== generated) {
    console.error("Generated design tokens are stale. Run: npm run tokens:generate")
    process.exit(1)
  }
  console.log("Generated design tokens are current")
} else {
  await writeFile(targetPath, generated, "utf8")
  console.log("Generated", targetPath)
}
