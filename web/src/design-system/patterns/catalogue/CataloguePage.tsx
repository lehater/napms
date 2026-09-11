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

export function CatalogueQuickFilters({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-12 flex-wrap items-center gap-3 border-b border-[var(--napms-color-border)] px-5 py-2.5">
      {children}
    </div>
  )
}

export function CataloguePagination({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-[62px] items-center justify-between border-t border-[var(--napms-color-border)] px-5 py-3.5">
      {children}
    </div>
  )
}
