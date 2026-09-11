import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"
import { Surface } from "@/design-system/primitives/Surface"

export function CataloguePage({
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

export function CatalogueSurface({
  children,
  className = "",
}: {
  children: React.ReactNode
  className?: string
}) {
  return <Surface className={`overflow-hidden ${className}`}>{children}</Surface>
}

export function CatalogueToolbar({ children }: { children: React.ReactNode }) {
  return (
    <div className="border-b border-[var(--napms-color-border)] p-5">
      {children}
    </div>
  )
}

export function CatalogueFilterBar({ children }: { children: React.ReactNode }) {
  return <div className="mt-5 grid gap-3 xl:flex xl:items-end xl:gap-5">{children}</div>
}

export function CatalogueFilterField({
  label,
  className = "",
  children,
}: {
  label: React.ReactNode
  className?: string
  children: React.ReactNode
}) {
  return (
    <label
      className={`grid gap-2 text-[11px] font-bold uppercase tracking-[0.07em] text-[var(--napms-color-text-secondary)] ${className}`}
    >
      {label}
      {children}
    </label>
  )
}

export function CatalogueViewBar({
  children,
  actions,
}: {
  children: React.ReactNode
  actions?: React.ReactNode
}) {
  return (
    <div className="flex min-h-12 flex-wrap items-center justify-between gap-3 border-b border-[var(--napms-color-border)] px-5 py-2.5">
      <div className="flex flex-wrap items-center gap-3">{children}</div>
      {actions ? <div className="shrink-0">{actions}</div> : null}
    </div>
  )
}

export const CatalogueQuickFilters = CatalogueViewBar

export function CataloguePagination({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-[62px] flex-wrap items-center justify-between gap-3 border-t border-[var(--napms-color-border)] px-5 py-3.5">
      {children}
    </div>
  )
}
