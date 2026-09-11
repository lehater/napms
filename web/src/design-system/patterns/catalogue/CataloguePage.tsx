import { PageHeader } from "@/design-system/layout/PageHeader"
import { PageWorkspace } from "@/design-system/layout/PageWorkspace"

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
  return <div className={`min-w-0 ${className}`}>{children}</div>
}

export function CatalogueToolbar({ children }: { children: React.ReactNode }) {
  return <div>{children}</div>
}

export function CatalogueFilterBar({ children }: { children: React.ReactNode }) {
  return <div className="mt-3 grid gap-3 xl:flex xl:items-end xl:gap-2.5">{children}</div>
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
      className={`grid gap-1 text-[10px] font-semibold leading-3 text-[var(--napms-color-text-body)] ${className}`}
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
    <div className="mt-3 flex min-h-8 flex-wrap items-center justify-between gap-2">
      <div className="flex flex-wrap items-center gap-2">{children}</div>
      {actions ? <div className="shrink-0">{actions}</div> : null}
    </div>
  )
}

export const CatalogueQuickFilters = CatalogueViewBar

export function CataloguePagination({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-14 flex-wrap items-center justify-between gap-3 px-0 py-3">
      {children}
    </div>
  )
}
