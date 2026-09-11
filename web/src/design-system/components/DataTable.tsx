export function DataTable({
  children,
  minWidth = 1180,
}: {
  children: React.ReactNode
  minWidth?: number
}) {
  return (
    <div className="min-h-[var(--napms-table-body-min-height)] overflow-x-auto">
      <table
        className="w-full table-fixed border-collapse text-left text-sm"
        style={{ minWidth }}
      >
        {children}
      </table>
    </div>
  )
}

export function DataTableHeader({ children }: { children: React.ReactNode }) {
  return (
    <thead className="bg-[var(--napms-color-surface-subtle)] text-[11px] font-bold uppercase tracking-[0.07em] text-[var(--napms-color-text-secondary)]">
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
}: {
  children?: React.ReactNode
  className?: string
}) {
  return <th className={`px-5 ${className}`}>{children}</th>
}

export function DataTableCell({
  children,
  className = "",
}: {
  children?: React.ReactNode
  className?: string
}) {
  return <td className={`px-5 py-3 align-middle ${className}`}>{children}</td>
}

export function DataTableSelectionCell({ children }: { children: React.ReactNode }) {
  return (
    <td className="w-[var(--napms-table-selection-column)] px-5 py-3 align-middle" onClick={(event) => event.stopPropagation()}>
      {children}
    </td>
  )
}

export function DataTableSelectionHead({ children }: { children: React.ReactNode }) {
  return (
    <th className="w-[var(--napms-table-selection-column)] px-5" onClick={(event) => event.stopPropagation()}>
      {children}
    </th>
  )
}
