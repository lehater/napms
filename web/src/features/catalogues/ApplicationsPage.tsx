import { useEffect, useState } from "react"
import { ChevronRight, Plus, Search } from "lucide-react"

import { ApiError } from "@/lib/api"
import { CatalogueIdentity } from "@/features/catalogues/components/CatalogueIdentity"
import { Button } from "@/components/ui/Button"
import {
  createCatalogueApplication,
  listCatalogueApplications,
  type ApplicationDto,
} from "@/features/catalogues/catalogueApi"

const inputClass =
  "min-h-10 w-full rounded-md border border-[#CBD5E1] bg-white px-3 py-2 text-sm text-[#172033] outline-none focus:border-[#2563EB] focus:ring-2 focus:ring-[#DBEAFE]"

function errorFrom(caught: unknown, fallback: string) {
  return caught instanceof ApiError
    ? caught
    : new ApiError(500, "InternalError", fallback)
}

export function ApplicationsPage({
  page,
  onPageChange,
  onOpenApplication,
}: {
  page: number
  onPageChange: (page: number) => void
  onOpenApplication: (applicationId: string) => void
}) {
  const [items, setItems] = useState<ApplicationDto[]>([])
  const [hasMore, setHasMore] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<ApiError | null>(null)
  const [searchInput, setSearchInput] = useState("")
  const [search, setSearch] = useState("")
  const [displayName, setDisplayName] = useState("")
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState<ApiError | null>(null)

  async function load() {
    setLoading(true)
    setError(null)
    try {
      const result = await listCatalogueApplications(page, search)
      setItems(result.items)
      setHasMore(result.hasMore)
    } catch (caught) {
      setError(errorFrom(caught, "Applications could not be loaded."))
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [page, search])

  async function create(event: React.FormEvent) {
    event.preventDefault()
    const name = displayName.trim()
    if (!name) return
    setCreating(true)
    setCreateError(null)
    try {
      const created = await createCatalogueApplication(name)
      setDisplayName("")
      onOpenApplication(created.applicationId)
    } catch (caught) {
      setCreateError(errorFrom(caught, "Application could not be created."))
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-6">
      <header>
        <div className="text-xs font-semibold uppercase tracking-[0.16em] text-[#64748B]">
          Catalogues
        </div>
        <h1 className="mt-1 text-2xl font-bold text-[#172033]">Applications</h1>
        <p className="mt-2 max-w-3xl text-sm text-[#64748B]">
          Maintain the Application Communication Catalogue structure used by Connectivity.
        </p>
      </header>

      <section className="rounded-lg border border-[#E2E8F0] bg-white p-5 shadow-sm">
        <div className="mb-4 flex items-center gap-2">
          <Plus className="size-4 text-[#2563EB]" aria-hidden="true" />
          <h2 className="font-semibold text-[#172033]">Add application</h2>
        </div>
        <form className="flex flex-col gap-3 sm:flex-row" onSubmit={create}>
          <input
            className={inputClass}
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
            placeholder="Application name"
            maxLength={256}
            aria-label="Application name"
          />
          <Button type="submit" loading={creating} disabled={!displayName.trim()}>
            Create
          </Button>
        </form>
        {createError ? (
          <p className="mt-3 text-sm text-red-700">{createError.message}</p>
        ) : null}
      </section>

      <section className="overflow-hidden rounded-lg border border-[#E2E8F0] bg-white shadow-sm">
        <div className="flex flex-col gap-3 border-b border-[#E2E8F0] p-4 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="font-semibold text-[#172033]">Application catalogue</h2>
          <form
            className="flex min-w-0 gap-2 sm:w-80"
            onSubmit={(event) => {
              event.preventDefault()
              if (page !== 1) onPageChange(1)
              setSearch(searchInput.trim())
            }}
          >
            <input
              className={inputClass}
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search applications"
              aria-label="Search applications"
            />
            <Button type="submit" variant="secondary" aria-label="Search">
              <Search className="size-4" aria-hidden="true" />
            </Button>
          </form>
        </div>

        {loading ? (
          <div className="p-6 text-sm text-[#64748B]">Loading applications…</div>
        ) : error ? (
          <div className="p-6">
            <p className="text-sm text-red-700">{error.message}</p>
            <Button className="mt-3" variant="secondary" onClick={() => void load()}>
              Retry
            </Button>
          </div>
        ) : items.length === 0 ? (
          <div className="p-6 text-sm text-[#64748B]">
            No applications match the current view.
          </div>
        ) : (
          <div className="divide-y divide-[#E2E8F0]">
            {items.map((item) => (
              <button
                key={item.applicationId}
                type="button"
                className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left hover:bg-[#F8FAFC]"
                onClick={() => onOpenApplication(item.applicationId)}
              >
                <CatalogueIdentity name={item.displayName} id={item.applicationId} />
                <div className="flex items-center gap-3">
                  <span className="rounded-full border border-green-200 bg-green-50 px-2 py-0.5 text-xs font-semibold text-green-800">
                    {item.lifecycle}
                  </span>
                  <ChevronRight className="size-4 text-[#94A3B8]" aria-hidden="true" />
                </div>
              </button>
            ))}
          </div>
        )}

        <div className="flex items-center justify-between border-t border-[#E2E8F0] px-4 py-3">
          <Button
            variant="secondary"
            disabled={page <= 1 || loading}
            onClick={() => onPageChange(page - 1)}
          >
            Previous
          </Button>
          <span className="text-xs font-medium text-[#64748B]">Page {page}</span>
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
