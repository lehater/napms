import type {
  InputHTMLAttributes,
  SelectHTMLAttributes,
} from "react"

const controlClass =
  "min-h-[var(--napms-control-height)] w-full rounded-[var(--napms-control-radius)] border border-[var(--napms-color-border-strong)] bg-[var(--napms-color-surface)] px-3 py-2 text-sm text-[var(--napms-color-text-primary)] outline-none transition focus:border-[var(--napms-color-primary)] focus:ring-2 focus:ring-[var(--napms-color-primary-subtle)] disabled:bg-[var(--napms-color-surface-subtle)] disabled:text-[var(--napms-color-text-muted)]"

export function Field({
  label,
  hint,
  children,
  className = "",
}: {
  label: string
  hint?: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <label className={`grid gap-2 text-sm font-medium text-[var(--napms-color-text-body)] ${className}`}>
      <span>{label}</span>
      {children}
      {hint ? (
        <span className="text-xs font-normal text-[var(--napms-color-text-secondary)]">
          {hint}
        </span>
      ) : null}
    </label>
  )
}

export function Input({
  className = "",
  ...props
}: InputHTMLAttributes<HTMLInputElement>) {
  return <input className={`${controlClass} ${className}`} {...props} />
}

export function Select({
  className = "",
  ...props
}: SelectHTMLAttributes<HTMLSelectElement>) {
  return <select className={`${controlClass} ${className}`} {...props} />
}
