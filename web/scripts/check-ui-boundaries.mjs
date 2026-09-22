import { readdir, readFile } from "node:fs/promises";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const webRoot = fileURLToPath(new URL("..", import.meta.url));
const srcRoot = join(webRoot, "src");
const providerRoot = join(srcRoot, "presentation", "providers", "mui");

async function sourceFiles(root) {
  const result = [];
  async function walk(directory) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) await walk(path);
      else if (/\.(?:ts|tsx|js|jsx)$/.test(entry.name)) result.push(path);
    }
  }
  await walk(root);
  return result;
}

const failures = [];

for (const path of await sourceFiles(srcRoot)) {
  const content = await readFile(path, "utf8");
  const displayPath = relative(webRoot, path);
  const isMuiProvider =
    path === providerRoot || path.startsWith(providerRoot + "/");

  if (/from\s+["']@mui\//.test(content) && !isMuiProvider) {
    failures.push(
      `${displayPath}: MUI imports are restricted to presentation/providers/mui`,
    );
  }
  if (content.includes("design-system/")) {
    failures.push(
      `${displayPath}: legacy design-system imports are forbidden after provider migration`,
    );
  }
  if (content.includes("@/components/ui/")) {
    failures.push(
      `${displayPath}: legacy components/ui imports are forbidden after provider migration`,
    );
  }
}

if (failures.length > 0) {
  console.error(
    "UI ownership boundary check failed:\n" +
      failures.map((item) => `- ${item}`).join("\n"),
  );
  process.exit(1);
}

console.log("UI ownership boundaries OK");
