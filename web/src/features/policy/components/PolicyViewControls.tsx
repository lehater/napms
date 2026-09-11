import { useEffect, useState } from "react"

import { Button } from "@/design-system/components/Button"
import { Field, Input, Select } from "@/design-system/components/Field"
import { listPolicyViewScopes } from "@/features/policy/api"
import { ApiError } from "@/lib/api"
import { nowLocalDateTimeInput, toOffsetAwareIso } from "@/lib/datetime"

export function PolicyViewControls({
  onRun,
  running,
}: {
  onRun: (scope: string, asOf: string) => Promise<void>
  running: boolean
}) {
  const [scopes, setScopes] = useState<string[]>([])
  const [ambiguousScopes, setAmbiguousScopes] = useState<string[]>([])
  const [scope, setScope] = useState("")
  const [asOf, setAsOf] = useState(nowLocalDateTimeInput())
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    let active = true
    let instant: string
    try {
      instant = toOffsetAwareIso(asOf)
    } catch {
      setScopes([])
      setAmbiguousScopes([])
      setScope("")
      setLoading(false)
      return () => {
        active = false
      }
    }

    setLoading(true)
    setError(null)
    void listPolicyViewScopes(instant)
      .then((result) => {
        if (!active) return
        const values = result.scopes.map((item) => item.scope)
        setScopes(values)
        setAmbiguousScopes(result.ambiguousScopes.map((item) => item.scope))
        setScope((current) =>
          values.includes(current)
            ? current
            : values.length === 1
              ? values[0]
              : "",
        )
      })
      .catch((caught) => {
        if (!active) return
        setScopes([])
        setAmbiguousScopes([])
        setScope("")
        setError(
          caught instanceof ApiError
            ? caught
            : new ApiError(500, "InternalError", "Policy scopes could not be loaded."),
        )
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [asOf])

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setError(null)
    try {
      await onRun(scope, toOffsetAwareIso(asOf))
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught
          : new ApiError(422, "InvalidAsOf", "Select a valid date and time."),
      )
    }
  }

  return (
    <form onSubmit={submit} className="rounded-lg border border-[#E2E8F0] bg-white p-5 md:p-6">
      <div className="grid gap-4 lg:grid-cols-[minmax(220px,1fr)_minmax(260px,1fr)_auto] lg:items-end">
        <Field label="Governance scope">
          <Select value={scope} onChange={(event) => setScope(event.target.value)} disabled={loading} required>
            <option value="">{loading ? "Loading scopes…" : "Select scope"}</option>
            {scopes.map((value) => <option key={value} value={value}>{value}</option>)}
          </Select>
        </Field>
        <Field label="As of" hint="The browser time is converted to an explicit offset-aware instant.">
          <Input type="datetime-local" step="1" value={asOf} onChange={(event) => setAsOf(event.target.value)} required />
        </Field>
        <Button type="submit" loading={running} disabled={!scope || !asOf}>Run view</Button>
      </div>
      {ambiguousScopes.length > 0 ? <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900">{ambiguousScopes.length} scope(s) have ambiguous ReadEffectiveDesiredPolicy authority and remain fail-closed.</div> : null}
      {error ? <div role="alert" className="mt-4 rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-800"><div className="font-semibold">{error.code}</div><div className="mt-1">{error.message}</div>{error.correlationId ? <div className="mt-2 text-xs">Correlation: {error.correlationId}</div> : null}</div> : null}
    </form>
  )
}
