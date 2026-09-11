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
      className={`h-7 rounded-full border px-4 text-xs font-semibold transition ${
        selected
          ? "border-[var(--napms-color-primary-border)] bg-[var(--napms-color-primary-subtle)] text-[var(--napms-color-primary-hover)]"
          : "border-[var(--napms-color-border)] bg-[var(--napms-color-surface)] text-[var(--napms-color-text-secondary)] hover:bg-[var(--napms-color-surface-subtle)]"
      } ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
