import { ArrowDown, ArrowUp } from "lucide-react"

export function DataTable({
  children,
  minWidth = 1180,
}: {
  children: React.ReactNode
  minWidth?: number
}) {
  return (
    <div className="mt-3 min-h-[var(--napms-table-body-min-height)] overflow-x-auto rounded-[var(--napms-surface-radius)] border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] shadow-[var(--napms-surface-shadow)]">
      <table
        className="w-full table-fixed border-collapse text-left text-[12px]"
        style={{ minWidth }}
      >
        {children}
      </table>
    </div>
  )
}

export function DataTableHeader({ children }: { children: React.ReactNode }) {
  return (
    <thead className="bg-[var(--napms-color-surface-subtle)] text-[10px] font-semibold text-[var(--napms-color-text-body)]">
      {children}
    </thead>
  )
}

export function DataTableBody({ children }: { children: React.ReactNode }) {
  return <tbody className="divide-y divide-[var(--napms-color-border)]">{children}</tbody>
}

export function DataTableHeaderRow({ children }: { children: React.ReactNode }) {
  return (
    <tr className="h-[var(--napms-table-header-height)] border-b border-[var(--napms-color-border)]">
      {children}
    </tr>
  )
}

export function DataTableRow({
  children,
  selected = false,
  onClick,
}: {
  children: React.ReactNode
  selected?: boolean
  onClick?: () => void
}) {
  return (
    <tr
      className={`h-[var(--napms-table-row-height)] bg-[var(--napms-color-surface)] transition ${
        onClick ? "cursor-pointer" : ""
      } ${
        selected
          ? "bg-[var(--napms-color-primary-subtle)]"
          : "hover:bg-[var(--napms-color-surface-subtle)]"
      }`}
      onClick={onClick}
    >
      {children}
    </tr>
  )
}

export function DataTableHeadCell({
  children,
  className = "",
  onSort,
  sortDirection = null,
  ariaLabel,
}: {
  children?: React.ReactNode
  className?: string
  onSort?: () => void
  sortDirection?: "asc" | "desc" | null
  ariaLabel?: string
}) {
  return (
    <th className={`px-[var(--napms-table-cell-x)] ${className}`}>
      {onSort ? (
        <button
          type="button"
          className="group inline-flex min-h-7 items-center gap-1 rounded px-1 text-left hover:bg-[var(--napms-color-surface-muted)] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--napms-color-primary-border)]"
          onClick={onSort}
          aria-label={ariaLabel}
          aria-sort={sortDirection === "asc" ? "ascending" : sortDirection === "desc" ? "descending" : "none"}
        >
          <span>{children}</span>
          {sortDirection === "asc" ? (
            <ArrowUp className="size-3" aria-hidden="true" />
          ) : sortDirection === "desc" ? (
            <ArrowDown className="size-3" aria-hidden="true" />
          ) : (
            <span className="w-3 opacity-0 transition-opacity group-hover:opacity-40" aria-hidden="true">↕</span>
          )}
        </button>
      ) : (
        children
      )}
    </th>
  )
}

export function DataTableCell({
  children,
  className = "",
}: {
  children?: React.ReactNode
  className?: string
}) {
  return (
    <td
      className={`px-[var(--napms-table-cell-x)] py-[var(--napms-table-cell-y)] align-middle ${className}`}
    >
      {children}
    </td>
  )
}

export function DataTableSelectionCell({ children }: { children: React.ReactNode }) {
  return (
    <td
      className="w-[var(--napms-table-selection-column)] px-[var(--napms-table-cell-x)] py-[var(--napms-table-cell-y)] align-middle"
      onClick={(event) => event.stopPropagation()}
    >
      {children}
    </td>
  )
}

export function DataTableSelectionHead({ children }: { children: React.ReactNode }) {
  return (
    <th
      className="w-[var(--napms-table-selection-column)] px-[var(--napms-table-cell-x)]"
      onClick={(event) => event.stopPropagation()}
    >
      {children}
    </th>
  )
}
