import { useEffect, useState } from "react"

import { getSession, login, logout, type Actor } from "@/api"
import { AppShell } from "@/components/layout/AppShell"
import { LoginPage } from "@/features/auth/LoginPage"
import { ComposeConnectivityPage } from "@/features/proposals/ComposeConnectivityPage"

export function App() {
  const [actor, setActor] = useState<Actor | null>(null)
  const [bootstrapping, setBootstrapping] = useState(true)

  useEffect(() => {
    let active = true
    void getSession()
      .then((current) => {
        if (active) setActor(current)
      })
      .finally(() => {
        if (active) setBootstrapping(false)
      })
    return () => {
      active = false
    }
  }, [])

  if (bootstrapping) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#F5F7FA] text-sm text-[#64748B]">
        Loading NAPMS…
      </main>
    )
  }

  if (!actor) {
    return (
      <LoginPage
        onLogin={async (loginName, password) => {
          const authenticated = await login(loginName, password)
          setActor(authenticated)
        }}
      />
    )
  }

  return (
    <AppShell
      actor={actor}
      onLogout={async () => {
        await logout()
        setActor(null)
      }}
    >
      <ComposeConnectivityPage />
    </AppShell>
  )
}
