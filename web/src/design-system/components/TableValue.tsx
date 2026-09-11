import type { ButtonHTMLAttributes } from "react"

export function PrimaryTableAction({
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      type="button"
      className={`font-semibold text-[var(--napms-color-primary)] hover:underline ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}

export function ReferenceText({ children }: { children: React.ReactNode }) {
  return (
    <span className="font-mono text-xs text-[var(--napms-color-text-secondary)]">
      {children}
    </span>
  )
}

export function EmptyValue() {
  return <span className="text-[var(--napms-color-text-muted)]">—</span>
}

export function TechnicalValueList({
  values,
  maxVisible = 2,
}: {
  values: string[]
  maxVisible?: number
}) {
  if (values.length === 0) return <EmptyValue />

  const visible = values.slice(0, maxVisible)
  const remaining = values.length - visible.length

  return (
    <div className="grid gap-0.5 font-mono text-xs text-[var(--napms-color-text-body)]">
      {visible.map((value) => (
        <span key={value}>{value}</span>
      ))}
      {remaining > 0 ? (
        <span className="text-[var(--napms-color-text-secondary)]">+{remaining} more</span>
      ) : null}
    </div>
  )
}
