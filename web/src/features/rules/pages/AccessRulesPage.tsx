import { useEffect, useState } from "react"
import { ChevronRight } from "lucide-react"

import { Button } from "@/design-system/components/Button"
import {
  DataTable,
  DataTableBody,
  DataTableCell,
  DataTableHeadCell,
  DataTableHeader,
  DataTableHeaderRow,
  DataTableRow,
} from "@/design-system/components/DataTable"
import { EmptyState, ErrorState, LoadingState } from "@/design-system/components/PageState"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { ListPagination } from "@/design-system/patterns/list/ListPage"
import { Surface } from "@/design-system/primitives/Surface"
import {
  CatalogueIdentity,
  shortId,
} from "@/features/catalogues/components/CatalogueIdentity"
import { listAccessRules } from "@/features/rules/api"
import { RuleOperationalStatus } from "@/features/rules/components/RuleStatus"
import type { RuleDto } from "@/features/rules/model/rule"
import { ApiError } from "@/lib/api"

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
        if (active) setError(caught instanceof ApiError ? caught : new ApiError(500, "InternalError", "Access Rules could not be loaded."))
      })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [page])

  return (
    <PageWorkspace>
      <PageHeader title="Access Rules" description="Authoritative Rules visible through your effective ReadAccessRule authority." />

      {ambiguousScopes.length > 0 ? (
        <div className="rounded-[var(--napms-control-radius)] border border-[var(--napms-color-warning-dot)] bg-[var(--napms-color-warning-bg)] p-4 text-sm text-[var(--napms-color-warning)]">
          <div className="font-semibold">Some scopes are fail-closed</div>
          <div className="mt-1">{ambiguousScopes.length} scope(s) have ambiguous read authority and are not included in this list.</div>
        </div>
      ) : null}

      {error ? <ErrorState message={`${error.code}: ${error.message}${error.correlationId ? ` · Correlation: ${error.correlationId}` : ""}`} /> : null}

      <Surface className="min-w-0 overflow-hidden">
        <div className="border-b border-[var(--napms-color-border)] px-5 py-4">
          <h2 className="text-base font-semibold text-[var(--napms-color-text-primary)]">Authorized Rules</h2>
          <p className="mt-1 text-xs text-[var(--napms-color-text-secondary)]">Page {page}</p>
        </div>

        {loading ? (
          <LoadingState>Loading Access Rules…</LoadingState>
        ) : rules.length === 0 ? (
          <EmptyState title="No visible Access Rules" description="No authoritative Rules are currently visible through your read authority." />
        ) : (
          <DataTable minWidth={920}>
            <DataTableHeader>
              <DataTableHeaderRow>
                <DataTableHeadCell>Rule ID</DataTableHeadCell>
                <DataTableHeadCell>Source</DataTableHeadCell>
                <DataTableHeadCell>Destination</DataTableHeadCell>
                <DataTableHeadCell>DCS revision</DataTableHeadCell>
                <DataTableHeadCell>Scope</DataTableHeadCell>
                <DataTableHeadCell>State</DataTableHeadCell>
                <DataTableHeadCell className="w-12" aria-label="Open" />
              </DataTableHeaderRow>
            </DataTableHeader>
            <DataTableBody>
              {rules.map((rule) => (
                <DataTableRow key={rule.ruleId}>
                  <DataTableCell className="font-mono text-xs text-[var(--napms-color-text-body)]">{shortId(rule.ruleId)}</DataTableCell>
                  <DataTableCell><CatalogueIdentity name={rule.catalogue?.sourceDisplayName} id={rule.semanticIdentity.sourceComponentDeploymentId} /></DataTableCell>
                  <DataTableCell><CatalogueIdentity name={rule.catalogue?.destinationDisplayName} id={rule.semanticIdentity.destinationComponentDeploymentId} /></DataTableCell>
                  <DataTableCell><CatalogueIdentity name={rule.catalogue?.dcsDisplayName} id={rule.semanticIdentity.dcsContractRevisionId} /></DataTableCell>
                  <DataTableCell>{rule.governanceScope}</DataTableCell>
                  <DataTableCell><RuleOperationalStatus state={rule.operationalState} /></DataTableCell>
                  <DataTableCell>
                    <button type="button" aria-label={`Open Rule ${rule.ruleId}`} className="grid size-8 place-items-center rounded-[var(--napms-control-radius)] text-[var(--napms-color-text-secondary)] hover:bg-[var(--napms-color-surface-muted)] hover:text-[var(--napms-color-text-primary)]" onClick={() => onOpenRule(rule.ruleId)}>
                      <ChevronRight className="size-4" aria-hidden="true" />
                    </button>
                  </DataTableCell>
                </DataTableRow>
              ))}
            </DataTableBody>
          </DataTable>
        )}

        <ListPagination>
          <span className="text-xs text-[var(--napms-color-text-secondary)]">Page {page}</span>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm" disabled={page === 1 || loading} onClick={() => onPageChange(Math.max(1, page - 1))}>Previous</Button>
            <Button variant="secondary" size="sm" disabled={!hasMore || loading} onClick={() => onPageChange(page + 1)}>Next</Button>
          </div>
        </ListPagination>
      </Surface>
    </PageWorkspace>
  )
}
