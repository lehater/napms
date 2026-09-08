import { LogOut, Network, PanelLeftClose } from "lucide-react"

import type { Actor } from "@/api"
import { Button } from "@/components/ui/Button"

export function AppShell({
  actor,
  onLogout,
  children,
}: {
  actor: Actor
  onLogout: () => Promise<void>
  children: React.ReactNode
}) {
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
            Access Policy
          </div>
          <div
            className="flex items-center gap-3 rounded-md bg-[#172E50] px-3 py-2.5 text-sm font-semibold text-white"
            aria-current="page"
          >
            <PanelLeftClose className="size-4" aria-hidden="true" />
            Compose Connectivity
          </div>
        </nav>
      </aside>

      <div className="min-w-0">
        <header className="flex h-16 items-center justify-between border-b border-[#E2E8F0] bg-white px-4 md:px-6">
          <div className="md:hidden text-sm font-bold text-[#172033]">NAPMS</div>
          <div className="ml-auto flex items-center gap-3">
            <div className="hidden text-right sm:block">
              <div className="text-sm font-semibold text-[#172033]">{actor.login}</div>
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
