import type { ReactNode } from "react"

import { Surface } from "@/design-system/primitives/Surface"

export function DetailSection({
  title,
  actions,
  children,
  className = "",
}: {
  title?: ReactNode
  actions?: ReactNode
  children: ReactNode
  className?: string
}) {
  return (
    <Surface className={`overflow-hidden ${className}`}>
      {title || actions ? (
        <div className="flex min-h-11 items-center justify-between gap-3 border-b border-[var(--napms-color-border)] px-4 py-3">
          {title ? (
            <h2 className="text-sm font-semibold text-[var(--napms-color-text-primary)]">
              {title}
            </h2>
          ) : <span />}
          {actions ? <div className="shrink-0">{actions}</div> : null}
        </div>
      ) : null}
      <div className="p-4">{children}</div>
    </Surface>
  )
}

export function DetailRow({
  label,
  children,
  labelWidthClassName = "grid-cols-[130px_minmax(0,1fr)]",
}: {
  label: ReactNode
  children: ReactNode
  labelWidthClassName?: string
}) {
  return (
    <div className={`grid gap-3 py-1.5 text-sm ${labelWidthClassName}`}>
      <div className="text-[var(--napms-color-text-secondary)]">{label}</div>
      <div className="min-w-0 text-[var(--napms-color-text-body)]">{children}</div>
    </div>
  )
}

export function DetailStack({
  children,
  className = "",
}: {
  children: ReactNode
  className?: string
}) {
  return <div className={`grid gap-4 ${className}`}>{children}</div>
}
