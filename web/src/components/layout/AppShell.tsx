import { useEffect, useState } from "react"
import {
  ClipboardList,
  Clock3,
  ListTree,
  LogOut,
  Menu,
  Network,
  PanelLeftClose,
  TableProperties,
} from "lucide-react"

import type { Actor } from "@/api"
import { Button } from "@/components/ui/Button"

export type NavKey =
  | "requirements"
  | "decisions"
  | "compose"
  | "rules"
  | "effective"
  | "normalized"
  | "technical-evidence"
  | "access-resolution"
  | "enforcement-placement"
  | "reconciliation"
  | "configuration-rendering"
  | "network-operations"
  | "explainability-audit"

type PreviewNav = {
  key: NavKey
  label: string
  increment: string
}

const previewTechnicalAccess: PreviewNav[] = [
  { key: "technical-evidence", label: "Technical Evidence", increment: "I17" },
  { key: "access-resolution", label: "Access Resolution", increment: "I18" },
]

const previewEnforcement: PreviewNav[] = [
  {
    key: "enforcement-placement",
    label: "Enforcement Placement",
    increment: "I19",
  },
  { key: "reconciliation", label: "Reconciliation", increment: "I20" },
  {
    key: "configuration-rendering",
    label: "Configuration Rendering",
    increment: "I21",
  },
]

function PreviewBadge({ increment }: { increment: string }) {
  return (
    <span className="ml-auto rounded border border-blue-300/30 bg-blue-300/10 px-1.5 py-0.5 text-[10px] font-semibold text-blue-100">
      Preview {increment}
    </span>
  )
}

export function AppShell({
  actor,
  activeNav,
  onNavigate,
  onLogout,
  children,
}: {
  actor: Actor
  activeNav: NavKey
  onNavigate: (target: NavKey) => void
  onLogout: () => Promise<void>
  children: React.ReactNode
}) {
  const [mobileNavigationOpen, setMobileNavigationOpen] = useState(false)

  useEffect(() => {
    if (!mobileNavigationOpen) return

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMobileNavigationOpen(false)
    }
    window.addEventListener("keydown", onKeyDown)
    return () => window.removeEventListener("keydown", onKeyDown)
  }, [mobileNavigationOpen])

  const navClass = (key: NavKey) =>
    key === activeNav
      ? "flex min-h-10 w-full items-center gap-3 rounded-md bg-[#172E50] px-3 py-2 text-left text-sm font-semibold text-white"
      : "flex min-h-10 w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm font-medium text-[#D9E4F2] hover:bg-white/5"

  const handleNavigate = (target: NavKey) => {
    setMobileNavigationOpen(false)
    onNavigate(target)
  }

  const navItem = (
    key: NavKey,
    label: string,
    icon?: React.ReactNode,
    previewIncrement?: string,
  ) => (
    <button
      type="button"
      className={navClass(key)}
      aria-current={activeNav === key ? "page" : undefined}
      onClick={() => handleNavigate(key)}
    >
      {icon ?? <span className="size-4" aria-hidden="true" />}
      <span>{label}</span>
      {previewIncrement ? <PreviewBadge increment={previewIncrement} /> : null}
    </button>
  )

  const previewItems = (items: PreviewNav[]) =>
    items.map((item) => (
      <div key={item.key}>
        {navItem(item.key, item.label, undefined, item.increment)}
      </div>
    ))

  const navigation = (
    <nav className="p-3" aria-label="Primary navigation">
      <div className="px-3 pb-2 pt-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
        Connectivity Needs
      </div>
      {navItem(
        "requirements",
        "My Connectivity Needs",
        <ClipboardList className="size-4" aria-hidden="true" />,
      )}

      <div className="px-3 pb-2 pt-5 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
        Connectivity Governance
      </div>
      {navItem("decisions", "Connectivity Decisions", undefined, "I16")}

      <div className="px-3 pb-2 pt-5 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
        Access Policy
      </div>
      {navItem(
        "compose",
        "Compose Connectivity",
        <PanelLeftClose className="size-4" aria-hidden="true" />,
      )}
      {navItem(
        "rules",
        "Access Rules",
        <ListTree className="size-4" aria-hidden="true" />,
      )}

      <div className="px-3 pb-2 pt-5 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
        Policy Views
      </div>
      {navItem(
        "effective",
        "Effective Policy",
        <Clock3 className="size-4" aria-hidden="true" />,
      )}
      {navItem(
        "normalized",
        "Normalized Policy",
        <TableProperties className="size-4" aria-hidden="true" />,
      )}

      <div className="px-3 pb-2 pt-5 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
        Technical Access
      </div>
      {previewItems(previewTechnicalAccess)}

      <div className="px-3 pb-2 pt-5 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
        Enforcement
      </div>
      {previewItems(previewEnforcement)}

      <div className="px-3 pb-2 pt-5 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
        Network Operations
      </div>
      {navItem("network-operations", "Network Operations", undefined, "I22")}

      <div className="px-3 pb-2 pt-5 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
        Product Operations
      </div>
      {navItem("explainability-audit", "Explainability & Audit", undefined, "I25")}
    </nav>
  )

  const brand = (
    <div className="flex h-16 items-center gap-3 border-b border-white/10 px-5">
      <div className="grid size-9 place-items-center rounded-md bg-[#2563EB]">
        <Network className="size-5" aria-hidden="true" />
      </div>
      <div>
        <div className="text-sm font-bold tracking-wide">NAPMS</div>
        <div className="text-xs text-[#8FA6C2]">Policy Management</div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-[#F5F7FA] md:grid md:grid-cols-[248px_minmax(0,1fr)]">
      <aside className="sticky top-0 hidden h-screen overflow-y-auto bg-[#0B1628] text-[#D9E4F2] md:block">
        {brand}
        {navigation}
      </aside>

      {mobileNavigationOpen ? (
        <div className="fixed inset-0 z-50 md:hidden">
          <button
            type="button"
            className="absolute inset-0 bg-black/40"
            aria-label="Close navigation"
            onClick={() => setMobileNavigationOpen(false)}
          />
          <aside
            role="dialog"
            aria-modal="true"
            aria-label="Primary navigation menu"
            className="relative h-full w-[min(320px,88vw)] overflow-y-auto bg-[#0B1628] text-[#D9E4F2] shadow-2xl"
          >
            {brand}
            {navigation}
          </aside>
        </div>
      ) : null}

      <div className="min-w-0">
        <header className="flex min-h-16 items-center justify-between gap-3 border-b border-[#E2E8F0] bg-white px-4 md:px-6">
          <Button
            variant="ghost"
            className="md:hidden"
            aria-label="Open navigation"
            onClick={() => setMobileNavigationOpen(true)}
          >
            <Menu className="size-5" aria-hidden="true" />
            Menu
          </Button>
          <div className="ml-auto flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <div className="text-sm font-semibold text-[#172033]">{actor.login}</div>
              <div className="text-xs text-[#5F6B7D]">{actor.actorId}</div>
            </div>
            <Button variant="ghost" onClick={() => void onLogout()}>
              <LogOut className="size-4" aria-hidden="true" />
              Logout
            </Button>
          </div>
        </header>
        <main className="p-4 md:p-6 lg:p-8">{children}</main>
      </div>
    </div>
  )
}
