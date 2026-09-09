import {
  ClipboardList,
  Clock3,
  Gavel,
  ListTree,
  LogOut,
  Network,
  TableProperties,
} from "lucide-react"

import type { Actor } from "@/api"
import { Button } from "@/components/ui/Button"

export type NavKey =
  | "connectivity"
  | "requirements"
  | "decisions"
  | "rules"
  | "effective"
  | "normalized"

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
      ? "flex w-full items-center gap-3 rounded-md bg-[#172E50] px-3 py-2.5 text-left text-sm font-semibold text-white"
      : "flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-left text-sm font-medium text-[#D9E4F2] hover:bg-white/5"

  return (
    <div className="min-h-screen bg-[#F5F7FA] md:grid md:grid-cols-[232px_1fr]">
      <aside className="hidden min-h-screen bg-[#0B1628] text-[#D9E4F2] md:flex md:flex-col">
        <div className="flex h-16 items-center gap-3 border-b border-white/10 px-5">
          <div className="grid size-9 place-items-center rounded-md bg-[#2563EB]">
            <Network className="size-5" aria-hidden="true" />
          </div>
          <div>
            <div className="text-sm font-bold tracking-wide">NAPMS</div>
            <div className="text-xs text-[#8FA6C2]">Policy Management</div>
          </div>
        </div>

        <nav className="flex-1 p-3" aria-label="Primary navigation">
          <div className="px-3 pb-2 pt-3 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
            Overview
          </div>
          <button
            type="button"
            className={navClass("connectivity")}
            aria-current={activeNav === "connectivity" ? "page" : undefined}
            onClick={() => onNavigate("connectivity")}
          >
            <Network className="size-4" aria-hidden="true" />
            Connectivity
          </button>
          <div className="px-3 pb-2 pt-6 text-[11px] font-semibold uppercase tracking-[0.16em] text-[#8FA6C2]">
            Policy
          </div>
          <button
            type="button"
            className={navClass("requirements")}
            aria-current={activeNav === "requirements" ? "page" : undefined}
            onClick={() => onNavigate("requirements")}
          >
            <ClipboardList className="size-4" aria-hidden="true" />
            Needs
          </button>
          <button
            type="button"
            className={navClass("decisions")}
            aria-current={activeNav === "decisions" ? "page" : undefined}
            onClick={() => onNavigate("decisions")}
          >
            <Gavel className="size-4" aria-hidden="true" />
            Decisions
          </button>
          <button
            type="button"
            className={navClass("rules")}
            aria-current={activeNav === "rules" ? "page" : undefined}
            onClick={() => onNavigate("rules")}
          >
            <ListTree className="size-4" aria-hidden="true" />
            Rules
          </button>
          <button
            type="button"
            className={navClass("effective")}
            aria-current={activeNav === "effective" ? "page" : undefined}
            onClick={() => onNavigate("effective")}
          >
            <Clock3 className="size-4" aria-hidden="true" />
            Effective
          </button>
          <button
            type="button"
            className={navClass("normalized")}
            aria-current={activeNav === "normalized" ? "page" : undefined}
            onClick={() => onNavigate("normalized")}
          >
            <TableProperties className="size-4" aria-hidden="true" />
            Export
          </button>
        </nav>
      </aside>

      <div className="min-w-0">
        <header className="flex min-h-16 items-center justify-between gap-3 border-b border-[#E2E8F0] bg-white px-4 md:px-6">
          <nav
            className="flex min-w-0 items-center gap-1 overflow-x-auto md:hidden"
            aria-label="Primary navigation"
          >
            {(
              [
                ["connectivity", "Connectivity"],
                ["requirements", "Needs"],
                ["decisions", "Decisions"],
                ["rules", "Rules"],
                ["effective", "Effective"],
                ["normalized", "Export"],
              ] as const
            ).map(([key, label]) => (
              <button
                key={key}
                type="button"
                className={
                  key === activeNav
                    ? "shrink-0 rounded-md bg-[#E8EEF8] px-2 py-1.5 text-xs font-semibold text-[#172033]"
                    : "shrink-0 rounded-md px-2 py-1.5 text-xs font-semibold text-[#64748B] hover:bg-[#F1F5F9]"
                }
                aria-current={key === activeNav ? "page" : undefined}
                onClick={() => onNavigate(key)}
              >
                {label}
              </button>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <div className="text-sm font-semibold text-[#172033]">
                {actor.login}
              </div>
              <div className="text-xs text-[#64748B]">{actor.actorId}</div>
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
