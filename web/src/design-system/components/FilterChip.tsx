import type { ButtonHTMLAttributes } from "react"

export function FilterChip({
  selected = false,
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { selected?: boolean }) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      className={`h-7 rounded-full border px-3 text-[11px] font-medium transition ${
        selected
          ? "border-[var(--napms-color-primary-border)] bg-[var(--napms-color-primary-subtle)] text-[var(--napms-color-primary-hover)]"
          : "border-transparent bg-[var(--napms-color-surface-muted)] text-[var(--napms-color-text-secondary)] hover:border-[var(--napms-color-border)] hover:bg-[var(--napms-color-surface)]"
      } ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
