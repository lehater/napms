import {
  Activity,
  Boxes,
  ClipboardList,
  Clock3,
  Gavel,
  ListTree,
  LogOut,
  Network,
  Search,
  Server,
  TableProperties,
} from "lucide-react"

import { Button } from "@/components/ui/Button"
import type { Actor } from "@/features/auth/model/actor"

export type NavKey =
  | "connectivity"
  | "checker"
  | "applications"
  | "resources"
  | "requirements"
  | "decisions"
  | "rules"
  | "effective"
  | "normalized"
  | "realization"

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
  const navClass = (key: NavKey) =>
    key === activeNav
      ? "flex w-full items-center gap-3 rounded-[var(--napms-control-radius)] bg-[var(--napms-color-nav-active)] px-3 py-2.5 text-left text-sm font-semibold text-white"
      : "flex w-full items-center gap-3 rounded-[var(--napms-control-radius)] px-3 py-2.5 text-left text-sm font-medium text-[var(--napms-color-nav-text)] hover:bg-white/5"

  const navHeadingClass =
    "px-3 pb-2 pt-6 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--napms-color-nav-muted)]"

  return (
    <div className="min-h-screen bg-[var(--napms-color-app-bg)] md:grid md:grid-cols-[var(--napms-sidebar-width)_minmax(0,1fr)]">
      <aside className="hidden min-h-screen bg-[var(--napms-color-nav-bg)] text-[var(--napms-color-nav-text)] md:flex md:flex-col">
        <div className="flex h-16 items-center gap-3 border-b border-[var(--napms-color-nav-divider)] px-5">
          <div className="grid size-9 place-items-center rounded-[var(--napms-control-radius)] bg-[var(--napms-color-primary)]">
            <Network className="size-5" aria-hidden="true" />
          </div>
          <div>
            <div className="text-sm font-bold tracking-wide">NAPMS</div>
            <div className="text-xs text-[var(--napms-color-nav-muted)]">Policy Management</div>
          </div>
        </div>

        <nav className="flex-1 p-3" aria-label="Primary navigation">
          <div className="px-3 pb-2 pt-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--napms-color-nav-muted)]">
            Overview
          </div>
          <button type="button" className={navClass("connectivity")} aria-current={activeNav === "connectivity" ? "page" : undefined} onClick={() => onNavigate("connectivity")}>
            <Network className="size-4" aria-hidden="true" />
            Connectivity
          </button>
          <button type="button" className={navClass("checker")} aria-current={activeNav === "checker" ? "page" : undefined} onClick={() => onNavigate("checker")}>
            <Search className="size-4" aria-hidden="true" />
            Checker
          </button>

          <div className={navHeadingClass}>Catalogues</div>
          <button type="button" className={navClass("applications")} aria-current={activeNav === "applications" ? "page" : undefined} onClick={() => onNavigate("applications")}>
            <Boxes className="size-4" aria-hidden="true" />
            Applications
          </button>
          <button type="button" className={navClass("resources")} aria-current={activeNav === "resources" ? "page" : undefined} onClick={() => onNavigate("resources")}>
            <Server className="size-4" aria-hidden="true" />
            Resources
          </button>

          <div className={navHeadingClass}>Policy</div>
          <button type="button" className={navClass("requirements")} aria-current={activeNav === "requirements" ? "page" : undefined} onClick={() => onNavigate("requirements")}>
            <ClipboardList className="size-4" aria-hidden="true" />
            Needs
          </button>
          <button type="button" className={navClass("decisions")} aria-current={activeNav === "decisions" ? "page" : undefined} onClick={() => onNavigate("decisions")}>
            <Gavel className="size-4" aria-hidden="true" />
            Decisions
          </button>
          <button type="button" className={navClass("rules")} aria-current={activeNav === "rules" ? "page" : undefined} onClick={() => onNavigate("rules")}>
            <ListTree className="size-4" aria-hidden="true" />
            Rules
          </button>
          <button type="button" className={navClass("effective")} aria-current={activeNav === "effective" ? "page" : undefined} onClick={() => onNavigate("effective")}>
            <Clock3 className="size-4" aria-hidden="true" />
            Effective
          </button>
          <button type="button" className={navClass("normalized")} aria-current={activeNav === "normalized" ? "page" : undefined} onClick={() => onNavigate("normalized")}>
            <TableProperties className="size-4" aria-hidden="true" />
            Export
          </button>

          <div className={navHeadingClass}>Operations</div>
          <button type="button" className={navClass("realization")} aria-current={activeNav === "realization" ? "page" : undefined} onClick={() => onNavigate("realization")}>
            <Activity className="size-4" aria-hidden="true" />
            Realization
          </button>
        </nav>

        <div className="border-t border-[var(--napms-color-nav-divider)] p-3">
          <div className="flex items-center gap-3 rounded-[var(--napms-control-radius)] px-3 py-2.5">
            <div className="grid size-8 shrink-0 place-items-center rounded-full bg-white/10 text-xs font-bold text-white">
              {actor.login.slice(0, 1).toUpperCase()}
            </div>
            <div className="min-w-0 flex-1">
              <div className="truncate text-sm font-semibold text-white">{actor.login}</div>
              <div className="truncate text-xs text-[var(--napms-color-nav-muted)]">{actor.actorId}</div>
            </div>
            <button
              type="button"
              className="rounded-[var(--napms-control-radius)] p-2 text-[var(--napms-color-nav-muted)] hover:bg-white/5 hover:text-white"
              onClick={() => void onLogout()}
              aria-label="Logout"
            >
              <LogOut className="size-4" aria-hidden="true" />
            </button>
          </div>
        </div>
      </aside>

      <div className="min-w-0">
        <header className="flex min-h-16 items-center justify-between gap-3 border-b border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] px-4 md:hidden">
          <nav className="flex min-w-0 items-center gap-1 overflow-x-auto" aria-label="Primary navigation">
            {(
              [
                ["connectivity", "Connectivity"],
                ["checker", "Checker"],
                ["applications", "Applications"],
                ["resources", "Resources"],
                ["requirements", "Needs"],
                ["decisions", "Decisions"],
                ["rules", "Rules"],
                ["effective", "Effective"],
                ["normalized", "Export"],
                ["realization", "Realization"],
              ] as const
            ).map(([key, label]) => (
              <button
                key={key}
                type="button"
                className={
                  key === activeNav
                    ? "shrink-0 rounded-[var(--napms-control-radius)] bg-[var(--napms-color-primary-subtle)] px-2 py-1.5 text-xs font-semibold text-[var(--napms-color-text-primary)]"
                    : "shrink-0 rounded-[var(--napms-control-radius)] px-2 py-1.5 text-xs font-semibold text-[var(--napms-color-text-secondary)] hover:bg-[var(--napms-color-surface-muted)]"
                }
                aria-current={key === activeNav ? "page" : undefined}
                onClick={() => onNavigate(key)}
              >
                {label}
              </button>
            ))}
          </nav>
          <Button variant="ghost" size="sm" onClick={() => void onLogout()}>
            <LogOut className="size-4" aria-hidden="true" />
            Logout
          </Button>
        </header>
        <main className="p-4 md:p-6">{children}</main>
      </div>
    </div>
  )
}
