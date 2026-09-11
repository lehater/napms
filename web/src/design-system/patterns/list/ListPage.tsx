import { ChevronLeft, ChevronRight } from "lucide-react"

import { Select } from "@/design-system/components/Field"
import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"

export function ListPage({
  title,
  description,
  actions,
  children,
}: {
  title: React.ReactNode
  description?: React.ReactNode
  actions?: React.ReactNode
  children: React.ReactNode
}) {
  return (
    <PageWorkspace>
      <PageHeader title={title} description={description} actions={actions} />
      {children}
    </PageWorkspace>
  )
}

export function ListSurface({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`min-w-0 ${className}`}>{children}</div>
}

export function ListToolbar({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>
}

export function ListFilterBar({ children }: { children: React.ReactNode }) {
  return <div className="mt-3 grid gap-3 xl:flex xl:items-end xl:gap-2.5">{children}</div>
}

export function ListFilterField({ label, className = "", children }: { label: React.ReactNode; className?: string; children: React.ReactNode }) {
  return <label className={`grid gap-1 text-[10px] font-semibold leading-3 text-[var(--napms-color-text-body)] ${className}`}>{label}{children}</label>
}

export function ListViewBar({ children, actions }: { children: React.ReactNode; actions?: React.ReactNode }) {
  return <div className="mt-3 flex min-h-8 flex-wrap items-center justify-between gap-2"><div className="flex flex-wrap items-center gap-2">{children}</div>{actions ? <div className="shrink-0">{actions}</div> : null}</div>
}

export function ListPagination({ children }: { children: React.ReactNode }) {
  return <div className="flex min-h-14 flex-wrap items-center justify-between gap-3 px-0 py-3">{children}</div>
}

function pageSlots(page: number, pageCount: number): Array<number | "ellipsis-left" | "ellipsis-right"> {
  if (pageCount <= 7) return Array.from({ length: pageCount }, (_, index) => index + 1)
  if (page <= 3) return [1, 2, 3, 4, 5, "ellipsis-right", pageCount]
  if (page >= pageCount - 2) return [1, "ellipsis-left", pageCount - 4, pageCount - 3, pageCount - 2, pageCount - 1, pageCount]
  return [1, "ellipsis-left", page - 1, page, page + 1, "ellipsis-right", pageCount]
}

export function ListPaginationControls({ page, pageSize, total, onPageChange, onPageSizeChange, pageSizeOptions = [25, 50, 100], disabled = false }: { page: number; pageSize: number; total: number; onPageChange: (page: number) => void; onPageSizeChange: (pageSize: number) => void; pageSizeOptions?: number[]; disabled?: boolean }) {
  const pageCount = Math.max(1, Math.ceil(total / pageSize))
  const safePage = Math.min(Math.max(page, 1), pageCount)
  const from = total === 0 ? 0 : (safePage - 1) * pageSize + 1
  const to = total === 0 ? 0 : Math.min(safePage * pageSize, total)
  return (
    <div className="grid min-h-14 grid-cols-1 items-center gap-3 py-3 text-[11px] text-[var(--napms-color-text-secondary)] lg:grid-cols-[1fr_auto_1fr]">
      <div>Showing {from.toLocaleString()}–{to.toLocaleString()} of {total.toLocaleString()}</div>
      <div className="flex items-center justify-center gap-1" aria-label="Pagination">
        <button type="button" className="grid size-7 place-items-center rounded-[var(--napms-control-radius)] hover:bg-[var(--napms-color-surface-muted)] disabled:opacity-40" disabled={disabled || safePage <= 1} onClick={() => onPageChange(safePage - 1)} aria-label="Previous page"><ChevronLeft className="size-3.5" aria-hidden="true" /></button>
        {pageSlots(safePage, pageCount).map((slot) => typeof slot === "number" ? (
          <button key={slot} type="button" className={slot === safePage ? "grid size-7 place-items-center rounded-[var(--napms-control-radius)] border border-[var(--napms-color-primary-border)] bg-[var(--napms-color-primary-subtle)] font-semibold text-[var(--napms-color-primary-hover)]" : "grid size-7 place-items-center rounded-[var(--napms-control-radius)] hover:bg-[var(--napms-color-surface-muted)]"} disabled={disabled} onClick={() => onPageChange(slot)} aria-current={slot === safePage ? "page" : undefined}>{slot}</button>
        ) : <span key={slot} className="grid size-7 place-items-center" aria-hidden="true">…</span>)}
        <button type="button" className="grid size-7 place-items-center rounded-[var(--napms-control-radius)] hover:bg-[var(--napms-color-surface-muted)] disabled:opacity-40" disabled={disabled || safePage >= pageCount} onClick={() => onPageChange(safePage + 1)} aria-label="Next page"><ChevronRight className="size-3.5" aria-hidden="true" /></button>
      </div>
      <label className="flex items-center justify-start gap-2 lg:justify-end"><span>Rows per page</span><Select className="w-[76px]" value={String(pageSize)} disabled={disabled} onChange={(event) => onPageSizeChange(Number(event.target.value))} aria-label="Rows per page">{pageSizeOptions.map((option) => <option key={option} value={option}>{option}</option>)}</Select></label>
    </div>
  )
}
