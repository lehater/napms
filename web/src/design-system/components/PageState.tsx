import { Button } from "@/design-system/components/Button"

export function LoadingState({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-[var(--napms-table-body-min-height)] items-start p-8 text-sm text-[var(--napms-color-text-secondary)]">
      {children}
    </div>
  )
}

export function ErrorState({
  message,
  onRetry,
}: {
  message: string
  onRetry?: () => void
}) {
  return (
    <div className="min-h-[var(--napms-table-body-min-height)] p-8">
      <p className="text-sm text-[var(--napms-color-danger)]">{message}</p>
      {onRetry ? (
        <Button className="mt-3" variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  )
}

export function EmptyState({
  title,
  description,
}: {
  title: React.ReactNode
  description?: React.ReactNode
}) {
  return (
    <div className="flex min-h-[var(--napms-table-body-min-height)] flex-col items-center justify-center p-10 text-center">
      <div className="text-sm font-semibold text-[var(--napms-color-text-primary)]">{title}</div>
      {description ? (
        <p className="mt-1 text-sm text-[var(--napms-color-text-secondary)]">{description}</p>
      ) : null}
    </div>
  )
}
