import { useState } from "react"
import { Network } from "lucide-react"

import { ApiError } from "@/lib/api"
import { Button } from "@/components/ui/Button"

export function LoginPage({
  onLogin,
}: {
  onLogin: (login: string, password: string) => Promise<void>
}) {
  const [login, setLogin] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setSubmitting(true)
    setError(null)
    try {
      await onLogin(login, password)
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Authentication could not be completed.",
      )
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-[#F5F7FA] p-4">
      <form
        onSubmit={submit}
        className="w-full max-w-[420px] rounded-lg border border-[#E2E8F0] bg-white p-7 shadow-sm"
      >
        <div className="mb-7 flex items-center gap-3">
          <div className="grid size-10 place-items-center rounded-md bg-[#0B1628] text-white">
            <Network className="size-5" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[#172033]">Sign in to NAPMS</h1>
            <p className="text-sm text-[#64748B]">Local development access</p>
          </div>
        </div>

        <div className="grid gap-4">
          <label className="grid gap-2 text-sm font-medium text-[#334155]">
            Login
            <input
              autoComplete="username"
              value={login}
              onChange={(event) => setLogin(event.target.value)}
              className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2"
              required
            />
          </label>
          <label className="grid gap-2 text-sm font-medium text-[#334155]">
            Password
            <input
              autoComplete="current-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="min-h-10 rounded-md border border-[#CBD5E1] px-3 py-2"
              required
            />
          </label>

          {error ? (
            <div role="alert" className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
              {error}
            </div>
          ) : null}

          <Button type="submit" loading={submitting}>
            Sign in
          </Button>
        </div>
      </form>
    </main>
  )
}
