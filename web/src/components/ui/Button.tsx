import type { ButtonHTMLAttributes } from "react"

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost"
  size?: "sm" | "default"
  loading?: boolean
}

export function Button({
  variant = "primary",
  size = "default",
  loading = false,
  disabled,
  className = "",
  children,
  ...props
}: Props) {
  const variants = {
    primary:
      "border-transparent bg-[var(--napms-color-primary)] text-white hover:bg-[var(--napms-color-primary-hover)] active:bg-[var(--napms-color-primary-active)]",
    secondary:
      "border-[var(--napms-color-border-strong)] bg-[var(--napms-color-surface)] text-[var(--napms-color-text-primary)] hover:bg-[var(--napms-color-surface-subtle)]",
    ghost:
      "border-transparent bg-transparent text-[var(--napms-color-text-secondary)] hover:bg-[var(--napms-color-surface-muted)]",
  }
  const sizes = {
    default: "min-h-[var(--napms-control-height)] px-4 py-2 text-sm",
    sm: "min-h-[var(--napms-control-height-sm)] px-3 py-1.5 text-xs",
  }

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-[var(--napms-control-radius)] border font-semibold transition disabled:cursor-not-allowed disabled:opacity-50 ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? "Working…" : children}
    </button>
  )
}
