import { useEffect, useState } from "react"
import { ChevronRight, CircleAlert } from "lucide-react"

import { ApiError, listAccessRules, type RuleDto } from "@/api"
import { Button } from "@/components/ui/Button"
import { StatusBadge } from "@/components/ui/StatusBadge"

function shortId(value: string) {
  return value.length <= 18 ? value : `${value.slice(0, 8)}…${value.slice(-6)}`
}

export function AccessRulesPage({
  page,
  onPageChange,
  onOpenRule,
}: {
  page: number
  onPageChange: (page: number) => void
  onOpenRule: (ruleId: string) => void
}) {
  const [rules, setRules] = useState<RuleDto[]>([])
  const [hasMore, setHasMore] = useState(false)
  const [ambiguousScopes, setAmbiguousScopes] = useState<string[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)

  useEffect(() => {
    let active = true
    setLoading(true)
    setError(null)

    void listAccessRules(page)
      .then((result) => {
        if (!active) return
        setRules(result.items)
        setHasMore(result.hasMore)
        setAmbiguousScopes(result.ambiguousScopes.map((item) => item.scope))
      })
      .catch((caught) => {
        if (!active) return
        setError(
          caught instanceof ApiError
            ? caught
            : new ApiError(500, "InternalError", "Access Rules could not be loaded."),
        )
      })
      .finally(() => {
        if (active) setLoading(false)
      })

    return () => {
      active = false
    }
  }, [page])

  return (
    <div className="mx-auto max-w-[1280px]">
      <header className="mb-6">
        <div className="mb-1 text-xs font-semibold uppercase tracking-[0.14em] text-[#64748B]">
          Access Policy
        </div>
        <h1 className="text-[28px] font-bold tracking-tight text-[#172033]">
          Access Rules
        </h1>
        <p className="mt-2 max-w-3xl text-sm text-[#64748B]">
          Authoritative Rules visible through your effective ReadAccessRule authority.
        </p>
      </header>

      {ambiguousScopes.length > 0 ? (
        <div className="mb-4 rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <div className="font-semibold">Some scopes are fail-closed</div>
          <div className="mt-1">
            {ambiguousScopes.length} scope(s) have ambiguous read authority and are not
            included in this list.
          </div>
        </div>
      ) : null}

      {error ? (
        <div
          role="alert"
          className="mb-4 rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-800"
        >
          <div className="flex gap-3">
            <CircleAlert className="mt-0.5 size-4 shrink-0" aria-hidden="true" />
            <div>
              <div className="font-semibold">{error.code}</div>
              <div className="mt-1">{error.message}</div>
              {error.correlationId ? (
                <div className="mt-2 text-xs">Correlation: {error.correlationId}</div>
              ) : null}
            </div>
          </div>
        </div>
      ) : null}

      <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white">
        <div className="flex items-center justify-between border-b border-[#E2E8F0] px-5 py-4">
          <div>
            <h2 className="text-base font-semibold text-[#172033]">Authorized Rules</h2>
            <p className="mt-1 text-xs text-[#64748B]">Page {page}</p>
          </div>
        </div>

        {loading ? (
          <div className="p-8 text-sm text-[#64748B]">Loading Access Rules…</div>
        ) : rules.length === 0 ? (
          <div className="p-10 text-center">
            <div className="text-sm font-semibold text-[#334155]">
              No visible Access Rules
            </div>
            <div className="mt-2 text-sm text-[#64748B]">
              No authoritative Rules are currently visible through your read authority.
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[920px] border-collapse text-left text-sm">
              <thead className="bg-[#F8FAFC] text-xs uppercase tracking-wide text-[#64748B]">
                <tr>
                  <th className="px-5 py-3 font-semibold">Rule ID</th>
                  <th className="px-5 py-3 font-semibold">Source</th>
                  <th className="px-5 py-3 font-semibold">Destination</th>
                  <th className="px-5 py-3 font-semibold">DCS revision</th>
                  <th className="px-5 py-3 font-semibold">Scope</th>
                  <th className="px-5 py-3 font-semibold">State</th>
                  <th className="w-12 px-5 py-3" aria-label="Open" />
                </tr>
              </thead>
              <tbody>
                {rules.map((rule) => (
                  <tr
                    key={rule.ruleId}
                    className="border-t border-[#E2E8F0] hover:bg-[#F8FAFC]"
                  >
                    <td className="px-5 py-3 font-mono text-xs text-[#334155]">
                      {shortId(rule.ruleId)}
                    </td>
                    <td className="px-5 py-3 font-mono text-xs">
                      {shortId(rule.semanticIdentity.sourceComponentDeploymentId)}
                    </td>
                    <td className="px-5 py-3 font-mono text-xs">
                      {shortId(rule.semanticIdentity.destinationComponentDeploymentId)}
                    </td>
                    <td className="px-5 py-3 font-mono text-xs">
                      {shortId(rule.semanticIdentity.dcsContractRevisionId)}
                    </td>
                    <td className="px-5 py-3">{rule.governanceScope}</td>
                    <td className="px-5 py-3">
                      <StatusBadge value={rule.operationalState} />
                    </td>
                    <td className="px-5 py-3">
                      <button
                        type="button"
                        aria-label={`Open Rule ${rule.ruleId}`}
                        className="grid size-8 place-items-center rounded-md text-[#64748B] hover:bg-[#E2E8F0] hover:text-[#172033]"
                        onClick={() => onOpenRule(rule.ruleId)}
                      >
                        <ChevronRight className="size-4" aria-hidden="true" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="flex items-center justify-end gap-2 border-t border-[#E2E8F0] px-5 py-4">
          <Button
            variant="secondary"
            disabled={page === 1 || loading}
            onClick={() => onPageChange(Math.max(1, page - 1))}
          >
            Previous
          </Button>
          <Button
            variant="secondary"
            disabled={!hasMore || loading}
            onClick={() => onPageChange(page + 1)}
          >
            Next
          </Button>
        </div>
      </section>
    </div>
  )
}
