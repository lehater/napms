import { readFile, writeFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";

const sourcePath = fileURLToPath(
  new URL("../../docs/contracts/ui/mvp-design-tokens.json", import.meta.url),
);
const targetPath = fileURLToPath(
  new URL("../src/presentation/providers/mui/theme-tokens.generated.ts", import.meta.url),
);
const checkOnly = process.argv.includes("--check");

const document = JSON.parse(await readFile(sourcePath, "utf8"));

function lookup(path) {
  return path.split(".").reduce((value, key) => value?.[key], document);
}

function resolve(path, stack = []) {
  if (stack.includes(path)) {
    throw new Error(`Circular token alias: ${[...stack, path].join(" -> ")}`);
  }
  const token = lookup(path);
  if (!token || typeof token !== "object" || !Object.hasOwn(token, "$value")) {
    throw new Error(`Unknown token: ${path}`);
  }
  const value = token.$value;
  if (typeof value === "string") {
    const match = /^\{([^{}]+)\}$/.exec(value);
    if (match) return resolve(match[1], [...stack, path]);
  }
  return value;
}

function color(path) {
  const value = resolve(path);
  if (!value || typeof value !== "object" || typeof value.hex !== "string") {
    throw new Error(`Expected color token: ${path}`);
  }
  return value.hex;
}

function dimension(path) {
  const value = resolve(path);
  if (!value || typeof value !== "object" || typeof value.value !== "number") {
    throw new Error(`Expected dimension token: ${path}`);
  }
  return value.value;
}

function typography(path) {
  const value = resolve(path);
  if (!value || typeof value !== "object") {
    throw new Error(`Expected typography token: ${path}`);
  }
  return {
    fontFamily: value.fontFamily.join(", "),
    fontSize: value.fontSize.value,
    fontWeight: value.fontWeight,
    lineHeight: value.lineHeight,
    letterSpacing: value.letterSpacing.value,
  };
}

const tokens = {
  color: {
    navigationBackground: color("semantic.color.navigation.background"),
    navigationSelected: color("semantic.color.navigation.selected"),
    navigationText: color("semantic.color.navigation.text"),
    navigationMutedText: color("semantic.color.navigation.muted-text"),
    pageBackground: color("semantic.color.surface.page"),
    surface: color("semantic.color.surface.default"),
    surfaceSubtle: color("semantic.color.surface.subtle"),
    surfaceMuted: color("semantic.color.surface.muted"),
    textPrimary: color("semantic.color.text.primary"),
    textSecondary: color("semantic.color.text.secondary"),
    textMuted: color("semantic.color.text.muted"),
    border: color("semantic.color.border.default"),
    primary: color("semantic.color.action.primary"),
    primaryHover: color("semantic.color.action.primary-hover"),
    primaryActive: color("semantic.color.action.primary-active"),
    focus: color("semantic.color.focus.ring"),
    success: color("semantic.color.status.success"),
    warning: color("semantic.color.status.warning"),
    danger: color("semantic.color.status.danger"),
    info: color("semantic.color.status.info"),
  },
  spacing: {
    inline: dimension("semantic.spacing.inline"),
    control: dimension("semantic.spacing.control"),
    group: dimension("semantic.spacing.group"),
    section: dimension("semantic.spacing.section"),
    page: dimension("semantic.spacing.page"),
  },
  radius: {
    control: dimension("semantic.radius.control"),
    surface: dimension("semantic.radius.surface"),
    dialog: dimension("semantic.radius.dialog"),
  },
  typography: {
    pageTitle: typography("typography.page-title"),
    sectionTitle: typography("typography.section-title"),
    body: typography("typography.body"),
    metadata: typography("typography.metadata"),
  },
  component: {
    sidebarWidth: dimension("component.app-shell.sidebar-width"),
    workspacePadding: dimension("component.app-shell.workspace-padding"),
    controlHeight: dimension("component.control.height"),
    tableHeaderHeight: dimension("component.table.header-height"),
    tableRowHeight: dimension("component.table.row-height"),
    tableSelectionColumnWidth: dimension("component.table.selection-column-width"),
    tableCellPaddingX: dimension("component.table.cell-padding-x"),
    tableCellPaddingY: dimension("component.table.cell-padding-y"),
  },
};

const generated =
  "// Generated from docs/contracts/ui/mvp-design-tokens.json. Do not edit manually.\n" +
  "export const muiThemeTokens = " +
  JSON.stringify(tokens, null, 2) +
  " as const;\n";

if (checkOnly) {
  const existing = await readFile(targetPath, "utf8").catch(() => "");
  if (existing !== generated) {
    console.error("Generated MUI theme tokens are stale. Run: npm run tokens:generate");
    process.exit(1);
  }
  console.log("Generated MUI theme tokens are current");
} else {
  await writeFile(targetPath, generated, "utf8");
  console.log("Generated", targetPath);
}
