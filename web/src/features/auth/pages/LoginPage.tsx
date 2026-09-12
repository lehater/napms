import { useState } from "react"
import { Network } from "lucide-react"

import { Alert } from "@/design-system/components/Alert"
import { Button } from "@/design-system/components/Button"
import { Field, Input } from "@/design-system/components/Field"
import { ApiError } from "@/lib/api"

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
    <main className="grid min-h-screen place-items-center bg-[var(--napms-color-app-bg)] p-4">
      <form
        onSubmit={submit}
        className="w-full max-w-[var(--napms-auth-card-width)] rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] p-7 shadow-[var(--napms-surface-shadow)]"
      >
        <div className="mb-7 flex items-center gap-3">
          <div className="grid size-10 place-items-center rounded-[var(--napms-control-radius)] bg-[var(--napms-color-nav-bg)] text-[var(--napms-color-code-text)]">
            <Network className="size-5" aria-hidden="true" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-[var(--napms-color-text-primary)]">Sign in to NAPMS</h1>
            <p className="text-sm text-[var(--napms-color-text-secondary)]">Local development access</p>
          </div>
        </div>

        <div className="grid gap-4">
          <Field label="Login">
            <Input
              autoComplete="username"
              value={login}
              onChange={(event) => setLogin(event.target.value)}
              required
            />
          </Field>
          <Field label="Password">
            <Input
              autoComplete="current-password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </Field>

          {error ? <Alert role="alert" tone="danger">{error}</Alert> : null}

          <Button type="submit" loading={submitting}>
            Sign in
          </Button>
        </div>
      </form>
    </main>
  )
}
