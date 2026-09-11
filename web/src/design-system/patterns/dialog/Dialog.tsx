import type { ReactNode } from "react"
import { X } from "lucide-react"

import { Button } from "@/design-system/components/Button"

export function Dialog({
  open,
  labelledBy,
  busy = false,
  onClose,
  children,
  maxWidthClassName = "max-w-[500px]",
}: {
  open: boolean
  labelledBy: string
  busy?: boolean
  onClose: () => void
  children: ReactNode
  maxWidthClassName?: string
}) {
  if (!open) return null

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/30 p-4"
      role="presentation"
      onMouseDown={(event) => {
        if (event.currentTarget === event.target && !busy) onClose()
      }}
    >
      <div
        className={`w-full overflow-hidden rounded-xl border border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] shadow-2xl ${maxWidthClassName}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={labelledBy}
      >
        {children}
      </div>
    </div>
  )
}

export function DialogHeader({
  titleId,
  title,
  description,
  busy = false,
  onClose,
}: {
  titleId: string
  title: ReactNode
  description?: ReactNode
  busy?: boolean
  onClose: () => void
}) {
  return (
    <div className="flex min-h-[89px] items-start justify-between gap-4 border-b border-[var(--napms-color-border)] px-7 py-6">
      <div className="min-w-0">
        <h2
          id={titleId}
          className="text-lg font-semibold text-[var(--napms-color-text-primary)]"
        >
          {title}
        </h2>
        {description ? (
          <p className="mt-1 text-sm text-[var(--napms-color-text-secondary)]">
            {description}
          </p>
        ) : null}
      </div>
      <Button
        type="button"
        variant="ghost"
        size="sm"
        aria-label="Close dialog"
        disabled={busy}
        onClick={onClose}
      >
        <X className="size-4" aria-hidden="true" />
      </Button>
    </div>
  )
}

export function DialogBody({
  children,
  className = "",
}: {
  children: ReactNode
  className?: string
}) {
  return <div className={`px-7 py-6 ${className}`}>{children}</div>
}

export function DialogActions({ children }: { children: ReactNode }) {
  return (
    <div className="flex justify-end gap-2 border-t border-[var(--napms-color-border)] pt-5">
      {children}
    </div>
  )
}
